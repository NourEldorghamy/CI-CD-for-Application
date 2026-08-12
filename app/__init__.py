from flask import Flask


def create_app():

    app = Flask(__name__)

    app.config.from_mapping(
        DATABASE=app.instance_path + "/store.db",
        SECRET_KEY="dev-secret-key"
    )

    from app.database import close_db

    app.teardown_appcontext(close_db)

    from app.routes import main

    app.register_blueprint(main)

    return app