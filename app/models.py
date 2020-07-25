from . import db

class Games(db.Model):
    code = db.Column(db.String(4), primary_key=True)

class Players(db.Model):
    username = db.Column(db.String(24), primary_key=True)
    code = db.Column(db.String(4), primary_key=True)
    ready = db.Column(db.Boolean, unique=False, nullable=False)
    first_name = db.Column(db.String(24), unique=False, nullable=True)
    last_name = db.Column(db.String(24), unique=False, nullable=True)
    role = db.Column(db.String(12), unique=False, nullable=True)

class Weapons(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(12), unique=True, nullable=False)
    action = db.Column(db.String(12), unique=True, nullable=False)

class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(24), unique=True, nullable=False)
    description = db.Column(db.String(), unique=True, nullable=False)