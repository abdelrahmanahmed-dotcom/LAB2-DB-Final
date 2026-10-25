"""Application factory: builds the Flask app and plugs the pieces together."""
from flask import Flask

from app import db
from app.config import Config
from app.errors import register_error_handlers
from app.routes import auth, library, todos


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(todos.bp)
    app.register_blueprint(library.bp)  # [Lab 3] books and authors
    register_error_handlers(app)
    return app
