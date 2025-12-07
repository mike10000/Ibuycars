# PostgreSQL Setup Guide for iBuyCars

This guide will help you set up PostgreSQL for the iBuyCars application on Windows.

## Prerequisites

✅ PostgreSQL 17 installed
✅ Python package `psycopg2-binary` installed

## Step 1: Create Database and User

You have two options to set up the database:

### Option A: Using Command Line (psql)

1. **Open Command Prompt or PowerShell as Administrator**

2. **Connect to PostgreSQL**:
   ```powershell
   psql -U postgres
   ```
   
   You'll be prompted for the password you set during PostgreSQL installation.

3. **Run the setup commands**:
   ```sql
   -- Create database
   CREATE DATABASE ibuycars_db;
   
   -- Create user
   CREATE USER ibuycars_user WITH PASSWORD 'ibuycars_secure_2024';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE ibuycars_db TO ibuycars_user;
   
   -- Connect to the database
   \c ibuycars_db
   
   -- Grant schema privileges (PostgreSQL 15+)
   GRANT ALL ON SCHEMA public TO ibuycars_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ibuycars_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ibuycars_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ibuycars_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ibuycars_user;
   
   -- Exit psql
   \q
   ```

### Option B: Using SQL File

1. **Open Command Prompt or PowerShell**

2. **Navigate to the project directory**:
   ```powershell
   cd C:\Users\mtint\Desktop\Ibuycars
   ```

3. **Run the setup script**:
   ```powershell
   psql -U postgres -f setup_postgres.sql
   ```

4. **Then connect and grant additional privileges**:
   ```powershell
   psql -U postgres -d ibuycars_db
   ```
   
   Then run:
   ```sql
   GRANT ALL ON SCHEMA public TO ibuycars_user;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ibuycars_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ibuycars_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ibuycars_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ibuycars_user;
   \q
   ```

## Step 2: Configure Environment Variables

1. **Copy the example environment file**:
   ```powershell
   copy .env.example .env
   ```

2. **Edit the `.env` file** with your favorite text editor and update these values:

   ```env
   # Set database type to postgresql
   DB_TYPE=postgresql
   
   # PostgreSQL connection details
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=ibuycars_db
   POSTGRES_USER=ibuycars_user
   POSTGRES_PASSWORD=ibuycars_secure_2024
   
   # Keep your existing Google OAuth credentials
   GOOGLE_CLIENT_ID=your-actual-client-id
   GOOGLE_CLIENT_SECRET=your-actual-secret
   
   # Other settings
   SECRET_KEY=your-secret-key
   ALLOWED_DOMAINS=ibuycars.com
   MANAGER_EMAILS=mtintner@ibuycars.com
   ```

## Step 3: Initialize Database Schema

Run the initialization script to create all tables:

```powershell
python init_postgres.py
```

You should see output like:
```
============================================================
PostgreSQL Database Initialization
============================================================

Creating database schema...
✓ Created users table
✓ Created saved_searches table
✓ Created listing_assignments table
✓ Created indexes
✓ Created initial manager user (if not exists)

✓ PostgreSQL database schema initialized successfully!

Database is ready to use!
You can now start the application with: python app.py
```

## Step 4: Test Database Connection

Test that everything is working:

```powershell
python db_config.py
```

Expected output:
```
Database Type: postgresql
✓ Successfully connected to postgresql database
PostgreSQL version: PostgreSQL 17.x ...
```

## Step 5: Start the Application

```powershell
python app.py
```

The application should start without database errors!

## Troubleshooting

### Error: "psql is not recognized"

PostgreSQL's bin directory is not in your PATH. Either:
- Add `C:\Program Files\PostgreSQL\17\bin` to your system PATH
- Or use the full path: `"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres`

### Error: "password authentication failed"

Make sure you're using the correct password you set during PostgreSQL installation.

### Error: "database does not exist"

Run the database creation commands from Step 1 again.

### Error: "connection refused"

PostgreSQL service might not be running. Start it:
```powershell
net start postgresql-x64-17
```

Or check Services (services.msc) and start "postgresql-x64-17".

### Error: "permission denied for schema public"

Run the GRANT commands from Step 1 again, specifically the schema privileges.

## Switching Back to SQLite

If you need to switch back to SQLite for any reason:

1. Edit `.env` and change:
   ```env
   DB_TYPE=sqlite
   ```

2. Restart the application

Your original SQLite databases (`notes.db` and `users.db`) remain untouched!

## Verifying PostgreSQL Setup

### Using psql Command Line

```powershell
# Connect to the database
psql -U ibuycars_user -d ibuycars_db

# List all tables
\dt

# View users table
SELECT * FROM users;

# Exit
\q
```

### Using pgAdmin 4 (Optional)

If you want to install pgAdmin 4 later:
1. Download from: https://www.pgadmin.org/download/
2. Install and launch
3. Add server:
   - Host: localhost
   - Port: 5432
   - Database: ibuycars_db
   - Username: ibuycars_user
   - Password: ibuycars_secure_2024

## Next Steps

Once PostgreSQL is set up and working:
1. Test user authentication
2. Test search functionality
3. Verify data is being saved to PostgreSQL
4. This setup mimics what you'll use on Google Cloud Run with Cloud SQL!

## Cloud Run Deployment Notes

When deploying to Google Cloud Run:
1. Create a Cloud SQL PostgreSQL instance
2. Update environment variables in Cloud Run to point to Cloud SQL
3. Use Cloud SQL Proxy or private IP for connection
4. The same code will work - just change the `.env` configuration!
