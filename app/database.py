from . import db
from .models import *

ses = db.session

def player_join(name, room):
    # Add player.
    player = Players(username=name, code=room, ready=False)
    ses.add(player)

    # Add room if it doesn't exists.
    instance = Games.query.filter(Games.code==room).first()
    if not instance:
        game = Games(code=room)
        ses.add(game)

    ses.commit()

def player_leave(name, room):
    # Removes player.
    Players.query.filter(Players.username==name, Players.code==room).delete()

    # Removes room if it exists.
    instance = Players.query.filter(Players.code==room).first()
    if not instance:
            Games.query.filter(Games.code==room).delete()

    ses.commit()

def player_ready(name, room):
    instance = Players.query.filter(Players.username==name, Players.code==room).first()
    instance.ready = not instance.ready
    ses.commit()

def is_room_ready (room):
    ready = True
    players = Players.query.filter(Players.code==room)
    for player in players:
        ready = player.ready and ready
    return ready

def get_players(room):
    li = []
    instance = Players.query.filter(Players.code==room).all()
    for player in instance:
        ready = '(READY)'if player.ready == True else '(NOT READY)'
        li.append(f'{player.username} {ready}')
    return li
