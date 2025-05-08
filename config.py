import os

DB_HOST = os.getenv("DB_HOST", "your-postgresql-vm-ip")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "url_shortener")
DB_USER = os.getenv("DB_USER", "url_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "url_pass")
