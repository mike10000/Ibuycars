"""
Seed Database with Dummy Users
"""
import sqlite3
import user_db
from datetime import datetime

def seed_users():
    print("Seeding users...")
    user_db.init_user_db()
    
    # Create Manager
    manager_email = "mtintner@ibuycars.com"
    manager_id = user_db.create_or_update_user(manager_email, "Manager Mike")
    user_db.update_user_role(manager_id, "manager")
    
    # Update picture (hacky direct SQL since create_or_update doesn't support it yet)
    conn = user_db.get_connection()
    conn.execute("UPDATE users SET role='manager' WHERE id=?", (manager_id,))
    conn.commit()
    conn.close()
    
    print(f"Created Manager: {manager_email} (ID: {manager_id})")
    
    # Create Regular User
    user_email = "user@ibuycars.com"
    user_id = user_db.create_or_update_user(user_email, "User John")
    
    print(f"Created User: {user_email} (ID: {user_id})")
    
    print("Done!")

if __name__ == "__main__":
    seed_users()
