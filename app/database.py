from . import db
from .models import *
from random import shuffle
from .helper import *
from .generator import *

ses = db.session


def player_join(sid: str, name: str, room: str):
    """Joins a player to a room (and creates a room if one doesn't exist).

    Args:
        sid (str): The session id of the player joining.
        name (str): The username of the player joining.
        room (str): The room code of the room the player is joining.
    """
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
    """Removes a player from a room (and destroys a room if it is empty).

    Args:
        sid (str): The session id of the player joining.
    """
    # Removes player.
    room = Players.query.filter(Players.id == sid).first().code
    Players.query.filter(Players.id == sid).delete()

    # Removes room if it exists.
    instance = Players.query.filter(Players.code == room).first()
    if not instance:
        Rooms.query.filter(Rooms.code == room).delete()

    ses.commit()


def player_ready(sid: str):
    """Marks a player as ready.

    Args:
        sid (str): the session id of the player.
    """
    instance = Players.query.filter(Players.id == sid).first()
    instance.ready = not instance.ready
    ses.commit()


def unready_all_players(room: str):
    """Marks all players as unready who belong to a specific room. 

    Args:
        room (str): The room code of the players being marked as unready.
    """
    players = get_players(room)

    for player in players:
        player.ready = False

    ses.commit()


def is_room_ready(room: str) -> bool:
    """Returns whether all players in a room are ready.

    Args:
        room (str): The room code of the room being checked.

    Returns:
        bool: Whether the room is ready or not.
    """
    ready = True
    players = Players.query.filter(Players.code == room)
    for player in players:
        if player.is_alive:
            ready = player.ready and ready
    return ready


def get_player(sid: str) -> Players:
    """Returns a player.

    Args:
        sid (str): The session id of the player.

    Returns:
        Players: A player
    """
    return Players.query.filter(Players.id == sid).first()


def get_player_from_name(name: str, room: str) -> Players:
    """Gets a player based on their username and room code.

    Args:
        name (str): A player's username.
        room (str): The room code of the player.

    Returns:
        Players: A player
    """
    return Players.query.filter(Players.username == name, Players.code == room).first()


def get_players(room: str):
    """Returns all players in a room

    Args:
        room (str): The room code of the players.

    Returns:
        Players: All of the players in a room.
    """
    return Players.query.filter(Players.code == room).all()


def update_player_chosen_player(sid: str, chosen_player: str):
    """Updates a player's chosen_player.

    Args:
        sid (str): The session id of the player.
        chosen_player (str): The id another player in the player's room.
    """
    get_player(sid).chosen_player = chosen_player

    ses.commit()


def update_player_alive(sid: str, is_alive: bool):
    """Updates a player's is_alive status.

    Args:
        sid (str): The session id of the player.
        is_alive (bool): Whether the player is alive or dead.
    """
    get_player(sid).is_alive = is_alive

    ses.commit()


def update_player_marked(sid: str, is_is_marked: bool):
    """Updates whether a player has been marked to be killed or not.

    Args:
        sid (str): The session id of the player.
        is_alive (bool): Whether the player is marked or not.
    """
    get_player(sid).is_marked = is_is_marked

    ses.commit()


def get_players_string_lobby(room: str) -> list:
    """Returns a list of strings representing the players and whether they are ready or not.

    Args:
        room (str): The room code of the players.

    Returns:
        list: A list of strings representing the players and whether they are ready or not.
    """
    li = []
    for player in get_players(room):
        ready = '(READY)'if player.ready == True else '(NOT READY)'
        li.append(f'{player.username} {ready}')
    return li


def get_players_string_win(room: str) -> list:
    """Returns a list of strings representing the players, their role, character name, and alive status.

    Args:
        room (str): The room code of the players.

    Returns:
        list: A list of strings representing the players, their role, character name, and alive status.
    """
    li = []
    for player in get_players(room):
        li.append(
            f'{player.character_name} ({player.username}) was a {get_role_name(player.role)} and {get_player_end_status(player.is_alive)}.')
    return li


def get_players_string(room: str, skip_id: str = "") -> list:
    """Returns a list of strings representing the players and their character name.

    Args:
        room (str): The room code of the players.
        skip_id (str, optional): A player to be skipped and not added to the list. Defaults to "".

    Returns:
        list: A list of strings representing the players and their character name.
    """
    li = []
    for player in get_players(room):
        if player.is_alive and not player.id == skip_id:
            li.append(f'{player.character_name} ({player.username})')
    return li


def get_player_string(sid: str) -> str:
    """Returns a string which represents a single player and their character name.

    Args:
        sid (str): The session id of the player.

    Returns:
        str: A string which represents a single player and their character name.
    """
    player = get_player(sid)
    return f'{player.character_name} ({player.username})'


def get_players_ids(room: str, skip_id: str = "") -> list:
    """Returns a list of the session ids of players in a room.

    Args:
        room (str): The room code of the players.
        skip_id (str, optional): A player to be skipped and not added to the list. Defaults to "".

    Returns:
        list: A list of the session ids of players in a room.
    """
    li = []
    for player in get_players(room):
        if player.is_alive and not player.id == skip_id:
            li.append(player.id)
    return li


def get_ready_count_string(room: str) -> str:
    """Returns a string representing how many players in a room are ready.

    Args:
        room (str): The room code of the players.

    Returns:
        str: A string representing how many players in a room are ready in the format '[ready]/[not ready]'.
    """
    player_count = 0
    ready_count = 0
    players = get_players(room)
    for player in players:
        if player.is_alive:
            player_count += 1
            if player.ready:
                ready_count += 1
    return f'{ready_count}/{player_count}'


def get_room_state(room: str) -> str:
    """Returns the state a room is currently in.

    Args:
        room (str): The room code of a room.

    Returns:
        str: The state of the room.
    """
    state = 'n/a'
    room = Rooms.query.filter(Rooms.code == room).first()
    return room.game_state if room else state


def update_room_state(room: str, state: str):
    """Updates the state a room is currently in.

    Args:
        room (str): The room code of the room being updated.
        state (str): The new state of the room.
    """
    Rooms.query.filter(Rooms.code == room).first().game_state = state.lower()
    ses.commit()


def assign_characters(room: str):
    """Assigns all players in a room a character.

    Args:
        room (str): The room code of the players being assigned a character.
    """
    players = get_players(room)
    for player in players:
        gender = generate_gender()
        first_name = generate_first_name(gender)
        last_name = generate_last_name()
        age = generate_age()

        player.character_name = f'{first_name} {last_name}'
        player.character_age = age

    ses.commit()


def assign_roles(room: str):
    """Assigns all players in a room a role.

    Args:
        room (str): The room code of the players being assigned a role.
    """
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
    """Gets the count of bad and good players in a room.

    Args:
        room (str): The room code of the room the count is coming from.

    Returns:
        str: The count of players in a bad role.
        str: The count of players in a good role.
    """
    count_antag = 0
    count_rest = 0
    players = get_players(room)
    for player in players:
        if player.is_alive:
            if player.role == 'antagonist':
                count_antag += 1
            else:
                count_rest += 1
    return count_antag, count_rest


def reset_players(room: str):
    """Resets alive, marked, and chosen player fields of all players in a room.

    Args:
        room (str): The room code of the players.
    """
    players = get_players(room)
    for player in players:
        player.is_alive = True
        player.is_marked = False
        player.chosen_player = ''
        player.ready = False

    ses.commit()
