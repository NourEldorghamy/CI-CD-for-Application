import sqlite3

from pathlib import Path


DATABASE = Path(__file__).resolve().parent.parent / "instance" / "store.db"


def init_db():

    DATABASE.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
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

    connection.commit()

    connection.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")