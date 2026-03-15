import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "shipments.db"

conn = sqlite3.connect('shipments.db')
db = conn.cursor()


order_items = [
    (1, 1, 99, 12.50),
    (2, 2, 180, 17.00),
    (3, 3, 500, 20.99),
    (4, 3,50, 20.99),
    (5, 2, 720, 17.00),
    (6, 1, 59, 12.50),
    (7, 1, 100, 12.50),
    (8, 2, 2000, 17.00),
    (9, 3, 230, 20.99),
    (10, 3, 70, 20.99), 
    (11, 2, 420, 17.00),
]

for order_id, product_id, quantity, price_at_purchase in order_items:
    db.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)", (order_id, product_id, quantity, price_at_purchase))

conn.commit()
conn.close()