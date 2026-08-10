from flask import Blueprint, render_template

from app.database import get_db


main = Blueprint("main", __name__)


@main.route("/")
def home():

    db = get_db()

    products = db.execute(
        "SELECT * FROM products"
    ).fetchall()

    return render_template(
        "index.html",
        products=products
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