from datetime import datetime
import uuid

from db import get_db
import sqlite3

def flash_success(message):
    from flask import flash
    flash(message, 'success')

def flash_error(message):
    from flask import flash
    flash(message, 'error')

def get_user_by_id(user_id):
    conn = sqlite3.connect("shipments.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    user = db.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (int(user_id),)
    ).fetchone()

    conn.close()
    return user

def update_order_status(order_id, new_status, actor_user_id):
    db = get_db()

    order = db.execute(
        "SELECT status FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if not order:
        return False, "Order not found"

    old_status = order["status"]

    if not is_valid_status_transition(old_status, new_status):
        return False, f"Invalid status transition from '{old_status}' to '{new_status}'"

    if old_status != "shipped" and new_status == "shipped":

        items = db.execute(
            "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
            (order_id,)
        ).fetchall()

        for item in items:
            product = db.execute(
                "SELECT stock_quantity FROM products WHERE id = ?",
                (item["product_id"],)
            ).fetchone()

            if product["stock_quantity"] < item["quantity"]:
                return False, f"Insufficient stock for product {item['product_id']}"

        for item in items:
            db.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (item["quantity"], item["product_id"])
            )

    db.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (new_status, order_id)
    )

    db.execute(
        """
        INSERT INTO audit_logs
        (actor_user_id, action, entity_type, entity_id, before_state, after_state)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (actor_user_id, "order_status_update", "order", order_id, old_status, new_status)
    )

    db.commit()

    return True, None

def bulk_shipment(order_ids, actor_user_id):
    db = get_db()
    bulk_id = str(uuid.uuid4())

    for order_id in order_ids:
        update_order_status(order_id, "shipped", actor_user_id)

        db.execute("""UPDATE audit_logs SET bulk_operation_id = ? WHERE entity_type = 'order' AND entity_id = ? ORDER BY id DESC LIMIT 1 """, (bulk_id, order_id))      

def is_valid_status_transition(old_status, new_status):
    valid_transitions = {
        "pending": ["paid"],
        "paid": ["shipped", "refunded"],
        "shipped": ["refunded"],
        "refunded": []
    }
    return new_status in valid_transitions.get(old_status, [])       
            
            