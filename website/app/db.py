"""Database connection helper: one MySQL connection per database per request."""
import pymysql
from flask import current_app, g


def _connect(database):
    return pymysql.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=database,
        cursorclass=pymysql.cursors.DictCursor,  # rows come back as dicts
        autocommit=True,
    )


def get_db():
    """Lab 2 database (users + todos). Opened the first time it is needed in a request."""
    if "db" not in g:
        g.db = _connect(current_app.config["DB_NAME"])
    return g.db


def get_library_db():
    """[Lab 3] The library database (author + book). Same server, other database."""
    if "library_db" not in g:
        g.library_db = _connect(current_app.config["LIBRARY_DB_NAME"])
    return g.library_db


def close_db(error=None):
    for key in ("db", "library_db"):
        connection = g.pop(key, None)
        if connection is not None:
            connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)  # close the connections after every request
