from . import db

class Rooms(db.Model):
    code = db.Column(db.String(4), primary_key=True)
    game_state = db.Column(db.String(24), unique=False, nullable=False, default='lobby')


class Players(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(24), unique=False, nullable=False, default=False)
    code = db.Column(db.String(4), unique=False, nullable=False, default=False)
    ready = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    role = db.Column(db.String(12), unique=False, nullable=False, default='regular')
    is_alive = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    is_marked = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    chosen_player = db.Column(db.String(24), unique=False, nullable=True)
    character_name = db.Column(db.String(64), unique=False, nullable=True)
    character_age = db.Column(db.Integer, unique=False, nullable=True)
