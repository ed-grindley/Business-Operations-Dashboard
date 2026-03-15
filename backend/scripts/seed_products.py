import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "shipments.db"

conn = sqlite3.connect('shipments.db')
db = conn.cursor()

products = [
    ('product4', 4, 80, 12.20, "PROD-4"),
    ('product5', 5, 40, 15, "PROD-5"),
    ('product6', 6, 75, 25, "PROD-6"),
    ('product7', 7, 110, 10, "PROD-7"),
    ('product8', 8, 58, 30, "PROD-8"),
    ('product9', 9, 90, 50, "PROD-9"),
]

for name, id, stock_quantity, price, sku in products:
    db.execute("INSERT INTO products (name, id, stock_quantity, price, sku) VALUES (?, ?, ?, ?, ?)", (name, id, stock_quantity, price, sku)
               )
    
conn.commit()
conn.close()
