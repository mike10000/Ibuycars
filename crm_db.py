"""
CRM Database Functions and Schema for Lead Management
Import this into app.py to add CRM functionality
"""
from datetime import datetime
from db_config import is_postgresql, get_placeholder

def init_leads_db(db):
    """Initialize the leads table with enhanced CRM fields"""
    
    # Determine correct syntax based on database type
    if is_postgresql():
        id_type = "SERIAL PRIMARY KEY"
        text_type = "VARCHAR(255)" # Or TEXT, Postgres handles both well
        ignore_conflict = "ON CONFLICT DO NOTHING"
        current_date = "CURRENT_DATE"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        text_type = "TEXT"
        ignore_conflict = "OR IGNORE"
        current_date = "DATE('now')"

    # Create enhanced leads table
    # Note: For Postgres, we use SERIAL for id
    create_query = f'''
        CREATE TABLE IF NOT EXISTS leads (
            id {id_type},
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
    '''
    
    # Execute create table
    if hasattr(db, 'execute'):
        cursor = db.execute(create_query)
    else:
        cursor = db.cursor()
        cursor.execute(create_query)
        db.commit()
    
    # Migrate existing notes to leads if notes table exists (SQLite only feature for now)
    if not is_postgresql():
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
    
    if hasattr(db, 'commit'):
        db.commit()

def get_leads_with_filters(db, status=None, sort_by='created_at', order='DESC'):
    """Get leads with optional filtering and sorting"""
    query = 'SELECT * FROM leads'
    params = []
    
    placeholder = get_placeholder()
    
    if status and status != 'all':
        query += f' WHERE status = {placeholder}'
        params.append(status)
    
    # Validate sort_by to prevent SQL injection
    valid_columns = ['created_at', 'updated_at', 'price', 'status', 'follow_up_date']
    if sort_by not in valid_columns:
        sort_by = 'created_at'
        
    if order.upper() not in ['ASC', 'DESC']:
        order = 'DESC'
    
    query += f' ORDER BY {sort_by} {order}'
    
    if hasattr(db, 'execute'):
        cur = db.execute(query, tuple(params))
        return [dict(row) for row in cur.fetchall()]
    else:
        cur = db.cursor()
        cur.execute(query, tuple(params))
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def save_lead(db, data):
    """Save or update a lead with all CRM fields"""
    url = data.get('url')
    if not url:
        raise ValueError('URL is required')
    
    placeholder = get_placeholder()
    
    # Check if lead exists
    check_query = f'SELECT id FROM leads WHERE url = {placeholder}'
    
    if hasattr(db, 'execute'):
        cur = db.execute(check_query, (url,))
    else:
        cur = db.cursor()
        cur.execute(check_query, (url,))
        
    existing = cur.fetchone()
    
    if existing:
        # Update existing lead
        update_query = f'''
            UPDATE leads SET
                title = {placeholder}, price = {placeholder}, source = {placeholder}, image_url = {placeholder},
                status = {placeholder}, seller_name = {placeholder}, seller_phone = {placeholder}, seller_email = {placeholder},
                vin = {placeholder}, condition_notes = {placeholder}, inspection_notes = {placeholder},
                my_offer = {placeholder}, seller_asking = {placeholder}, counter_offer = {placeholder},
                notes = {placeholder}, follow_up_date = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE url = {placeholder}
        '''
        params = (
            data.get('title'), data.get('price'), data.get('source'), data.get('image_url'),
            data.get('status', 'new'), data.get('seller_name'), data.get('seller_phone'), data.get('seller_email'),
            data.get('vin'), data.get('condition_notes'), data.get('inspection_notes'),
            data.get('my_offer'), data.get('seller_asking'), data.get('counter_offer'),
            data.get('notes'), data.get('follow_up_date'),
            url
        )
        lead_id = existing['id'] if isinstance(existing, dict) else existing[0]
    else:
        # Insert new lead
        if is_postgresql():
            update_query = f'''
                INSERT INTO leads (
                    url, title, price, source, image_url, status,
                    seller_name, seller_phone, seller_email,
                    vin, condition_notes, inspection_notes,
                    my_offer, seller_asking, counter_offer,
                    notes, follow_up_date
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                RETURNING id
            '''
        else:
            update_query = f'''
                INSERT INTO leads (
                    url, title, price, source, image_url, status,
                    seller_name, seller_phone, seller_email,
                    vin, condition_notes, inspection_notes,
                    my_offer, seller_asking, counter_offer,
                    notes, follow_up_date
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            '''
            
        params = (
            url, data.get('title'), data.get('price'), data.get('source'), data.get('image_url'),
            data.get('status', 'new'), data.get('seller_name'), data.get('seller_phone'), data.get('seller_email'),
            data.get('vin'), data.get('condition_notes'), data.get('inspection_notes'),
            data.get('my_offer'), data.get('seller_asking'), data.get('counter_offer'),
            data.get('notes'), data.get('follow_up_date')
        )
        lead_id = None
    
    if hasattr(db, 'execute'):
        cur = db.execute(update_query, params)
    else:
        cur = db.cursor()
        cur.execute(update_query, params)
    
    # Get ID for new insert
    if not existing:
        if is_postgresql():
            lead_id = cur.fetchone()['id']
        else:
            lead_id = cur.lastrowid
            
    if hasattr(db, 'commit'):
        db.commit()
        
    return lead_id

def update_lead_status(db, lead_id, status):
    """Quick status update for a lead"""
    timestamp_field = None
    if status == 'contacted':
        timestamp_field = 'contacted_at'
    elif status == 'viewed':
        timestamp_field = 'viewed_at'
    
    placeholder = get_placeholder()
    
    if timestamp_field:
        query = f'''
            UPDATE leads SET status = {placeholder}, {timestamp_field} = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        '''
        params = (status, lead_id)
    else:
        query = f'''
            UPDATE leads SET status = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        '''
        params = (status, lead_id)
    
    if hasattr(db, 'execute'):
        db.execute(query, params)
    else:
        cur = db.cursor()
        cur.execute(query, params)
    
    if hasattr(db, 'commit'):
        db.commit()

def get_leads_stats(db):
    """Get statistics for dashboard"""
    stats = {}
    
    if is_postgresql():
        date_check = "CURRENT_DATE"
    else:
        date_check = "DATE('now')"
    
    # Helper to execute and return dicts
    def query_db(q, p=None):
        if hasattr(db, 'execute'):
            cur = db.execute(q, p or ())
            return [dict(row) for row in cur.fetchall()]
        else:
            cur = db.cursor()
            cur.execute(q, p or ())
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
            
    # Count by status
    rows = query_db('SELECT status, COUNT(*) as count FROM leads GROUP BY status')
    stats['by_status'] = {row['status']: row['count'] for row in rows}
    
    # Total leads
    rows = query_db('SELECT COUNT(*) as total FROM leads')
    stats['total'] = rows[0]['total']
    
    # Upcoming follow-ups
    rows = query_db(f'''
        SELECT COUNT(*) as count FROM leads 
        WHERE follow_up_date IS NOT NULL AND follow_up_date >= {date_check}
    ''')
    stats['upcoming_follow_ups'] = rows[0]['count']
    
    # Total value of active offers
    rows = query_db('''
        SELECT SUM(my_offer) as total FROM leads 
        WHERE my_offer IS NOT NULL AND status IN ('negotiating', 'contacted', 'viewed')
    ''')
    stats['total_offers_value'] = rows[0]['total'] if rows[0]['total'] else 0
    
    return stats
