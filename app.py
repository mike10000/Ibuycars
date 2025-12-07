"""
Flask backend API for the car search tool with Google OAuth
"""
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for
from flask_cors import CORS
from flask_login import login_required, current_user, logout_user
from search_coordinator import SearchCoordinator
import traceback
import os
from datetime import datetime
from functools import wraps
from config import config
import auth

import user_db
import crm_db
from decorators import manager_required
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config.from_object(config)
CORS(app)  # Enable CORS for frontend

# Fix for Cloud Run (HTTPS)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize OAuth
auth.init_oauth(app)

# Register CRM Routes
import crm_routes
crm_routes.register_crm_routes(app)

# Note: @login_required decorator is now imported from flask_login

def get_db():
    """Get database connection (stored in Flask g object)"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = get_db_connection('main')
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection at end of request"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database on startup"""
    with app.app_context():
        # Initialize user database tables
        user_db.init_user_db()

# Initialize DB on start
# init_db()  # Temporarily disabled for debugging

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
    flow = auth.create_oauth_flow(redirect_uri=url_for('oauth2callback', _external=True))
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store state in session for verification
    session['state'] = state
    
    return redirect(authorization_url)

 
@app.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth2 callback from Google"""
    # Verify state
    if request.args.get('state') != session.get('state'):
        return 'State mismatch error', 400
    
    # Exchange authorization code for access token
    flow = auth.create_oauth_flow(redirect_uri=url_for('oauth2callback', _external=True))
    flow.fetch_token(authorization_response=request.url)
    
    # Get credentials
    credentials = flow.credentials
    
    # Get user info from Google
    import requests
    userinfo_endpoint = auth.get_google_provider_cfg()["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    
    if userinfo_response.status_code != 200:
        return "Failed to get user info from Google", 400
    
    userinfo = userinfo_response.json()
    
    # Validate email domain
    email = userinfo.get("email")
    if not auth.validate_domain(email):
        return render_template('unauthorized.html', email=email, allowed_domains=config.ALLOWED_DOMAINS)
    
    # Create or update user in database
    import user_db
    db_user_id = user_db.create_or_update_user(email, userinfo.get("name"))
    
    # Get user from database to check role
    db_user = user_db.get_user_by_id(db_user_id)
    
    # Check if user should be a manager (from config or existing role)
    user_role = db_user['role']
    if email in config.MANAGER_EMAILS and user_role != 'manager':
        # Promote to manager if in config
        user_db.update_user_role(db_user_id, 'manager')
        user_role = 'manager'
    
    # Create user and login
    user = auth.create_user_from_google_info(userinfo, db_id=db_user_id, role=user_role)
    
    # Store user in session
    session['user'] = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'picture': user.picture,
        'db_id': user.db_id,
        'role': user.role
    }
    
    from flask_login import login_user
    login_user(user)
    
    return redirect(url_for('index'))


@app.route('/login/test')
def login_test():
    """Test login for local development - automatically logs in as test manager"""
    # Get the test user from database
    test_user = user_db.get_user_by_email('mtintner@ibuycars.com')
    
    if not test_user:
        return "Test user not found. Run seed_users.py first.", 404
    
    # Create user object with dummy Google info
    userinfo = {
        'sub': 'test-google-id-123',
        'email': test_user['email'],
        'name': test_user['name'] or 'Test Manager',
        'picture': 'https://via.placeholder.com/150'
    }
    
    user = auth.create_user_from_google_info(
        userinfo, 
        db_id=test_user['id'], 
        role=test_user['role']
    )
    
    # Store user in session
    session['user'] = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'picture': user.picture,
        'db_id': user.db_id,
        'role': user.role
    }
    
    from flask_login import login_user
    login_user(user)
    
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Serve the main page"""
    print("INDEX ROUTE CALLED")
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint for car searches"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'success': False
            }), 400
        
        # Extract search parameters
        make_input = data.get('make', '').strip() if data.get('make') else ''
        model = data.get('model', '').strip() if data.get('model') else None
        year_min = data.get('year_min')
        year_max = data.get('year_max')
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        location = data.get('location', '').strip() if data.get('location') else None
        max_results = data.get('max_results', 20)
        enable_facebook = data.get('enable_facebook', False)
        enable_craigslist = data.get('enable_craigslist', True)
        enable_cars_com = data.get('enable_cars_com', True)
        enable_offerup = data.get('enable_offerup', True)
        enable_autotrader = data.get('enable_autotrader', False)
        private_sellers_only = data.get('private_sellers_only', False)
        
        # Parse makes - can be comma-separated string or list
        if isinstance(make_input, list):
            makes = [m.strip() for m in make_input if m.strip()]
        else:
            makes = [m.strip() for m in make_input.split(',') if m.strip()]
        
        # Validate required fields
        if not location:
            return jsonify({
                'error': 'Location is required',
                'success': False
            }), 400
        
        # Convert numeric fields safely
        def safe_int(value):
            if not value or value == '':
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        year_min = safe_int(year_min)
        year_max = safe_int(year_max)
        price_min = safe_int(price_min)
        price_max = safe_int(price_max)
        max_results = safe_int(max_results) or 20
        
        # Initialize coordinator
        coordinator = SearchCoordinator()
        
        # Search all sites
        results = coordinator.search_all(
            makes=makes,
            model=model,
            year_min=year_min,
            year_max=year_max,
            price_min=price_min,
            price_max=price_max,
            location=location,
            max_results=max_results,
            enable_facebook=enable_facebook,
            enable_craigslist=enable_craigslist,
            enable_cars_com=enable_cars_com,
            enable_offerup=enable_offerup,
            enable_autotrader=enable_autotrader,
            private_sellers_only=private_sellers_only
        )
        
        # Get all listings
        all_listings = coordinator.get_all_listings(results)
        
        # Apply additional filtering
        all_listings = coordinator.filter_listings(
            all_listings,
            year_min=year_min,
            year_max=year_max,
            price_min=price_min,
            price_max=price_max
        )
        
        # Convert to dictionaries
        listings_data = [listing.to_dict() for listing in all_listings]
        
        # Create summary
        summary = {source: len(listings) for source, listings in results.items()}
        
        return jsonify({
            'success': True,
            'summary': summary,
            'total': len(listings_data),
            'listings': listings_data
        })
        
    except ValueError as e:
        print(f"ValueError in search API: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Invalid input: {str(e)}',
            'success': False
        }), 400
    except Exception as e:
        print(f"Error in search API: {e}")
        traceback.print_exc()
        import sys
        error_type = type(e).__name__
        error_msg = str(e)
        return jsonify({
            'error': f'{error_type}: {error_msg}',
            'success': False,
            'traceback': traceback.format_exc() if app.debug else None
        }), 500


# ==================== USER MANAGEMENT ROUTES ====================

@app.route('/api/users', methods=['GET'])
@login_required
@manager_required
def get_users():
    """Get all users (manager only)"""
    users = user_db.get_all_users()
    return jsonify(users)

@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@login_required
@manager_required
def update_user_role_route(user_id):
    """Update user role (manager only)"""
    data = request.get_json()
    role = data.get('role')
    
    if role not in ['manager', 'user']:
        return jsonify({'error': 'Invalid role'}), 400
    
    success = user_db.update_user_role(user_id, role)
    if success:
        return jsonify({'message': 'Role updated successfully'})
    return jsonify({'error': 'Failed to update role'}), 400

@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT'])
@login_required
@manager_required
def deactivate_user_route(user_id):
    """Deactivate a user (manager only)"""
    success = user_db.deactivate_user(user_id)
    if success:
        return jsonify({'message': 'User deactivated successfully'})
    return jsonify({'error': 'Failed to deactivate user'}), 400

# ==================== SAVED SEARCHES ROUTES ====================

@app.route('/api/searches', methods=['GET'])
@login_required
def get_searches():
    """Get all saved searches for current user"""
    searches = user_db.get_saved_searches(current_user.db_id)
    return jsonify(searches)

@app.route('/api/searches', methods=['POST'])
@login_required
@manager_required
def save_search_route():
    """Save a search query (manager only)"""
    data = request.get_json()
    name = data.get('name')
    search_params = data.get('search_params')
    
    if not name or not search_params:
        return jsonify({'error': 'Name and search_params required'}), 400
    
    search_id = user_db.save_search(current_user.db_id, name, search_params)
    return jsonify({'id': search_id, 'message': 'Search saved successfully'})

@app.route('/api/searches/<int:search_id>', methods=['DELETE'])
@login_required
@manager_required
def delete_search_route(search_id):
    """Delete a saved search (manager only)"""
    success = user_db.delete_saved_search(search_id, current_user.db_id)
    if success:
        return jsonify({'message': 'Search deleted successfully'})
    return jsonify({'error': 'Failed to delete search'}), 400

@app.route('/api/searches/<int:search_id>/results', methods=['POST'])
@login_required
@manager_required
def rerun_search(search_id):
    """Re-run a saved search (manager only)"""
    search = user_db.get_search_by_id(search_id)
    
    if not search:
        return jsonify({'error': 'Search not found'}), 404
    
    # Use the search params to run the search
    search_params = search['search_params']
    coordinator = SearchCoordinator()
    
    try:
        results = coordinator.search(
            makes=search_params.get('makes', []),
            model=search_params.get('model'),
            year_min=search_params.get('year_min'),
            year_max=search_params.get('year_max'),
            price_min=search_params.get('price_min'),
            price_max=search_params.get('price_max'),
            location=search_params.get('location'),
            max_results=search_params.get('max_results', 20),
            enable_craigslist=search_params.get('enable_craigslist', True),
            enable_cars_com=search_params.get('enable_cars_com', True),
            enable_offerup=search_params.get('enable_offerup', False),
            enable_autotrader=search_params.get('enable_autotrader', False),
            enable_facebook=search_params.get('enable_facebook', False),
            private_sellers_only=search_params.get('private_sellers_only', False)
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ASSIGNMENT ROUTES ====================

@app.route('/api/assignments', methods=['GET'])
@login_required
def get_assignments():
    """Get assignments for current user"""
    status = request.args.get('status')  # Optional filter
    assignments = user_db.get_user_assignments(current_user.db_id, status)
    return jsonify(assignments)

@app.route('/api/assignments', methods=['POST'])
@login_required
@manager_required
def create_assignment_route():
    """Create a new assignment (manager only)"""
    data = request.get_json()
    
    search_id = data.get('search_id')
    listing_url = data.get('listing_url')
    listing_data = data.get('listing_data')
    assigned_to = data.get('assigned_to')
    notes = data.get('notes')
    
    if not all([listing_url, listing_data, assigned_to]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    assignment_id = user_db.create_assignment(
        search_id, listing_url, listing_data, assigned_to, current_user.db_id, notes
    )
    return jsonify({'id': assignment_id, 'message': 'Assignment created successfully'})

@app.route('/api/assignments/<int:assignment_id>/status', methods=['PUT'])
@login_required
def update_assignment_status_route(assignment_id):
    """Update assignment status"""
    data = request.get_json()
    status = data.get('status')
    notes = data.get('notes')
    
    if not status:
        return jsonify({'error': 'Status required'}), 400
    
    success = user_db.update_assignment_status(assignment_id, current_user.db_id, status, notes)
    if success:
        return jsonify({'message': 'Status updated successfully'})
    return jsonify({'error': 'Failed to update status'}), 400

@app.route('/api/assignments/<int:assignment_id>/reassign', methods=['PUT'])
@login_required
@manager_required
def reassign_assignment(assignment_id):
    """Reassign a listing to a different user (manager only)"""
    data = request.get_json()
    new_assignee_id = data.get('assigned_to')
    
    if not new_assignee_id:
        return jsonify({'error': 'assigned_to required'}), 400
    
    success = user_db.reassign_listing(assignment_id, new_assignee_id, current_user.db_id)
    if success:
        return jsonify({'message': 'Assignment reassigned successfully'})
    return jsonify({'error': 'Failed to reassign'}), 400

@app.route('/api/assignments/search/<int:search_id>', methods=['GET'])
@login_required
@manager_required
def get_search_assignments_route(search_id):
    """Get all assignments for a search (manager only)"""
    assignments = user_db.get_search_assignments(search_id)
    return jsonify(assignments)

# ==================== FRONTEND ROUTES ====================

@app.route('/users')
@login_required
@manager_required
def users_page():
    """User management page (manager only)"""
    return render_template('users.html')

@app.route('/searches')
@login_required
@manager_required
def searches_page():
    """Saved searches page (manager only)"""
    return render_template('saved_searches.html')

@app.route('/my-assignments')
@login_required
def assignments_page():
    """User's assignments page"""
    return render_template('my_assignments.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """CRM Dashboard"""
    # Get stats from CRM DB
    db = get_db()
    stats = crm_db.get_leads_stats(db)
    return render_template('dashboard.html', stats=stats)





if __name__ == '__main__':
    # Allow OAuth over HTTP for local testing
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, host='0.0.0.0', port=5000)

