import random
from app import get_db, app


STATUSES = ["pending", "paid", "shipped", "refunded"]

def seed_orders(num_orders=100):
    db = get_db()

    users = db.execute("SELECT id FROM users").fetchall()
    products = db.execute("SELECT id, price FROM products").fetchall()

    if not users or not products:
        raise Exception("Users or Products table is empty.")

    for _ in range(num_orders):

        user = random.choice(users)
        status = random.choice(STATUSES)

        num_items = random.randint(1, 5)
        chosen_products = random.sample(products, min(num_items, len(products)))

        total_amount = 0

        cursor = db.execute("""
            INSERT INTO orders (user_id, status, total_amount)
            VALUES (?, ?, ?)
        """, (user["id"], status, 0))

        order_id = cursor.lastrowid

        for product in chosen_products:
            quantity = random.randint(1, 5)
            price = product["price"]

            total_amount += quantity * price

            db.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (?, ?, ?, ?)
            """, (order_id, product["id"], quantity, price))

        db.execute("""
            UPDATE orders
            SET total_amount = ?
            WHERE id = ?
        """, (total_amount, order_id))

    db.commit()
    print(f"✅ Seeded {num_orders} realistic orders.")


if __name__ == "__main__":
    with app.app_context():
        seed_orders(100)