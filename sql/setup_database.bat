@echo off
REM Tamil Literature Database Setup Script for PostgreSQL
REM This script will create the database and load all schema and sample data

SET PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
SET DB_NAME=tamil_literature_db
SET DB_USER=postgres

echo =========================================
echo Tamil Literature Database Setup
echo =========================================
echo.

echo Step 1: Creating database...
%PSQL% -U %DB_USER% -c "CREATE DATABASE %DB_NAME% WITH ENCODING 'UTF8';"
if %ERRORLEVEL% NEQ 0 (
    echo Note: Database might already exist, continuing...
)
echo.

echo Step 2: Installing schema and initial sample data...
%PSQL% -U %DB_USER% -d %DB_NAME% -f sql\schema.sql
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install schema
    exit /b 1
)
echo.

echo Step 3: Loading additional sample word data...
%PSQL% -U %DB_USER% -d %DB_NAME% -f sql\sample_word_data.sql
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to load sample data
    exit /b 1
)
echo.

echo =========================================
echo Database setup completed successfully!
echo =========================================
echo.
echo Database name: %DB_NAME%
echo.
echo To connect to the database, use:
echo %PSQL% -U %DB_USER% -d %DB_NAME%
echo.
echo Or set the connection string:
echo postgresql://%DB_USER%:yourpassword@localhost:5432/%DB_NAME%
echo.

pause
