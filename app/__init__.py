from flask import Flask

from app.database import close_db


def create_app(test_config=None):

    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev"
    )

    if test_config is not None:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    from app.routes import main

    app.register_blueprint(main)

    return app