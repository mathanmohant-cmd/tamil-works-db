#!/usr/bin/env python3
"""Reset admin password on Railway database"""
import psycopg2
import bcrypt

DATABASE_URL = "postgresql://postgres:uMqwCkeykRglEkccpiXdYcgUKOiuNluw@centerbeam.proxy.rlwy.net:26715/railway"

# Generate bcrypt hash for password
password = "TKsltk#123"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Generated hash: {password_hash}")

# Connect and update
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Update admin password
cur.execute(
    "UPDATE admin_users SET password_hash = %s WHERE username = %s",
    [password_hash, 'admin']
)
conn.commit()

print("Updated admin password")

# Verify
cur.execute("SELECT username, password_hash FROM admin_users WHERE username = 'admin'")
result = cur.fetchone()
print(f"Verified: username={result[0]}, hash_length={len(result[1])}")

# Test the hash works
test_hash = result[1]
if bcrypt.checkpw(password.encode('utf-8'), test_hash.encode('utf-8')):
    print("Password verification successful!")
else:
    print("Password verification failed!")

cur.close()
conn.close()
