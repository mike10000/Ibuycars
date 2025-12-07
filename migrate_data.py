import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite Configuration
SQLITE_DB = 'notes.db'

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ibuycars_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'ibuycars_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'water')

def migrate_data():
    print("Starting migration from SQLite to PostgreSQL...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"SQLite database {SQLITE_DB} not found. Skipping migration.")
        return

    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        pg_cursor = pg_conn.cursor()
        
        # Migrate Leads/Notes
        print("Migrating leads...")
        
        # Check if 'leads' table exists in SQLite, otherwise check 'notes'
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
        if sqlite_cursor.fetchone():
            source_table = 'leads'
            print("Found 'leads' table in SQLite.")
        else:
            source_table = 'notes'
            print("Found 'notes' table in SQLite (legacy).")
            
        sqlite_cursor.execute(f"SELECT * FROM {source_table}")
        rows = sqlite_cursor.fetchall()
        
        if rows:
            # Prepare data for insertion
            # We need to map columns. 
            # If source is 'notes', columns are likely: id, url, title, price, source, image_url, note, created_at
            # If source is 'leads', it matches the new schema more closely.
            
            columns = [desc[0] for desc in sqlite_cursor.description]
            
            for row in rows:
                data = dict(row)
                
                # Map fields
                url = data.get('url')
                title = data.get('title')
                price = data.get('price')
                source = data.get('source')
                image_url = data.get('image_url')
                
                # Handle 'note' vs 'notes'
                notes = data.get('notes') or data.get('note')
                
                created_at = data.get('created_at')
                
                # Insert into Postgres
                # Using ON CONFLICT DO NOTHING to avoid duplicates if run multiple times
                query = """
                    INSERT INTO leads (url, title, price, source, image_url, notes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        notes = EXCLUDED.notes,
                        updated_at = CURRENT_TIMESTAMP
                """
                pg_cursor.execute(query, (url, title, price, source, image_url, notes, created_at))
                
            print(f"✓ Migrated {len(rows)} leads/notes.")
        else:
            print("No leads/notes found to migrate.")
            
        pg_conn.commit()
        
        sqlite_conn.close()
        pg_conn.close()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_data()
