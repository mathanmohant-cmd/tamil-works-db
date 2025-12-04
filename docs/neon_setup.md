# Neon Database Setup Guide for Tamil Literature Database

## Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up" (top right)
3. Sign up using:
   - GitHub account (recommended - fastest)
   - Google account
   - Email/password

4. Verify your email if using email signup

## Step 2: Create a New Project

1. Once logged in, click **"Create a project"**
2. Fill in the details:
   - **Project name**: `tamil-literature-db` (or your choice)
   - **Database name**: `tamil_literature`
   - **Region**: Choose closest to your location:
     - Asia: Singapore (aws-ap-southeast-1)
     - India: Mumbai if available, otherwise Singapore
     - US: US East (aws-us-east-1)
     - Europe: Frankfurt (aws-eu-central-1)
   - **PostgreSQL version**: 15 or 16 (latest stable)

3. Click **"Create Project"**

## Step 3: Get Connection Details

After project creation, you'll see:

1. **Connection String** - Copy this! It looks like:
   ```
   postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require
   ```

2. **Connection Details** (you can also find these in Settings):
   - Host: `ep-xxxxx.region.aws.neon.tech`
   - Database: `tamil_literature`
   - User: (automatically generated)
   - Password: (automatically generated)
   - Port: `5432`

3. **Save these details** in a safe place (like a password manager)

## Step 4: Install PostgreSQL Client (if you don't have it)

### Windows:
```bash
# Option 1: Using Chocolatey
choco install postgresql

# Option 2: Download from
# https://www.postgresql.org/download/windows/
# Install only the command line tools (psql)
```

### macOS:
```bash
brew install postgresql
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get install postgresql-client
```

## Step 5: Connect to Your Database

Using the connection string from Step 3:

```bash
psql "postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require"
```

Or connect with individual parameters:

```bash
psql -h ep-xxxxx.region.aws.neon.tech -U username -d tamil_literature
# Enter password when prompted
```

## Step 6: Create the Database Schema

Once connected to psql, run:

```sql
-- You can paste the entire schema file content here
-- Or use \i command if you have the file locally
\i C:/Users/t_mat/tamil_literature_schema.sql
```

Or from your command line (without being in psql):

```bash
psql "postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require" -f C:/Users/t_mat/tamil_literature_schema.sql
```

## Step 7: Verify Installation

```sql
-- List all tables
\dt

-- Should show:
-- works
-- sections
-- verses
-- lines
-- words
-- commentaries
-- cross_references

-- List all views
\dv

-- Should show:
-- verse_hierarchy
-- word_details

-- Check sample data
SELECT * FROM works;
SELECT * FROM word_details WHERE work_name = 'Thirukkural';
```

## Step 8: Save Connection String for Later Use

Create a file to store your connection details:

**Method 1: Environment Variable (Recommended)**

Windows (PowerShell):
```powershell
[Environment]::SetEnvironmentVariable("NEON_DB_URL", "postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require", "User")
```

Linux/macOS:
```bash
echo 'export NEON_DB_URL="postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require"' >> ~/.bashrc
source ~/.bashrc
```

**Method 2: Config File**

Create `C:/Users/t_mat/.neon_db_config`:
```
HOST=ep-xxxxx.region.aws.neon.tech
DATABASE=tamil_literature
USER=username
PASSWORD=password
PORT=5432
SSLMODE=require
```

## Connecting from Different Tools

### Using DBeaver (Free Database GUI)

1. Download from https://dbeaver.io/download/
2. Install and open
3. Click "New Database Connection"
4. Select "PostgreSQL"
5. Enter connection details from Step 3
6. Enable SSL (required for Neon)
7. Click "Test Connection"
8. Click "Finish"

### Using pgAdmin (PostgreSQL GUI)

1. Download from https://www.pgadmin.org/download/
2. Install and open
3. Right-click "Servers" → "Create" → "Server"
4. General tab: Name = "Neon Tamil Literature"
5. Connection tab: Enter details from Step 3
6. SSL tab: Mode = "Require"
7. Click "Save"

### Using Python

```python
import psycopg2

# Using connection string
conn = psycopg2.connect(
    "postgresql://username:password@ep-xxxxx.region.aws.neon.tech/tamil_literature?sslmode=require"
)

# Or using individual parameters
conn = psycopg2.connect(
    host="ep-xxxxx.region.aws.neon.tech",
    database="tamil_literature",
    user="username",
    password="password",
    port=5432,
    sslmode="require"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM works")
print(cursor.fetchall())
conn.close()
```

### Using Node.js

```javascript
const { Client } = require('pg');

const client = new Client({
  connectionString: process.env.NEON_DB_URL,
  ssl: { rejectUnauthorized: false }
});

await client.connect();
const res = await client.query('SELECT * FROM works');
console.log(res.rows);
await client.end();
```

## Important Notes

### Free Tier Limits
- **Storage**: 3 GB (plenty for text data)
- **Compute**: Shared CPU, auto-suspends after 5 minutes of inactivity
- **Branches**: 10 branches (useful for testing)
- **Connection**: No connection limit

### Best Practices

1. **Always use SSL**: Neon requires SSL connections
2. **Use connection pooling** for web applications
3. **Create branches** for testing before modifying production data
4. **Regular backups**: Neon provides automatic backups, but export important data
5. **Monitor usage**: Check dashboard for storage and compute usage

### Neon-Specific Features

**Database Branching** (like Git for databases):
```bash
# Create a branch for testing
# Do this from Neon dashboard or CLI
neonctl branches create --name testing
```

**Auto-suspend**: Database automatically suspends after 5 minutes of inactivity (saves resources)

**Scale to zero**: On free tier, compute scales to zero when not in use

## Troubleshooting

### Connection Refused
- Check SSL is enabled (`sslmode=require`)
- Verify connection string is correct
- Check if project is in suspended state (wait 1-2 seconds, it auto-wakes)

### Authentication Failed
- Verify username and password
- Password may have special characters - ensure proper URL encoding
- Reset password in Neon dashboard if needed

### SSL Error
- Always include `sslmode=require` in connection string
- For programming languages, ensure SSL is properly configured

## Next Steps

After setup:
1. Run the queries from `tamil_literature_queries.sql`
2. Start populating with actual Tamil literature data
3. Create additional indexes based on query patterns
4. Consider setting up a REST API using PostgREST or similar

## Quick Reference

**Connect via psql**:
```bash
psql $NEON_DB_URL
```

**Run a query file**:
```bash
psql $NEON_DB_URL -f queries.sql
```

**Export data**:
```bash
pg_dump $NEON_DB_URL > backup.sql
```

**Import data**:
```bash
psql $NEON_DB_URL < backup.sql
```

## Support

- Neon Documentation: https://neon.tech/docs
- Neon Discord: https://discord.gg/neon
- PostgreSQL Documentation: https://www.postgresql.org/docs/
