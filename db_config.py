"""
Database Configuration Module
Supports both SQLite and PostgreSQL based on environment variables
"""
import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database type from environment
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()

# PostgreSQL configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'ibuycars_db'),
    'user': os.getenv('POSTGRES_USER', 'ibuycars_user'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
}

# SQLite configuration
SQLITE_DB = 'notes.db'
SQLITE_USER_DB = 'users.db'


def get_db_connection(db_name='main'):
    """
    Get a database connection based on DB_TYPE environment variable
    
    Args:
        db_name: For SQLite, specify 'main' or 'users'. For PostgreSQL, this is ignored.
    
    Returns:
        Database connection object
    """
    if DB_TYPE == 'postgresql':
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(
                host=POSTGRES_CONFIG['host'],
                port=POSTGRES_CONFIG['port'],
                database=POSTGRES_CONFIG['database'],
                user=POSTGRES_CONFIG['user'],
                password=POSTGRES_CONFIG['password'],
                cursor_factory=RealDictCursor
            )
            return conn
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL support. "
                "Install it with: pip install psycopg2-binary"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")
    
    else:  # SQLite
        db_file = SQLITE_USER_DB if db_name == 'users' else SQLITE_DB
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn


@contextmanager
def get_db_cursor(db_name='main'):
    """
    Context manager for database operations
    Automatically handles connection and cursor cleanup
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def execute_query(query, params=None, db_name='main', fetch_one=False, fetch_all=False):
    """
    Execute a database query with automatic connection handling
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dict)
        db_name: Database name ('main' or 'users' for SQLite)
        fetch_one: If True, return single row
        fetch_all: If True, return all rows
    
    Returns:
        Query results or None
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        else:
            conn.commit()
            last_id = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
            conn.close()
            return last_id
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


def get_placeholder():
    """
    Get the correct parameter placeholder for the current database type
    
    Returns:
        '?' for SQLite, '%s' for PostgreSQL
    """
    return '%s' if DB_TYPE == 'postgresql' else '?'


def adapt_query(query):
    """
    Adapt a query from SQLite syntax to PostgreSQL if needed
    
    Args:
        query: SQL query string with '?' placeholders
    
    Returns:
        Adapted query string
    """
    if DB_TYPE == 'postgresql':
        # Replace ? with %s for PostgreSQL
        count = query.count('?')
        for i in range(count):
            query = query.replace('?', '%s', 1)
        
        # Replace AUTOINCREMENT with SERIAL
        query = query.replace('AUTOINCREMENT', 'SERIAL')
        
        # Replace CURRENT_TIMESTAMP if needed
        # PostgreSQL uses CURRENT_TIMESTAMP, same as SQLite, so no change needed
        
    return query


def is_postgresql():
    """Check if using PostgreSQL"""
    return DB_TYPE == 'postgresql'


def is_sqlite():
    """Check if using SQLite"""
    return DB_TYPE == 'sqlite'


if __name__ == '__main__':
    # Test database connection
    print(f"Database Type: {DB_TYPE}")
    
    try:
        conn = get_db_connection()
        print(f"✓ Successfully connected to {DB_TYPE} database")
        
        # Test query
        cursor = conn.cursor()
        if DB_TYPE == 'postgresql':
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"PostgreSQL version: {version}")
        else:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"SQLite version: {version[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
