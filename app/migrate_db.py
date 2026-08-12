import sqlite3

from pathlib import Path


DATABASE = Path(__file__).resolve().parent.parent / "instance" / "store.db"


def migrate_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # Check the existing orders table.
    columns = cursor.execute(
        "PRAGMA table_info(orders)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    # Add user_id only if it does not already exist.
    if "user_id" not in column_names:

        cursor.execute("""
            ALTER TABLE orders
            ADD COLUMN user_id INTEGER
        """)

        print("Added user_id column to orders.")

    else:

        print("user_id already exists.")

    connection.commit()

    connection.close()

    print("Database migration completed successfully.")


if __name__ == "__main__":

    migrate_database()