import psycopg2
import sys

passwords = ["water", "Water", "admin", "password", "postgres"]

print("Testing connection to PostgreSQL...")

for pwd in passwords:
    try:
        print(f"Trying password: '{pwd}'")
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password=pwd,
            port="5432"
        )
        print(f"✓ Success! Password is: '{pwd}'")
        conn.close()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Failed: {e}")

print("Could not connect with any common passwords.")
