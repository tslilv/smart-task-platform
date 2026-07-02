import os
from flask import Flask
from app.db import init_db


def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, "templates")

    app = Flask(__name__, template_folder=template_dir)

    init_db(app)

    from app.routes import main
    app.register_blueprint(main)

    return app