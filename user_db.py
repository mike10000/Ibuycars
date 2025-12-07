"""
User Management Database Functions
Handles users, roles, saved searches, and listing assignments
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from db_config import get_db_connection, get_placeholder, adapt_query

def get_connection():
    """Get database connection"""
    conn = get_db_connection('users')
    return conn

def init_user_db():
    """Initialize all user management tables"""
    from db_config import is_postgresql
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Determine the correct syntax based on database type
    if is_postgresql():
        id_type = "SERIAL PRIMARY KEY"
        text_type = "VARCHAR(255)"
        boolean_default = "TRUE"
    else:
        id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
        text_type = "TEXT"
        boolean_default = "1"
    
    # Users table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            email {text_type} NOT NULL UNIQUE,
            name {text_type},
            role {text_type} DEFAULT 'user',
            is_active BOOLEAN DEFAULT {boolean_default},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Saved searches table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS saved_searches (
            id {id_type},
            created_by INTEGER NOT NULL,
            name {text_type} NOT NULL,
            search_params TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Listing assignments table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS listing_assignments (
            id {id_type},
            search_id INTEGER,
            listing_url TEXT NOT NULL,
            listing_data TEXT NOT NULL,
            assigned_to INTEGER,
            assigned_by INTEGER NOT NULL,
            status {text_type} DEFAULT 'pending',
            notes TEXT,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (search_id) REFERENCES saved_searches(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== USER FUNCTIONS ====================

def create_or_update_user(email: str, name: str = None) -> int:
    """Create a new user or update existing user's last login"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    existing = cursor.fetchone()
    
    if existing:
        # Update last login
        cursor.execute('''
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, name = COALESCE(?, name)
            WHERE email = ?
        ''', (name, email))
        user_id = existing['id']
    else:
        # Create new user
        cursor.execute('''
            INSERT INTO users (email, name, last_login)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (email, name))
        user_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users() -> List[Dict]:
    """Get all users"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def update_user_role(user_id: int, role: str) -> bool:
    """Update user role (manager or user)"""
    if role not in ['manager', 'user']:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def deactivate_user(user_id: int) -> bool:
    """Deactivate a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def is_manager(user_id: int) -> bool:
    """Check if user is a manager"""
    user = get_user_by_id(user_id)
    return user and user['role'] == 'manager'

# ==================== SAVED SEARCHES FUNCTIONS ====================

def save_search(user_id: int, name: str, search_params: Dict) -> int:
    """Save a search query"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO saved_searches (created_by, name, search_params)
        VALUES (?, ?, ?)
    ''', (user_id, name, json.dumps(search_params)))
    search_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return search_id

def get_saved_searches(user_id: int) -> List[Dict]:
    """Get all saved searches for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, u.name as created_by_name 
        FROM saved_searches s
        JOIN users u ON s.created_by = u.id
        WHERE s.created_by = ?
        ORDER BY s.created_at DESC
    ''', (user_id,))
    searches = []
    for row in cursor.fetchall():
        search = dict(row)
        search['search_params'] = json.loads(search['search_params'])
        searches.append(search)
    conn.close()
    return searches

def get_search_by_id(search_id: int) -> Optional[Dict]:
    """Get a saved search by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_searches WHERE id = ?', (search_id,))
    search = cursor.fetchone()
    conn.close()
    if search:
        search_dict = dict(search)
        search_dict['search_params'] = json.loads(search_dict['search_params'])
        return search_dict
    return None

def delete_saved_search(search_id: int, user_id: int) -> bool:
    """Delete a saved search (only by creator)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM saved_searches 
        WHERE id = ? AND created_by = ?
    ''', (search_id, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# ==================== ASSIGNMENT FUNCTIONS ====================

def create_assignment(search_id: int, listing_url: str, listing_data: Dict,
                     assigned_to: int, assigned_by: int, notes: str = None) -> int:
    """Create a new listing assignment"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO listing_assignments 
        (search_id, listing_url, listing_data, assigned_to, assigned_by, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (search_id, listing_url, json.dumps(listing_data), assigned_to, assigned_by, notes))
    assignment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return assignment_id

def get_user_assignments(user_id: int, status: str = None) -> List[Dict]:
    """Get assignments for a user, optionally filtered by status"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT a.*, 
               u1.name as assigned_to_name,
               u2.name as assigned_by_name,
               s.name as search_name
        FROM listing_assignments a
        JOIN users u1 ON a.assigned_to = u1.id
        JOIN users u2 ON a.assigned_by = u2.id
        LEFT JOIN saved_searches s ON a.search_id = s.id
        WHERE a.assigned_to = ?
    '''
    
    params = [user_id]
    if status:
        query += ' AND a.status = ?'
        params.append(status)
    
    query += ' ORDER BY a.assigned_at DESC'
    
    cursor.execute(query, params)
    assignments = []
    for row in cursor.fetchall():
        assignment = dict(row)
        assignment['listing_data'] = json.loads(assignment['listing_data'])
        assignments.append(assignment)
    conn.close()
    return assignments

def get_search_assignments(search_id: int) -> List[Dict]:
    """Get all assignments for a saved search"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, 
               u1.name as assigned_to_name,
               u2.name as assigned_by_name
        FROM listing_assignments a
        JOIN users u1 ON a.assigned_to = u1.id
        JOIN users u2 ON a.assigned_by = u2.id
        WHERE a.search_id = ?
        ORDER BY a.assigned_at DESC
    ''', (search_id,))
    assignments = []
    for row in cursor.fetchall():
        assignment = dict(row)
        assignment['listing_data'] = json.loads(assignment['listing_data'])
        assignments.append(assignment)
    conn.close()
    return assignments

def update_assignment_status(assignment_id: int, user_id: int, status: str, notes: str = None) -> bool:
    """Update assignment status (by assigned user)"""
    valid_statuses = ['pending', 'contacted', 'offer_made', 'purchased', 'passed', 'declined']
    if status not in valid_statuses:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query
    if notes:
        cursor.execute('''
            UPDATE listing_assignments 
            SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND assigned_to = ?
        ''', (status, notes, assignment_id, user_id))
    else:
        cursor.execute('''
            UPDATE listing_assignments 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND assigned_to = ?
        ''', (status, assignment_id, user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def reassign_listing(assignment_id: int, new_assignee_id: int, manager_id: int) -> bool:
    """Reassign a listing to a different user (manager only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE listing_assignments 
        SET assigned_to = ?, 
            assigned_by = ?,
            status = 'pending',
            assigned_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_assignee_id, manager_id, assignment_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def get_assignment_by_id(assignment_id: int) -> Optional[Dict]:
    """Get a single assignment by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, 
               u1.name as assigned_to_name,
               u2.name as assigned_by_name,
               s.name as search_name
        FROM listing_assignments a
        JOIN users u1 ON a.assigned_to = u1.id
        JOIN users u2 ON a.assigned_by = u2.id
        LEFT JOIN saved_searches s ON a.search_id = s.id
        WHERE a.id = ?
    ''', (assignment_id,))
    assignment = cursor.fetchone()
    conn.close()
    if assignment:
        assignment_dict = dict(assignment)
        assignment_dict['listing_data'] = json.loads(assignment_dict['listing_data'])
        return assignment_dict
    return None

# Initialize database on import
if __name__ == '__main__':
    init_user_db()
    print("User management database initialized!")
