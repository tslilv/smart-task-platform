"""Application factory and Flask configuration."""

import os
from flask import Flask
from app.db import init_db
from flask_cors import CORS


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

    # Load the Flask secret key from an environment variable or use a default value for development.
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Allow the frontend (running on a different origin) to access the backend
    # and include session cookies for authentication.
    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    )

    init_db(app)

    from app.routes import main
    app.register_blueprint(main)

    return app