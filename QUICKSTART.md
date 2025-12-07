# Quick Start Guide - PostgreSQL Setup

## What We've Done So Far

✅ Installed PostgreSQL 17
✅ Installed Python package `psycopg2-binary`
✅ Created database configuration module (`db_config.py`)
✅ Updated application code to support PostgreSQL
✅ Created setup scripts and documentation

## The Easy Way (Recommended)

We've created an automated script that handles everything for you!

1. **Run the Setup Script**
   Double-click `setup_postgres.bat` or run in terminal:
   ```powershell
   .\setup_postgres.bat
   ```

   This script will:
   - Find your PostgreSQL installation automatically
   - Create the database and user (you'll just need to type your password)
   - Create the `.env` file
   - Initialize the database schema
   - Test the connection

2. **That's it!**
   Once the script finishes, your application is ready to run.

## The Manual Way (If script fails)

### Step 1: Create PostgreSQL Database

Run this command (using full path if needed):

```powershell
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -f setup_postgres.sql
```

### Step 4: Test It!

```powershell
python app.py
```

## Files Created

- `db_config.py` - Database abstraction layer
- `init_postgres.py` - Database schema setup
- `setup_postgres.sql` - SQL setup script
- `setup_postgres.bat` - Automated setup script
- `POSTGRESQL_SETUP.md` - Detailed documentation
- `QUICKSTART.md` - This file

## Need Help?

See `POSTGRESQL_SETUP.md` for detailed instructions and troubleshooting.
