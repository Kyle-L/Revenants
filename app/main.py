import os
import operator
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio
from .helper import *
from .database import *

MIN_PLAYER_COUNT = 4

app = Blueprint('main', __name__)


@app.route('/how-to-play')
def how_to_play():
    return render_template('how-to-play.html')


@app.route('/license')
def license():
    return render_template('license.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['action'] == 'host':
            session['name'] = request.form.get('name').upper()
            session['room'] = generate_room_code(4).upper()
        elif request.form['action'] == 'join':
            name = request.form.get('name').upper()
            room = request.form.get('room').upper()

            # If there is already a player with that name, redirect to index.
            state = get_room_state(room)
            if get_player_from_name(name, room) or (state != 'n/a' and state != 'lobby'):
                return render_template('index.html', error_message='blah')

            session['name'] = name
            session['room'] = room

        return redirect(url_for('.game'))
    return render_template('index.html')


@app.route('/game')
def game():
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))

    # If there is already a player with that name, redirect to index.
    state = get_room_state(room)
    if get_player_from_name(name, room) or (state != 'n/a' and state != 'lobby'):
        return redirect(url_for('.index'))

    return render_template('game.html', name=name, room=room)


@socketio.on('join')
def joined(data):
    """ Called when a client connects.
    """

    # Gets the player's name and room.
    name = session.get('name')
    room = session.get('room')

    # Adds a player to the socketio room session.
    join_room(room)

    # Adds a player from the database.
    player_join(request.sid, name, room)

    print(f'[{room}] {name} joined.')

    emit('update_players', {
         'players': get_players_string_lobby(room)}, room=room)


@socketio.on('disconnect')
def left():
    """ Called when a client disconnects.
    """

    # Gets the player's name and room.
    name = session.get('name')
    room = session.get('room')

    player = get_player(request.sid)

    # Removes a player to the socketio room session.
    leave_room(room)

    # Removes a player from the database.
    player_leave(request.sid)

    print(f'[{room}] {name} left.')

    emit('update_players', {
         'players': get_players_string_lobby(room)}, room=room)

    if len(get_players(room)) < MIN_PLAYER_COUNT and get_room_state(room) != 'lobby':
        return_to_lobby(room)


@socketio.on('ready')
def ready(data):
    """ Called when a client clicks the ready button.
    """

    # Gets the player's name and room.
    name = session.get('name')
    room = session.get('room')

    player_ready(request.sid)
    state = get_room_state(room)
    if state == 'lobby':
        emit('update_players', {
             'players': get_players_string_lobby(room)}, room=room)
    elif state == 'day' or state == 'night':
        if data['chosen_player']:
            update_player_chosen_player(request.sid, data['chosen_player'])
        emit('update_ready', {'players': get_ready_count_string(
            room) + ' are ready.'}, room=room)
    else:
        emit('update_ready', {'players': get_ready_count_string(
            room) + ' are ready.'}, room=room)

    if is_room_ready(room) and len(get_players(room)) >= MIN_PLAYER_COUNT:
        unready_all_players(room)

        if state == 'lobby':
            start_setup(room)
        elif state == 'setup':
            start_round(room, 'Night', False)
        elif state == 'night':
            process_choices_night(room)
        elif state == 'night-results':
            start_round(room, 'Day', True)
        elif state == 'day':
            process_choices_day(room)
        elif state == 'day-results':
            start_round(room, 'Night', False)
        elif state == 'win':
            return_to_lobby(room)


def return_to_lobby(room):
    """ Returns the game to the lobby state.
    """

    print(f'[{room}] Returning to lobby.')

    reset_game(room)
    update_room_state(room, 'lobby')
    payload = {
        'time': 5,
        'message': 'Returning to lobby in...',
        'state_html': 'lobby',
        'state_name': '',
        'alive': True
    }
    emit('start_lobby', payload, room=room)


def start_setup(room):
    """ Starts the game's setup state.
    """

    print(f'[{room}] Starting setup.')

    assign_roles(room)
    assign_characters(room)
    update_room_state(room, 'setup')
    players = get_players(room)
    for player in players:
        payload = {
            'time': 5,
            'message': 'Game starting in...',
            'state_html': 'setup',
            'state_name': 'Set Up',
            'name': player.character_name,
            'age': player.character_age,
            'role': get_role_name(player.role),
            'role_description': get_role_description(player.role),
            'alive': player.is_alive
        }
        emit('start_setup', payload, room=player.id)


def start_round(room, round_name, is_day):
    print(f'[{room}] Starting {round_name.lower()}.')

    update_room_state(room, round_name.lower())

    players = get_players(room)
    for player in players:
        payload = {
            'time': 5,
            'message': f'{round_name} starting in...',
            'state_html': 'round',
            'state_name': round_name,
            'role_action': get_role_action(player.role, is_day),
            'players_names': get_players_string(room, player.id),
            'players_ids': get_players_ids(room, player.id),
            'alive': player.is_alive

        }
        emit('start_round', payload, room=player.id)


def process_choices_night(room):
    """ Processes the choices that were made by players at night.
    """

    print(f'[{room}] Showing night results.')

    result_general_list = []
    result_private_dict = {}

    protect_dict = {}

    players = get_players(room)

    # The first loop through the players' list will process actions that should happen 1st.
    for player in players:
        if player.role == 'antagonist':
            # Marks the player to be killed.
            update_player_marked(player.chosen_player, True)
            # Updates the result list.
            result_general_list.append(f'{get_player_string(player.chosen_player)} was attacked.')

        elif player.role == 'regular':
            # Update the dictionary representing how many regulars are protecting someone.
            if player.chosen_player in protect_dict:
                protect_dict[player.chosen_player] += 1
            else:
                protect_dict[player.chosen_player] = 1

        elif player.role == 'prophet':
            # Update the personal result dict for the player who is a prophet.
            result_private_dict[player.id] = [f'{get_player_string(player.chosen_player)} is a {get_role_name(get_player(player.chosen_player).role)}.']

    # Unmark the protected player if they've been marked by the antagonist.
    player_protected = max(protect_dict.items(), key=operator.itemgetter(1))[0]
    if protect_dict[player_protected] > 1:
        update_player_marked(player_protected, False)
        result_general_list.append(f'{get_player_string(player_protected)} was protected.')

    # The second loop through the players' list will process actions that should happen 2nd.
    for player in players:
        if player.role == 'doctor':
            update_player_marked(player.chosen_player, False)
            result_general_list.append(f'{get_player_string(player.chosen_player)} was healed.')

    # The final loop through the players' list will determine who survives the night.
    for player in players:
        if (player.is_marked):
            update_player_alive(player.id, False)
            result_general_list.append(f'{get_player_string(player.id)} died from their injuries.')
            result_private_dict[player.id] = ['You have died from your injuries.']

    # Determines if the game was won by a team or the next round should start.
    process_win_conditions(room, players, 'night-results', 'Night', result_general_list, result_private_dict)


def process_choices_day(room: str):
    """ Processes the choices that were made by players during the day.
    """

    print(f'[{room}] Showing day results.')

    result_general_list = []
    result_private_dict = {}

    kill_dict = {}

    players = get_players(room)

    # The loops through the players to determine how wants to kill who.
    for player in players:
        if player.chosen_player in kill_dict:
            kill_dict[player.chosen_player] += 1
        else:
            kill_dict[player.chosen_player] = 1

    # Grab the player from the dict with the most votes and mark them as dead.
    player_killed = max(kill_dict.items(), key=operator.itemgetter(1))[0]
    update_player_alive(player_killed, False)
    result_general_list = [f'{get_player_string(player_killed)} was killed.']

    # Determines if the game was won by a team or the next round should start.
    process_win_conditions(room, players, 'day-results', 'Day', result_general_list, result_private_dict)


def process_win_conditions(room, players, state, state_name, result_general_list, result_private_dict):
    count_antag, count_rest = get_role_count(room)
    if count_antag >= count_rest:
        update_room_state(room, 'win')
        payload = {
            'time': 5,
            'message': f'{state_name} results showing in...',
            'state_html': 'win',
            'state_name': get_role_name('antagonist').capitalize() + 's Win!',
            'win_message': f'{get_win_message(True)}',
            'players': get_players_string_win(room)
        }

        emit('start_win', payload, room=room)
        reset_game(room)
    elif count_antag == 0:
        update_room_state(room, 'win')
        payload = {
            'time': 5,
            'message': f'{state_name} results showing in...',
            'state_html': 'win',
            'state_name': get_role_name('regular').capitalize() + 's Win!',
            'win_message': f'{get_win_message(False)}',
            'players': get_players_string_win(room)
        }

        emit('start_win', payload, room=room)
        reset_game(room)
    else:
        update_room_state(room, state)

        for player in players:
            payload = {
                'time': 5,
                'message': f'{state_name} results showing in...',
                'state_html': 'results',
                'state_name': f'{state_name} Results',
                'results_general': result_general_list,
                'results_private': result_private_dict[player.id] if player.id in result_private_dict else [],
                'alive': player.is_alive
            }

            emit('start_results', payload, room=player.id)


def reset_game(room: str):
    reset_players(room)
    emit('update_players', {
         'players': get_players_string_lobby(room)}, room=room)
