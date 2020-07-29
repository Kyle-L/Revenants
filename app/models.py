from . import db

class Rooms(db.Model):
    code = db.Column(db.String(4), primary_key=True)
    game_state = db.Column(db.String(24), unique=False, nullable=False, default='lobby')

class Players(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(24), unique=False, nullable=False, default=False)
    code = db.Column(db.String(4), unique=False, nullable=False, default=False)
    ready = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    role = db.Column(db.String(12), unique=False, nullable=False, default='villager')
    alive = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    marked = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    chosen = db.Column(db.String(24), unique=False, nullable=True)


class Characters(db.Model):
    username = db.Column(db.String(24), primary_key=True)
    code = db.Column(db.String(4), primary_key=True)
    prefix = db.Column(db.String(24), unique=False, nullable=False)
    first_name = db.Column(db.String(24), unique=False, nullable=False)
    last_name = db.Column(db.String(24), unique=False, nullable=False)
    pronouns = db.Column(db.String(24), unique=False, nullable=False)
    profession = db.Column(db.String(24), unique=False, nullable=False)