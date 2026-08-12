from flask import Blueprint, render_template, redirect, url_for, session
from app.database import get_db

main = Blueprint("main", __name__)


@main.route("/")
def home():

    db = get_db()

    products = db.execute(
        "SELECT * FROM products"
    ).fetchall()

    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    return render_template(
        "index.html",
        products=products,
        cart_count=cart_count
    )


@main.route("/products/<int:product_id>")
def product_detail(product_id):

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found", 404

    return render_template(
        "product_detail.html",
        product=product
    )


@main.route("/cart")
def cart():

    cart = session.get("cart", {})

    product_ids = list(cart.keys())

    products = []

    if product_ids:

        db = get_db()

        placeholders = ",".join("?" * len(product_ids))

        products = db.execute(
            f"SELECT * FROM products WHERE id IN ({placeholders})",
            product_ids
        ).fetchall()

    total = 0
    cart_items = []

    for product in products:

        quantity = cart[str(product["id"])]

        subtotal = product["price"] * quantity

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    cart_count = sum(cart.values())

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


@main.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found", 404

    cart = session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    # Do not allow the cart quantity to exceed stock.
    if current_quantity >= product["stock"]:
        return redirect(url_for("main.cart"))

    cart[product_id] = current_quantity + 1

    session["cart"] = cart

    return redirect(url_for("main.cart"))


@main.route("/cart/increase/<int:product_id>")
def increase_quantity(product_id):

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found", 404

    cart = session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    # Do not allow quantity to exceed available stock.
    if current_quantity >= product["stock"]:
        return redirect(url_for("main.cart"))

    cart[product_id] = current_quantity + 1

    session["cart"] = cart

    return redirect(url_for("main.cart"))


@main.route("/cart/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id not in cart:
        return redirect(url_for("main.cart"))

    if cart[product_id] > 1:
        cart[product_id] -= 1
    else:
        del cart[product_id]

    session["cart"] = cart

    return redirect(url_for("main.cart"))


@main.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart

    return redirect(url_for("main.cart"))