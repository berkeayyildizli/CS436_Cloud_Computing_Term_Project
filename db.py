import psycopg2
import string
import random
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def create_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def insert_url(conn, code, original_url):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (code, original_url) VALUES (%s, %s);",
            (code, original_url)
        )
        conn.commit()

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
