from . import db
from .models import *

ses = db.session

def player_join(name, room):
    # Add player.
    player = Players(username=name, code=room)
    ses.add(player)

    # Add room if it doesn't exists.
    instance = Games.query.filter(Games.code==room).first()
    if not instance:
        game = Games(code=room)
        ses.add(game)

    ses.commit()

def player_leave(name, room):
    # Removes player.
    Players.query.filter(Players.username==name).delete()

    # Removes room if it exists.
    instance = Players.query.filter(Players.code==room).first()
    if not instance:
            Games.query.filter(Games.code==room).delete()

    ses.commit()

def get_players(room):
    li = []
    instance = Players.query.filter(Players.code==room).all()
    for player in instance:
        li.append(player.username)
    return li
