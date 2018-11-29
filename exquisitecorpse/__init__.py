import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.update(
        SECRET_KEY = os.environ.get("SECRET_KEY", default=None),
        SQLALCHEMY_DATABASE_URI = os.environ.get("SECRET_KEY", default="sqlite:///" + os.path.join(app.instance_path, 'database.sqlite'))
    )
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import corpse
    app.register_blueprint(corpse.bp)
    app.add_url_rule('/', endpoint='index')

    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found."

    return app
