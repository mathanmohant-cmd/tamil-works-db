@echo off
REM Verify Tamil Literature Database Installation

SET PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
SET DB_NAME=tamil_literature_db
SET DB_USER=postgres

echo =========================================
echo Tamil Literature Database Verification
echo =========================================
echo.

echo Checking database connection...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT version();"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Cannot connect to database
    exit /b 1
)
echo.

echo Listing all tables...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "\dt"
echo.

echo Checking works table...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT work_id, work_name, work_name_tamil, author FROM works ORDER BY work_id;"
echo.

echo Checking sections count...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT COUNT(*) as total_sections FROM sections;"
echo.

echo Checking verses count...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT work_name, COUNT(*) as verse_count FROM verses v JOIN works w ON v.work_id = w.work_id GROUP BY work_name ORDER BY work_name;"
echo.

echo Checking words count...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT COUNT(*) as total_words FROM words;"
echo.

echo Sample query: Find all occurrences of word root 'முதல்'...
%PSQL% -U %DB_USER% -d %DB_NAME% -c "SELECT work_name, hierarchy_path, word_text, line_text FROM word_details WHERE word_root = 'முதல்' ORDER BY work_name;"
echo.

echo =========================================
echo Verification complete!
echo =========================================

pause
