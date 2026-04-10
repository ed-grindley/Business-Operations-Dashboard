import uuid
from dotenv import load_dotenv
from flask import Flask, flash, json, redirect, render_template, session, request, url_for, g
load_dotenv()
from backend.services.orders import ingest_order
from db import get_db
import config
import sqlite3
from helpers import get_user_by_id, update_order_status
from werkzeug.security import check_password_hash, generate_password_hash
from auth import role_required
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import User


app = Flask(__name__)
app.config.from_object("config.Config") 

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user_row = get_user_by_id(user_id)
    if user_row:
        return User(user_row["id"], user_row["username"], user_row["role"])
    return None

@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        user_row = get_db().execute(
            "SELECT id, username, password_hash, role FROM users WHERE username=?",
            (request.form["username"],)
        ).fetchone()

        if user_row and check_password_hash(user_row["password_hash"], request.form["password"]):
            user_obj = User(user_row["id"], user_row["username"], user_row["role"])
            login_user(user_obj)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/inventory")
@login_required
def inventory():
    db = get_db()
    products = db.execute("SELECT id, name, stock_quantity, sku, price FROM products ORDER BY name").fetchall()

    return render_template("inventory.html", products=products)

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db = get_db()

    if not current_user.is_authenticated:
        flash("You must be logged in to view the dashboard.", "danger")
        return redirect(url_for("login"))

    filters = {
        "order_id": request.args.get("order_id", ""),   
        "status": request.args.get("status", ""),
        "date_from": request.args.get("from", ""),
        "date_until": request.args.get("until", ""),
        "user_id": request.args.get("user", "")
    }


    query = "SELECT orders.id, orders.status, orders.created_at, orders.user_id, order_items.quantity, products.name FROM orders JOIN order_items ON orders.id = order_items.order_id JOIN products ON order_items.product_id = products.id WHERE 1=1"
    params = []

    if filters["order_id"]:
        query += " AND orders.id = ?"
        params.append(filters["order_id"])

    if filters["status"]:
        query += " AND orders.status = ?"
        params.append(filters["status"])

    if filters["date_from"]:
        query += " AND orders.created_at >= ?"
        params.append(filters["date_from"])

    if filters["date_until"]:
        query += " AND orders.created_at <= ?"
        params.append(filters["date_until"])

    if current_user.role == 'admin' and filters["user_id"]:
        query += " AND orders.user_id = ?"
        params.append(filters["user_id"])


    orders = db.execute(query, params).fetchall()


    users = db.execute("SELECT id, username FROM users").fetchall() if current_user.role == 'admin' else []


    return render_template(
        "dashboard.html",
        filters=filters,
        users=users, current_user=current_user, orders=orders
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/update_status/<int:order_id>", methods=["POST"])
@login_required
@role_required("admin", "operations")
def update_status(order_id):
    
    actor_user_id = current_user.id
    new_status = request.form.get("status")

    update_order_status(order_id, new_status, actor_user_id)

    return redirect(url_for("dashboard"))

@app.route("/bulk_ship", methods=["POST"])
@login_required
@role_required("admin", "operations")
def bulk_ship():

    db = get_db()

    bulk_id = str(uuid.uuid4())
    actor_user_id = current_user.id

    order_ids = request.form.getlist("order_ids")

    if not order_ids:
        flash("No orders selected for shipping.", "warning")
        return redirect(url_for("dashboard"))

    placeholder = ",".join(["?"] * len(order_ids))

    ordered = db.execute(
        f"SELECT id FROM orders WHERE id IN ({placeholder}) ORDER BY created_at ASC",
        order_ids
    ).fetchall()

    shipped = []
    failed = []

    for row in ordered:

        order_id = row["id"]

        success, reason = update_order_status(order_id, "shipped", actor_user_id)

        if success:

            db.execute(
                """
                UPDATE audit_logs
                SET bulk_operation_id = ?
                WHERE entity_type = 'order'
                AND entity_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (bulk_id, order_id)
            )

            shipped.append(str(order_id))

        else:
            failed.append(f"Order {order_id} failed to ship: {reason}")

    db.commit()

    if shipped:
        flash(f"Shipped: Order {', '.join(shipped)}", "success")

    for msg in failed:
        flash(msg, "danger")

    return redirect(url_for("dashboard"))

@app.route("/audit_logs")
@login_required
@role_required("admin")
def audit_logs():
    db = get_db()
    logs = db.execute("SELECT audit_logs.bulk_operation_id, audit_logs.created_at, users.username, audit_logs.action, audit_logs.before_state, audit_logs.after_state FROM audit_logs JOIN users ON audit_logs.actor_user_id = users.id ORDER BY audit_logs.created_at DESC").fetchall()
    return render_template("audit_logs.html", logs=logs)

@app.route("/import-orders", methods=["POST"])
def import_orders():
    file = request.files["file"]
    data = json.load(file)

    bulk_id = str(uuid.uuid4())

    for order in data:
        ingest_order(order, bulk_id)

    return "Imported"


if __name__ == "__main__":
    app.run(debug=True)


