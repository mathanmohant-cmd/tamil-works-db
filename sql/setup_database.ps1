# Tamil Literature Database Setup Script for PostgreSQL
# PowerShell version with better error handling

$PSQL = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
$DB_NAME = "tamil_literature_db"
$DB_USER = "postgres"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Tamil Literature Database Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if psql exists
if (-not (Test-Path $PSQL)) {
    Write-Host "Error: PostgreSQL psql not found at: $PSQL" -ForegroundColor Red
    Write-Host "Please update the PSQL variable with the correct path" -ForegroundColor Yellow
    exit 1
}

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Step 1: Creating database..." -ForegroundColor Yellow
& $PSQL -U $DB_USER -c "CREATE DATABASE $DB_NAME WITH ENCODING 'UTF8';"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Note: Database might already exist, continuing..." -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 2: Installing schema and initial sample data..." -ForegroundColor Yellow
& $PSQL -U $DB_USER -d $DB_NAME -f "sql\schema.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install schema" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "Step 3: Loading additional sample word data..." -ForegroundColor Yellow
& $PSQL -U $DB_USER -d $DB_NAME -f "sql\sample_word_data.sql"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to load sample data" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Green
Write-Host "Database setup completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database name: $DB_NAME"
Write-Host ""
Write-Host "To connect to the database, use:"
Write-Host "$PSQL -U $DB_USER -d $DB_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or set the connection string:"
Write-Host "postgresql://$DB_USER:yourpassword@localhost:5432/$DB_NAME" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to continue..."
