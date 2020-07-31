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
        ses.add(game, 'lobby')

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
        if player.alive:
            ready = player.ready and ready
    return ready


def get_player(sid: str):
    return Players.query.filter(Players.id == sid).first()

def get_player_from_name(name: str, room: str):
    return Players.query.filter(Players.username == name, Players.code==room).first()

def get_players(room: str):
    return Players.query.filter(Players.code == room).all()


def update_player_chosen(sid: str, chosen:str):
    get_player(sid).chosen = chosen

    ses.commit()

def update_player_alive(room: str, name:str, is_alive: bool):
    get_player_from_name(name, room).alive = is_alive

    ses.commit()

def update_player_marked(room: str, name:str, is_marked: bool):
    get_player_from_name(name, room).marked = is_marked

    ses.commit()

def get_players_string_lobby(room: str) -> list:
    li = []
    instance = Players.query.filter(Players.code == room).all()
    for player in instance:
        ready = '(READY)'if player.ready == True else '(NOT READY)'
        li.append(f'{player.username} {ready}')
    return li

def get_players_string(room: str, skip_id: str="") -> list:
    li = []
    instance = Players.query.filter(Players.code == room).all()
    for player in instance:
        if player.alive and not player.id == skip_id:
            li.append(f'{player.username}')
    return li

def get_ready_count_string(room: str) -> str:
    player_count = 0
    ready_count = 0
    players = get_players(room)
    for player in players:
        if player.alive:
            player_count += 1
            if player.ready: 
                ready_count += 1
    return f'{ready_count}/{player_count}'


def get_room_state(room: str):
    state = 'n/a'
    room = Rooms.query.filter(Rooms.code == room).first()
    return room.game_state if room else state


def update_room_state(room: str, state: str):
    Rooms.query.filter(Rooms.code == room).first().game_state = state.lower()
    ses.commit()


def assign_roles(room: str):
    antag_num = 1
    prophet_num = 1

    players = get_players(room)
    indices = list(range(len(players)))
    shuffle(indices)

    while antag_num > 0:
        players[indices.pop()].role = 'antagonist'
        antag_num -= 1

    while prophet_num > 0:
        players[indices.pop()].role = 'prophet'
        prophet_num -= 1

    while len(indices) > 0:
        players[indices.pop()].role = 'regular'

    ses.commit()

def get_role_count(room: str):
    count_antag = 0
    count_rest = 0
    players = get_players(room)
    for player in players:
        if player.alive:
            if player.role == 'antagonist':
                count_antag += 1
            else:
                count_rest += 1
    return count_antag, count_rest
    
def reset_players(room: str):
    players = get_players(room)
    for player in players:
        player.alive = True
        player.marked = False
        player.chosen = ''
        player.ready = False
    
    ses.commit()