"""
Initialize PostgreSQL Database Schema
Creates all required tables for the iBuyCars application
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_config import get_db_connection, is_postgresql

def init_postgres_schema():
    """Initialize PostgreSQL database schema"""
    
    if not is_postgresql():
        print("Error: DB_TYPE must be set to 'postgresql' in .env file")
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Creating database schema...")
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        print("✓ Created users table")
        
        # Saved searches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_searches (
                id SERIAL PRIMARY KEY,
                created_by INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                search_params TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        print("✓ Created saved_searches table")
        
        # Listing assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listing_assignments (
                id SERIAL PRIMARY KEY,
                search_id INTEGER,
                listing_url TEXT NOT NULL,
                listing_data TEXT NOT NULL,
                assigned_to INTEGER,
                assigned_by INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                notes TEXT,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (search_id) REFERENCES saved_searches(id),
                FOREIGN KEY (assigned_to) REFERENCES users(id),
                FOREIGN KEY (assigned_by) REFERENCES users(id)
            )
        ''')
        print("✓ Created listing_assignments table")

        # CRM Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                price TEXT,
                source TEXT,
                image_url TEXT,
                
                -- Status & Workflow
                status VARCHAR(50) DEFAULT 'new',
                
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
        print("✓ Created leads table")
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_saved_searches_created_by ON saved_searches(created_by)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_assignments_assigned_to ON listing_assignments(assigned_to)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_assignments_search_id ON listing_assignments(search_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_leads_url ON leads(url)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)
        ''')
        
        print("✓ Created indexes")
        
        # Create initial manager user if it doesn't exist
        cursor.execute('''
            INSERT INTO users (email, name, role, last_login)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (email) DO NOTHING
        ''', ('mtintner@ibuycars.com', 'Mike Tintner', 'manager'))
        
        print("✓ Created initial manager user (if not exists)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ PostgreSQL database schema initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    print()
    
    success = init_postgres_schema()
    
    if success:
        print("\nDatabase is ready to use!")
        print("You can now start the application with: python app.py")
    else:
        print("\nDatabase initialization failed.")
        print("Please check your .env configuration and PostgreSQL connection.")
        sys.exit(1)
