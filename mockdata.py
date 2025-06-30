import psycopg2

import os

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # Step 1: Create the table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            code VARCHAR(255) UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        );
    """)

    # Step 2: Insert test data
    cur.execute("""
        INSERT INTO urls (code, original_url)
        VALUES (%s, %s)
        ON CONFLICT (code) DO NOTHING;
    """, ('test123', 'https://www.google.com'))

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Table verified and mock data inserted.")

except Exception as e:
    print(f"❌ Error: {e}")
