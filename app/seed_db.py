import sqlite3

from pathlib import Path


DATABASE = Path(__file__).resolve().parent.parent / "instance" / "store.db"


products = [
    (
        "Wireless Headphones",
        "High-quality wireless headphones with clear sound and comfortable ear cushions.",
        49.99,
        "Audio",
        4.5,
        "headphones.jpg",
        20
    ),
    (
        "Mechanical Keyboard",
        "A responsive mechanical keyboard designed for comfortable typing and gaming.",
        79.99,
        "Accessories",
        4.8,
        "keyboard.jpg",
        15
    ),
    (
        "Wireless Mouse",
        "A lightweight wireless mouse with precise tracking and long battery life.",
        29.99,
        "Accessories",
        4.3,
        "mouse.jpg",
        30
    ),
    (
        "Smart Watch",
        "A modern smartwatch with fitness tracking and smartphone notifications.",
        99.99,
        "Wearables",
        4.6,
        "smartwatch.jpg",
        10
    )
]


def seed_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.executemany("""
        INSERT INTO products
        (name, description, price, category, rating, image, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, products)

    connection.commit()

    connection.close()


if __name__ == "__main__":
    seed_database()
    print("Products inserted successfully.")