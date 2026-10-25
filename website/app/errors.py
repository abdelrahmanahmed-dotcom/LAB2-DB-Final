"""[R10] Friendly error pages: the user never sees a raw error or a stack trace."""
from flask import render_template
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)  # 404, 405, ...
    def http_error(error):
        message = error.name
        if error.code == 413:  # [Lab 3, Bonus] picture bigger than MAX_CONTENT_LENGTH
            message = "The picture is too big (2 MB at most)"
        return render_template("error.html", code=error.code, message=message), error.code

    @app.errorhandler(Exception)  # anything unexpected, e.g. MySQL is down
    def server_error(error):
        app.logger.exception(error)  # the details go to the log, not to the user
        return render_template("error.html", code=500, message="Something went wrong"), 500
