@echo off
REM Quick PostgreSQL Setup Script for iBuyCars
echo ============================================================
echo PostgreSQL Setup for iBuyCars
echo ============================================================
echo.

REM Find PostgreSQL executable
set "PSQL_CMD=psql"
if exist "C:\Program Files\PostgreSQL\17\bin\psql.exe" (
    set "PSQL_CMD="C:\Program Files\PostgreSQL\17\bin\psql.exe""
) else if exist "C:\Program Files\PostgreSQL\17\pgAdmin 4\runtime\psql.exe" (
    set "PSQL_CMD="C:\Program Files\PostgreSQL\17\pgAdmin 4\runtime\psql.exe""
) else if exist "C:\Program Files\PostgreSQL\16\bin\psql.exe" (
    set "PSQL_CMD="C:\Program Files\PostgreSQL\16\bin\psql.exe""
) else if exist "C:\Program Files\PostgreSQL\15\bin\psql.exe" (
    set "PSQL_CMD="C:\Program Files\PostgreSQL\15\bin\psql.exe""
)

echo [INFO] Using psql command: %PSQL_CMD%

REM Check if .env exists
if exist .env (
    echo [INFO] .env file already exists
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto skip_env
)

REM Create .env from example
echo [1/4] Creating .env file...
copy .env.example .env >nul
echo       Created .env file from template
echo       Please edit .env and update your credentials!
echo.

:skip_env

REM Create Database and User
echo.
echo [1.5/4] Creating Database and User...
echo Please enter your PostgreSQL superuser password when prompted.
echo (This is the password you set during installation)
echo.

%PSQL_CMD% -U postgres -f setup_postgres.sql

if errorlevel 1 (
    echo.
    echo [WARNING] Failed to run setup script.
    echo You may need to run this manually or check your password.
    echo Command: %PSQL_CMD% -U postgres -f setup_postgres.sql
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if errorlevel 2 exit /b 1
)
echo.

REM Test database connection
echo [2/4] Testing database connection...
python db_config.py
if errorlevel 1 (
    echo.
    echo [ERROR] Database connection failed!
    echo Please check your PostgreSQL installation and .env configuration.
    echo See POSTGRESQL_SETUP.md for detailed instructions.
    pause
    exit /b 1
)
echo.

REM Initialize database schema
echo [3/4] Initializing database schema...
python init_postgres.py
if errorlevel 1 (
    echo.
    echo [ERROR] Database initialization failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo.

REM Test application startup
echo [4/4] Testing application...
echo This will start the app briefly to verify everything works.
echo Press Ctrl+C to stop after verification.
echo.
timeout /t 3 >nul
python app.py

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Edit .env file with your actual credentials
echo 2. Run: python app.py
echo 3. Visit: http://localhost:5000
echo.
pause
