from backend.db import get_db



def ingest_order(order_data, bulk_id=None):
    db = get_db()

    try:
        cursor = db.execute(
            "INSERT INTO orders (external_id, status) VALUES (?, ?)",
            (order_data["id"], "pending")
        )
        order_id = cursor.lastrowid

        for item in order_data["items"]:
            db.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item["product_id"], item["qty"], item["price"]))

        db.execute("""
            INSERT INTO audit_logs (order_id, action, bulk_id)
            VALUES (?, ?, ?)
        """, (order_id, "created", bulk_id))

        db.commit()

    except:
        db.rollback()
        raise