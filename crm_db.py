"""
CRM Database Functions and Schema for Lead Management
Import this into app.py to add CRM functionality
"""
import sqlite3
from datetime import datetime

def init_leads_db(db):
    """Initialize the leads table with enhanced CRM fields"""
    # Create enhanced leads table
    db.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            price TEXT,
            source TEXT,
            image_url TEXT,
            
            -- Status & Workflow
            status TEXT DEFAULT 'new',
            
            -- Contact Information
            seller_name TEXT,
            seller_phone TEXT,
            seller_email TEXT,
            
            -- Vehicle Details
            vin TEXT,
            condition_notes TEXT,
            inspection_notes TEXT,
            
            -- Offer Tracking
            my_offer REAL,
            seller_asking REAL,
            counter_offer REAL,
            
            -- Notes & Follow-up
            notes TEXT,
            follow_up_date DATE,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            viewed_at TIMESTAMP,
            contacted_at TIMESTAMP
        )
    ''')
    
    # Migrate existing notes to leads if notes table exists
    try:
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if cursor.fetchone():
            db.execute('''
                INSERT OR IGNORE INTO leads (url, title, price, source, image_url, notes, created_at)
                SELECT url, title, price, source, image_url, note, created_at FROM notes
            ''')
            print("✓ Migrated existing notes to leads table")
    except Exception as e:
        print(f"Note: Migration skipped: {e}")
    
    db.commit()

def get_leads_with_filters(db, status=None, sort_by='created_at', order='DESC'):
    """Get leads with optional filtering and sorting"""
    query = 'SELECT * FROM leads'
    params = []
    
    if status and status != 'all':
        query += ' WHERE status = ?'
        params.append(status)
    
    query += f' ORDER BY {sort_by} {order}'
    
    cur = db.execute(query, params)
    return [dict(row) for row in cur.fetchall()]

def save_lead(db, data):
    """Save or update a lead with all CRM fields"""
    url = data.get('url')
    if not url:
        raise ValueError('URL is required')
    
    # Check if lead exists
    cur = db.execute('SELECT id FROM leads WHERE url = ?', (url,))
    existing = cur.fetchone()
    
    if existing:
        # Update existing lead
        db.execute('''
            UPDATE leads SET
                title = ?, price = ?, source = ?, image_url = ?,
                status = ?, seller_name = ?, seller_phone = ?, seller_email = ?,
                vin = ?, condition_notes = ?, inspection_notes = ?,
                my_offer = ?, seller_asking = ?, counter_offer = ?,
                notes = ?, follow_up_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE url = ?
        ''', (
            data.get('title'), data.get('price'), data.get('source'), data.get('image_url'),
            data.get('status', 'new'), data.get('seller_name'), data.get('seller_phone'), data.get('seller_email'),
            data.get('vin'), data.get('condition_notes'), data.get('inspection_notes'),
            data.get('my_offer'), data.get('seller_asking'), data.get('counter_offer'),
            data.get('notes'), data.get('follow_up_date'),
            url
        ))
    else:
        # Insert new lead
        db.execute('''
            INSERT INTO leads (
                url, title, price, source, image_url, status,
                seller_name, seller_phone, seller_email,
                vin, condition_notes, inspection_notes,
                my_offer, seller_asking, counter_offer,
                notes, follow_up_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url, data.get('title'), data.get('price'), data.get('source'), data.get('image_url'),
            data.get('status', 'new'), data.get('seller_name'), data.get('seller_phone'), data.get('seller_email'),
            data.get('vin'), data.get('condition_notes'), data.get('inspection_notes'),
            data.get('my_offer'), data.get('seller_asking'), data.get('counter_offer'),
            data.get('notes'), data.get('follow_up_date')
        ))
    
    db.commit()

def update_lead_status(db, lead_id, status):
    """Quick status update for a lead"""
    timestamp_field = None
    if status == 'contacted':
        timestamp_field = 'contacted_at'
    elif status == 'viewed':
        timestamp_field = 'viewed_at'
    
    if timestamp_field:
        db.execute(f'''
            UPDATE leads SET status = ?, {timestamp_field} = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, lead_id))
    else:
        db.execute('''
            UPDATE leads SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, lead_id))
    
    db.commit()

def get_leads_stats(db):
    """Get statistics for dashboard"""
    stats = {}
    
    # Count by status
    cur = db.execute('SELECT status, COUNT(*) as count FROM leads GROUP BY status')
    stats['by_status'] = {row['status']: row['count'] for row in cur.fetchall()}
    
    # Total leads
    cur = db.execute('SELECT COUNT(*) as total FROM leads')
    stats['total'] = cur.fetchone()['total']
    
    # Upcoming follow-ups
    cur = db.execute('''
        SELECT COUNT(*) as count FROM leads 
        WHERE follow_up_date IS NOT NULL AND follow_up_date >= DATE('now')
    ''')
    stats['upcoming_follow_ups'] = cur.fetchone()['count']
    
    # Total value of active offers
    cur = db.execute('''
        SELECT SUM(my_offer) as total FROM leads 
        WHERE my_offer IS NOT NULL AND status IN ('negotiating', 'contacted', 'viewed')
    ''')
    result = cur.fetchone()
    stats['total_offers_value'] = result['total'] if result['total'] else 0
    
    return stats
