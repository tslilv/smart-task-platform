"""Application factory and Flask configuration."""

import os
from flask import Flask
from app.db import init_db


def create_app():
    """Create and configure the Flask application."""
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    init_db(app)

    from app.routes import main
    app.register_blueprint(main)

    return app