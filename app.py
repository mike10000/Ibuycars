"""
Flask backend API for the car search tool
"""
from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
from search_coordinator import SearchCoordinator
import traceback
import sqlite3
import os
from datetime import datetime

DATABASE = 'notes.db'

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

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
        db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                price TEXT,
                source TEXT,
                image_url TEXT,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Initialize DB on start
init_db()

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


@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all saved notes"""
    try:
        db = get_db()
        cur = db.execute('SELECT * FROM notes ORDER BY created_at DESC')
        notes = [dict(row) for row in cur.fetchall()]
        return jsonify({'success': True, 'notes': notes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
def save_note():
    """Save or update a note"""
    try:
        data = request.get_json()
        url = data.get('url')
        note_text = data.get('note')
        
        if not url or not note_text:
            return jsonify({'success': False, 'error': 'URL and note text are required'}), 400
            
        db = get_db()
        
        # Check if note exists for this URL
        cur = db.execute('SELECT id FROM notes WHERE url = ?', (url,))
        existing = cur.fetchone()
        
        if existing:
            db.execute('UPDATE notes SET note = ?, created_at = CURRENT_TIMESTAMP WHERE url = ?',
                      (note_text, url))
        else:
            db.execute('''
                INSERT INTO notes (url, title, price, source, image_url, note)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                url,
                data.get('title', 'Unknown Car'),
                data.get('price', 'N/A'),
                data.get('source', 'Unknown'),
                data.get('image_url', ''),
                note_text
            ))
            
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        db = get_db()
        db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

