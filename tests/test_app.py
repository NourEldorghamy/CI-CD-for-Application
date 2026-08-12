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