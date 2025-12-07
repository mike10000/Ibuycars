content = """DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ibuycars_db
POSTGRES_USER=ibuycars_user
POSTGRES_PASSWORD=water
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your_random_secret_key_here
ALLOWED_DOMAINS=ibuycars.com
MANAGER_EMAILS=mtintner@ibuycars.com,anothermanager@ibuycars.com
FLASK_ENV=development
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ .env file created successfully")
