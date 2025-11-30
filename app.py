"""
Flask backend API for the car search tool with Google OAuth
"""
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for
from flask_cors import CORS
from flask_login import login_required, current_user, logout_user
from search_coordinator import SearchCoordinator
import traceback
import sqlite3
import os
from datetime import datetime
from functools import wraps
from config import config
import auth

DATABASE = 'notes.db'

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config.from_object(config)
CORS(app)  # Enable CORS for frontend

# Initialize OAuth
auth.init_oauth(app)

# Note: @login_required decorator is now imported from flask_login

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Initialize DB tables if needed
        pass

# Initialize DB on start
init_db()

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
    
    # Create user and login
    user = auth.create_user_from_google_info(userinfo)
    
    # Store user in session
    session['user'] = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'picture': user.picture
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




if __name__ == '__main__':
    # Allow OAuth over HTTP for local testing
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, host='0.0.0.0', port=5000)

