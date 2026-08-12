import sqlite3

from flask import current_app, g


def get_db():

    if "db" not in g:

        database = current_app.config.get(
            "DATABASE",
            current_app.instance_path + "/store.db"
        )

        g.db = sqlite3.connect(database)

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):

    db = g.pop("db", None)

    if db is not None:
        db.close()