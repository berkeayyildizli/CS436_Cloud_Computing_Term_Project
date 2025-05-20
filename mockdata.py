import psycopg2

# Replace with your actual credentials
DB_HOST = "34.58.226.13"
DB_PORT = "5432"
DB_NAME = "url_shortener"
DB_USER = "url_user"
DB_PASSWORD = "url_pass"

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
