import os

from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

from . import auth, corpse

from .db import db, migrate

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.update(
        SECRET_KEY = os.environ.get("SECRET_KEY", default=None),
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE", default="sqlite:///" + os.path.join(app.instance_path, 'database.sqlite')),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )
    if not app.config.get('SECRET_KEY'):
        print("No secret key!")
        raise ValueError("No secret key set for Flask application")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth.bp)

    app.register_blueprint(corpse.bp)
    app.add_url_rule('/', endpoint='index')

    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found."

    return app
