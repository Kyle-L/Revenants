from . import db
from .models import *
from random import shuffle
from .helper import *

ses = db.session


def player_join(sid: str, name: str, room: str):
    # Add player.
    player = Players(id=sid, username=name, code=room, ready=False)
    ses.add(player)

    # Add room if it doesn't exists.
    instance = Rooms.query.filter(Rooms.code == room).first()
    if not instance:
        game = Rooms(code=room)
        ses.add(game)

    ses.commit()


def player_leave(sid: str):
    # Removes player.
    room = Players.query.filter(Players.id == sid).first().code
    Players.query.filter(Players.id == sid).delete()

    # Removes room if it exists.
    instance = Players.query.filter(Players.code == room).first()
    if not instance:
        Rooms.query.filter(Rooms.code == room).delete()

    ses.commit()


def player_ready(sid: str):
    instance = Players.query.filter(Players.id == sid).first()
    instance.ready = not instance.ready
    ses.commit()


def unready_all_players(room: str):
    players = get_players(room)

    for player in players:
        player.ready = False

    ses.commit()


def is_room_ready(room: str) -> bool:
    ready = True
    players = Players.query.filter(Players.code == room)
    for player in players:
        ready = player.ready and ready
    return ready


def get_player(sid: str):
    return Players.query.filter(Players.id == sid).first()


def get_players(room: str):
    return Players.query.filter(Players.code == room).all()


def get_players_string(room: str) -> list:
    li = []
    instance = Players.query.filter(Players.code == room).all()
    for player in instance:
        ready = '(READY)'if player.ready == True else '(NOT READY)'
        li.append(f'{player.username} {ready} {player.role}')
    return li


def get_room_state(room: str):
    return Rooms.query.filter(Rooms.code == room).first().game_state


def update_room_state(room: str, state: str):
    Rooms.query.filter(Rooms.code == room).first().game_state = state.lower()
    ses.commit()


def assign_roles(room: str):
    werewolf_num = 1
    prophet_num = 1

    players = get_players(room)
    indices = list(range(len(players)))
    shuffle(indices)

    while werewolf_num > 0:
        players[indices.pop()].role = 'antagonist'
        werewolf_num -= 1

    while prophet_num > 0:
        players[indices.pop()].role = 'prophet'
        prophet_num -= 1

    while len(indices) > 0:
        players[indices.pop()].role = 'regular'

    ses.commit()
