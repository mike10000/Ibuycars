
import sqlite3
import os

DATABASE = 'notes.db'

def check_db():
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found.")
        return

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")

    if 'leads' in tables:
        print("\nChecking 'leads' table schema:")
        cursor.execute("PRAGMA table_info(leads)")
        columns = [row['name'] for row in cursor.fetchall()]
        print(f"Columns: {columns}")
        if 'status' not in columns:
            print("CRITICAL ERROR: 'status' column missing from leads table!")
        else:
            print("Verified: 'status' column exists.")

        print("\nChecking 'leads' data count:")
        cursor.execute("SELECT COUNT(*) as count FROM leads")
        print(f"Total leads: {cursor.fetchone()['count']}")
        
        print("\nSample lead:")
        cursor.execute("SELECT * FROM leads LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(dict(row))
    else:
        print("\nERROR: 'leads' table does not exist!")

    conn.close()

if __name__ == "__main__":
    check_db()
