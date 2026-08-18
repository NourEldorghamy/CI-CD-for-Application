def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Products" in response.data


def test_register_page(client):
    response = client.get("/register")

    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_cart_page(client):
    response = client.get("/cart")

    assert response.status_code == 200


def test_checkout_requires_login(client):
    response = client.get("/checkout")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_account_requires_login(client):
    response = client.get("/account")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_product_not_found(client):
    response = client.get("/products/999999")

    assert response.status_code == 404

def test_register_user(client):
    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_duplicate_registration(client):
    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123",
        "confirm_password": "TestPassword123"
    }

    first_response = client.post(
        "/register",
        data=user_data,
        follow_redirects=False
    )

    assert first_response.status_code == 302

    second_response = client.post(
        "/register",
        data=user_data,
        follow_redirects=False
    )

    assert second_response.status_code == 400
    assert b"already exists" in second_response.data

def test_login_success(client):
    # Create a user first.
    register_response = client.post(
        "/register",
        data={
            "name": "Login User",
            "email": "login@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert register_response.status_code == 302

    # Log in with the registered user's credentials.
    login_response = client.post(
        "/login",
        data={
            "email": "login@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

def test_invalid_login(client):
    # Create a user first.
    register_response = client.post(
        "/register",
        data={
            "name": "Invalid Login User",
            "email": "invalidlogin@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert register_response.status_code == 302

    # Attempt to log in with the wrong password.
    login_response = client.post(
        "/login",
        data={
            "email": "invalidlogin@example.com",
            "password": "WrongPassword123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 401

def test_logout(client):
    # Create a user.
    register_response = client.post(
        "/register",
        data={
            "name": "Logout User",
            "email": "logout@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert register_response.status_code == 302

    # Log in.
    login_response = client.post(
        "/login",
        data={
            "email": "logout@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

    # Log out.
    logout_response = client.get(
        "/logout",
        follow_redirects=False
    )

    assert logout_response.status_code == 302

def test_add_product_to_cart(client):
    response = client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    assert response.status_code == 302

    cart_response = client.get("/cart")

    assert cart_response.status_code == 200
    assert b"Test Headphones" in cart_response.data

def test_increase_cart_quantity(client):
    # Add the test product to the cart.
    add_response = client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    assert add_response.status_code == 302

    # Increase the quantity.
    increase_response = client.get(
        "/cart/increase/1",
        follow_redirects=False
    )

    assert increase_response.status_code == 302

    # Verify the quantity in the session.
    with client.session_transaction() as session:
        cart = session["cart"]

        assert cart["1"] == 2


def test_decrease_cart_quantity(client):
    # Add the test product twice so its quantity is 2.
    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    # Decrease the quantity.
    decrease_response = client.get(
        "/cart/decrease/1",
        follow_redirects=False
    )

    assert decrease_response.status_code == 302

    # Verify the quantity decreased from 2 to 1.
    with client.session_transaction() as session:
        cart = session["cart"]

        assert cart["1"] == 1

def test_remove_item_from_cart(client):
    # Add the test product to the cart.
    add_response = client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    assert add_response.status_code == 302

    # Remove the product from the cart.
    remove_response = client.get(
        "/cart/remove/1",
        follow_redirects=False
    )

    assert remove_response.status_code == 302

    # Verify the product was removed from the session cart.
    with client.session_transaction() as session:
        cart = session.get("cart", {})

        assert "1" not in cart

def test_empty_cart_cannot_checkout(client):
    # Register a user.
    register_response = client.post(
        "/register",
        data={
            "name": "Checkout User",
            "email": "emptycheckout@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert register_response.status_code == 302

    # Log in.
    login_response = client.post(
        "/login",
        data={
            "email": "emptycheckout@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

    # Try to access checkout with an empty cart.
    checkout_response = client.get(
        "/checkout",
        follow_redirects=False
    )

    assert checkout_response.status_code in (302, 400)

def test_checkout_creates_order(client):
    # Register a user.
    register_response = client.post(
        "/register",
        data={
            "name": "Order User",
            "email": "order@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert register_response.status_code == 302

    # Log in.
    login_response = client.post(
        "/login",
        data={
            "email": "order@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    assert login_response.status_code == 302

    # Add product to cart.
    add_response = client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    assert add_response.status_code == 302

    # Submit checkout.
    checkout_response = client.post(
        "/checkout",
        data={
            "customer_name": "Order User",
            "email": "order@example.com",
            "address": "123 Test Street"
        },
        follow_redirects=False
    )

    assert checkout_response.status_code == 302
    assert "/order/" in checkout_response.headers["Location"]

def test_checkout_reduces_stock(client):
    # Register a user.
    client.post(
        "/register",
        data={
            "name": "Stock User",
            "email": "stock@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Log in.
    client.post(
        "/login",
        data={
            "email": "stock@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Add the product twice.
    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    # Checkout.
    checkout_response = client.post(
        "/checkout",
        data={
            "customer_name": "Stock User",
            "email": "stock@example.com",
            "address": "123 Stock Street"
        },
        follow_redirects=False
    )

    assert checkout_response.status_code == 302

    # Check the database.
    with client.application.app_context():
        from app.database import get_db

        db = get_db()

        product = db.execute(
            """
            SELECT stock
            FROM products
            WHERE id = ?
            """,
            (1,)
        ).fetchone()

        assert product["stock"] == 8

def test_order_appears_in_account(client):
    # Register a user.
    client.post(
        "/register",
        data={
            "name": "Account Order User",
            "email": "accountorder@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Log in.
    client.post(
        "/login",
        data={
            "email": "accountorder@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Add product.
    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    # Create order.
    checkout_response = client.post(
        "/checkout",
        data={
            "customer_name": "Account Order User",
            "email": "accountorder@example.com",
            "address": "123 Account Street"
        },
        follow_redirects=False
    )

    assert checkout_response.status_code == 302

    # Open account page.
    account_response = client.get("/account")

    assert account_response.status_code == 200
    assert b"Account Order User" in account_response.data

def test_order_confirmation(client):
    # Register a user.
    client.post(
        "/register",
        data={
            "name": "Confirmation User",
            "email": "confirmation@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Log in.
    client.post(
        "/login",
        data={
            "email": "confirmation@example.com",
            "password": "TestPassword123"
        },
        follow_redirects=False
    )

    # Add product.
    client.get(
        "/cart/add/1",
        follow_redirects=False
    )

    # Create order.
    checkout_response = client.post(
        "/checkout",
        data={
            "customer_name": "Confirmation User",
            "email": "confirmation@example.com",
            "address": "123 Confirmation Street"
        },
        follow_redirects=False
    )

    assert checkout_response.status_code == 302

    # Extract order ID from the redirect URL.
    location = checkout_response.headers["Location"]
    order_id = location.rstrip("/").split("/")[-1]

    # Open order confirmation page.
    confirmation_response = client.get(
        f"/order/{order_id}"
    )

    assert confirmation_response.status_code == 200
    assert b"Confirmation User" in confirmation_response.data

