from . import db
from .models import *
from random import shuffle

ses = db.session

def player_join(sid, name, room):
    # Add player.
    player = Players(id=sid, username=name, code=room, ready=False)
    ses.add(player)

    # Add room if it doesn't exists.
    instance = Rooms.query.filter(Rooms.code==room).first()
    if not instance:
        game = Rooms(code=room)
        ses.add(game)

    ses.commit()

def player_leave(sid):
    # Removes player.
    room = Players.query.filter(Players.id==sid).first().code
    Players.query.filter(Players.id==sid).delete()


    # Removes room if it exists.
    instance = Players.query.filter(Players.code==room).first()
    if not instance:
            Rooms.query.filter(Rooms.code==room).delete()

    ses.commit()

def player_ready(sid):
    instance = Players.query.filter(Players.id==sid).first()
    instance.ready = not instance.ready
    ses.commit()

def unready_all_players(room):
    players = get_players(room)
    
    for player in players:
        player.ready = False

    ses.commit()

def is_room_ready (room):
    ready = True
    players = Players.query.filter(Players.code==room)
    for player in players:
        ready = player.ready and ready
    return ready

def get_player(sid):
    return Players.query.filter(Players.id==sid).first()

def get_players(room):
    return Players.query.filter(Players.code==room).all()

def get_players_string(room):
    li = []
    instance = Players.query.filter(Players.code==room).all()
    for player in instance:
        ready = '(READY)'if player.ready == True else '(NOT READY)'
        li.append(f'{player.username} {ready} {player.role}')
    return li

def get_room_state(room):
    return Rooms.query.filter(Rooms.code==room).first().game_state

def update_room_state(room, state):
    Rooms.query.filter(Rooms.code==room).first().game_state = state
    ses.commit()

def assign_roles(room):
    werewolf_num = 1
    seer_num = 1

    players = get_players(room)
    indices = list(range(len(players)))
    shuffle(indices)
    

    while werewolf_num > 0:
        players[indices.pop()].role = 'coxcomb'
        werewolf_num -= 1

    while seer_num > 0:
        players[indices.pop()].role = 'fortune teller'
        seer_num -= 1

    while len(indices) > 0:
        players[indices.pop()].role = 'villager'

    ses.commit()
