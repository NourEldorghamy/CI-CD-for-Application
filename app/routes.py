from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.database import get_db


main = Blueprint("main", __name__)


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for(
                    "main.login",
                    next=request.path
                )
            )

        return view(*args, **kwargs)

    return wrapped_view


# ============================================================
# REGISTER
# ============================================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:
            return "All fields are required.", 400

        if password != confirm_password:
            return "Passwords do not match.", 400

        if len(password) < 8:
            return "Password must be at least 8 characters.", 400

        db = get_db()

        existing_user = db.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user is not None:
            return "An account with this email already exists.", 400

        password_hash = generate_password_hash(password)

        db.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        db.commit()

        return redirect(
            url_for("main.login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        db = get_db()

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if user is None:

            return "Invalid email or password.", 401

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            return "Invalid email or password.", 401

        # ----------------------------------------------------
        # Preserve the cart before clearing the session.
        # ----------------------------------------------------

        cart = session.get(
            "cart",
            {}
        )

        # Clear previous session data.
        session.clear()

        # ----------------------------------------------------
        # Store authenticated user.
        # ----------------------------------------------------

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        # Restore shopping cart.
        session["cart"] = cart

        # ----------------------------------------------------
        # Return user to the page they originally requested.
        # ----------------------------------------------------

        next_page = request.args.get("next")

        if next_page:
            return redirect(next_page)

        return redirect(
            url_for("main.home")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@main.route("/logout")
def logout():

    # Clear the entire session.
    session.clear()

    # Return to the home page.
    return redirect(
        url_for("main.home")
    )


# ============================================================
# ACCOUNT
# ============================================================

@main.route("/account")
@login_required
def account():

    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # If the user no longer exists,
    # clear the invalid session.
    if user is None:

        session.clear()

        return redirect(
            url_for("main.login")
        )

    orders = db.execute(
        """
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    cart = session.get(
        "cart",
        {}
    )

    cart_count = sum(
        cart.values()
    )

    return render_template(
        "account.html",
        user=user,
        orders=orders,
        cart_count=cart_count
    )


# ============================================================
# HOME
# ============================================================

@main.route("/")
def home():

    db = get_db()

    products = db.execute(
        """
        SELECT *
        FROM products
        """
    ).fetchall()

    cart = session.get(
        "cart",
        {}
    )

    cart_count = sum(
        cart.values()
    )

    return render_template(
        "index.html",
        products=products,
        cart_count=cart_count
    )


# ============================================================
# PRODUCT DETAILS
# ============================================================

@main.route("/products/<int:product_id>")
def product_detail(product_id):

    db = get_db()

    product = db.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        return "Product not found", 404

    return render_template(
        "product_detail.html",
        product=product
    )


# ============================================================
# CART
# ============================================================

@main.route("/cart")
def cart():

    cart = session.get(
        "cart",
        {}
    )

    product_ids = list(
        cart.keys()
    )

    products = []

    if product_ids:

        db = get_db()

        placeholders = ",".join(
            "?" * len(product_ids)
        )

        products = db.execute(
            f"""
            SELECT *
            FROM products
            WHERE id IN ({placeholders})
            """,
            product_ids
        ).fetchall()

    total = 0
    cart_items = []

    for product in products:

        quantity = cart[
            str(product["id"])
        ]

        subtotal = (
            product["price"] * quantity
        )

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    cart_count = sum(
        cart.values()
    )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


# ============================================================
# ADD TO CART
# ============================================================

@main.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):

    db = get_db()

    product = db.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        return "Product not found", 404

    # Do not allow adding out-of-stock products.
    if product["stock"] <= 0:

        return redirect(
            url_for("main.cart")
        )

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0
    )

    # Do not allow quantity to exceed stock.
    if current_quantity >= product["stock"]:

        return redirect(
            url_for("main.cart")
        )

    cart[product_id] = (
        current_quantity + 1
    )

    session["cart"] = cart

    return redirect(
        url_for("main.cart")
    )


# ============================================================
# INCREASE QUANTITY
# ============================================================

@main.route("/cart/increase/<int:product_id>")
def increase_quantity(product_id):

    db = get_db()

    product = db.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        return "Product not found", 404

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0
    )

    # Do not exceed available stock.
    if current_quantity >= product["stock"]:

        return redirect(
            url_for("main.cart")
        )

    cart[product_id] = (
        current_quantity + 1
    )

    session["cart"] = cart

    return redirect(
        url_for("main.cart")
    )


# ============================================================
# DECREASE QUANTITY
# ============================================================

@main.route("/cart/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id not in cart:

        return redirect(
            url_for("main.cart")
        )

    if cart[product_id] > 1:

        cart[product_id] -= 1

    else:

        del cart[product_id]

    session["cart"] = cart

    return redirect(
        url_for("main.cart")
    )


# ============================================================
# REMOVE FROM CART
# ============================================================

@main.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

    session["cart"] = cart

    return redirect(
        url_for("main.cart")
    )


# ============================================================
# CHECKOUT
# ============================================================

@main.route(
    "/checkout",
    methods=["GET", "POST"]
)
@login_required
def checkout():

    cart = session.get(
        "cart",
        {}
    )

    # Cannot checkout with an empty cart.
    if not cart:

        return redirect(
            url_for("main.cart")
        )

    db = get_db()

    product_ids = list(
        cart.keys()
    )

    placeholders = ",".join(
        "?" * len(product_ids)
    )

    products = db.execute(
        f"""
        SELECT *
        FROM products
        WHERE id IN ({placeholders})
        """,
        product_ids
    ).fetchall()

    # Make sure every product still exists.
    if len(products) != len(product_ids):

        return (
            "One or more products in your cart "
            "are no longer available.",
            400
        )

    total = 0
    cart_items = []

    for product in products:

        quantity = cart[
            str(product["id"])
        ]

        # Quantity must be positive.
        if quantity <= 0:

            return (
                "Invalid product quantity.",
                400
            )

        # Quantity cannot exceed stock.
        if quantity > product["stock"]:

            return (
                "Requested quantity exceeds "
                "available stock.",
                400
            )

        subtotal = (
            product["price"] * quantity
        )

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    cart_count = sum(
        cart.values()
    )

    # ========================================================
    # CREATE ORDER
    # ========================================================

    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        if (
            not customer_name
            or not email
            or not address
        ):

            return (
                "All customer information is required.",
                400
            )

        try:

            # Start transaction.
            db.execute("BEGIN")

            # ------------------------------------------------
            # Create order
            # ------------------------------------------------

            cursor = db.execute(
                """
                INSERT INTO orders (
                    user_id,
                    customer_name,
                    email,
                    address,
                    total
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    customer_name,
                    email,
                    address,
                    total
                )
            )

            order_id = cursor.lastrowid

            # ------------------------------------------------
            # Create order items and reduce stock.
            # ------------------------------------------------

            for item in cart_items:

                product_id = (
                    item["product"]["id"]
                )

                quantity = item["quantity"]

                price = item["product"]["price"]

                # Reduce stock atomically.
                stock_update = db.execute(
                    """
                    UPDATE products
                    SET stock = stock - ?
                    WHERE id = ?
                      AND stock >= ?
                    """,
                    (
                        quantity,
                        product_id,
                        quantity
                    )
                )

                if stock_update.rowcount != 1:

                    raise ValueError(
                        "Insufficient stock."
                    )

                # Create order item.
                db.execute(
                    """
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                )

            # Save transaction.
            db.commit()

        except Exception:

            # Undo transaction.
            db.rollback()

            return (
                "An error occurred while "
                "creating the order.",
                500
            )

        # Empty cart after successful order.
        session.pop(
            "cart",
            None
        )

        return redirect(
            url_for(
                "main.order_confirmation",
                order_id=order_id
            )
        )

    # ========================================================
    # CHECKOUT PAGE
    # ========================================================

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total,
        cart_count=cart_count
    )


# ============================================================
# ORDER CONFIRMATION
# ============================================================

@main.route("/order/<int:order_id>")
@login_required
def order_confirmation(order_id):

    db = get_db()

    # Get order belonging to logged-in user.
    order = db.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
          AND user_id = ?
        """,
        (
            order_id,
            session["user_id"]
        )
    ).fetchone()

    if order is None:

        return "Order not found", 404

    # Get products belonging to this order.
    order_items = db.execute(
        """
        SELECT
            order_items.*,
            products.name,
            products.image
        FROM order_items
        JOIN products
            ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    return render_template(
        "order_confirmation.html",
        order=order,
        order_items=order_items
    )