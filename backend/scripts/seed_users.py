from werkzeug.security import generate_password_hash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "shipments.db"

conn = sqlite3.connect('shipments.db')
db = conn.cursor()

users = [
    ('admin', 'adminpassword', 'admin'),
    ('operations', 'opspassword', 'operations'),
    ('support', 'supportpassword', 'support'),
]


for username, password, role in users:
    db.execute(
        'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
        (username, generate_password_hash(password, method="pbkdf2:sha256"), role)
    )

conn.commit()
conn.close()