import psycopg2

try:
    conn = psycopg2.connect(
        host="34.58.226.13",
        port="5432",
        dbname="url_shortener",
        user="url_user",
        password="url_pass"
    )
    print("✅ Connected successfully.")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
