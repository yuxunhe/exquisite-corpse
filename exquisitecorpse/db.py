import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# from exquisitecorpse import db

db = SQLAlchemy()
migrate = Migrate()

# TODO: Check username and password lengths to prevent overflow in database
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    limbs = db.relationship('Limb', backref='user', lazy=False)
    corpses = db.relationship('Corpse', backref='user', lazy=False)

# TODO: Check limb length
class Limb(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    corpse_id = db.Column(db.Integer, db.ForeignKey("corpse.id"))
    created = db.Column(db.TIMESTAMP, nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

class Corpse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    limbs = db.relationship('Limb', backref='corpse', lazy=False)
