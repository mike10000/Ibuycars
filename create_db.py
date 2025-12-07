import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def create_database():
    # Connect to default 'postgres' database
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="Water",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'ibuycars_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'ibuycars_db'...")
            cursor.execute("CREATE DATABASE ibuycars_db")
            print("✓ Database created")
        else:
            print("✓ Database 'ibuycars_db' already exists")
            
        # Create user if not exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'ibuycars_user'")
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print("Creating user 'ibuycars_user'...")
            cursor.execute("CREATE USER ibuycars_user WITH PASSWORD 'water'")
            print("✓ User created")
        else:
            print("✓ User 'ibuycars_user' already exists")
            # Update password to ensure it matches
            cursor.execute("ALTER USER ibuycars_user WITH PASSWORD 'water'")
            print("✓ User password updated")
            
        # Grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE ibuycars_db TO ibuycars_user")
        
        # We need to connect to the specific database to grant schema privileges
        cursor.close()
        conn.close()
        
        # Connect to ibuycars_db
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="Water",
            port="5432",
            database="ibuycars_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("GRANT ALL ON SCHEMA public TO ibuycars_user")
        print("✓ Schema privileges granted")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_database()
