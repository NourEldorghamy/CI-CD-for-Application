import sys
import sqlite3
from pathlib import Path

import pytest


# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app import create_app


@pytest.fixture
def app(tmp_path):

    # Create a temporary database for testing.
    database = tmp_path / "test.db"

    connection = sqlite3.connect(database)

    connection.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            rating REAL,
            image TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users (id)
        )
    """)

    connection.execute("""
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,

            FOREIGN KEY (order_id)
                REFERENCES orders (id)
                ON DELETE CASCADE,

            FOREIGN KEY (product_id)
                REFERENCES products (id)
        )
    """)

    # Add a test product.
    connection.execute("""
        INSERT INTO products
        (name, description, price, category, rating, image, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Test Headphones",
        "Test product for automated testing.",
        50.00,
        "Audio",
        4.5,
        "headphones.jpg",
        10
    ))

    connection.commit()
    connection.close()

    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "DATABASE": str(database)
    })

    return app


@pytest.fixture
def client(app):

    return app.test_client()