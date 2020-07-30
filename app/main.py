import os, operator
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio
from .helper import *
from .database import *

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
    # Gets the player's name and room.
    name = session.get('name')
    room = session.get('room')

    # Adds a player to the socketio room session.
    join_room(room)

    # Adds a player from the database.
    player_join(request.sid, name, room)

    print(f'[{room}] {name} joined.')

    emit('update_players', {'players': get_players_string_lobby(room)}, room=room)


@socketio.on('disconnect')
def left():
    # Gets the player's name and room.
    name = session.get('name')
    room = session.get('room')

    player = get_player(request.sid)

    # Removes a player to the socketio room session.
    leave_room(room)

    # Removes a player from the database.
    player_leave(request.sid)

    print(f'[{room}] {name} left.')

    emit('update_players', {'players': get_players_string_lobby(room)}, room=room)


@socketio.on('ready')
def ready(data):
    name = session.get('name')
    room = session.get('room')

    player_ready(request.sid)
    state = get_room_state(room)
    if state == 'lobby':
        emit('update_players', {'players': get_players_string_lobby(room)}, room=room)
    elif state == 'day' or state == 'night':
        if data['chosen_player']:
            update_player_chosen(request.sid, data['chosen_player'])
        emit('update_done', {'players': get_ready_count_string(room) + ' are ready.'}, room=room)
    else:
        emit('update_done', {'players': get_ready_count_string(room) + ' are ready.'}, room=room)


    if is_room_ready(room):
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
            start_round(room, 'Night')


def start_setup(room):
    print(f'[{room}] Starting setup.')

    assign_roles(room)
    update_room_state(room, 'setup')
    players = get_players(room)
    for player in players:
        payload = {
            'time': 5,
            'message': 'Game starting in...',
            'state_html': 'setup',
            'state_name': 'Set Up',
            'role': get_role_name(player.role),
            'role_description': get_role_description(player.role),
            'alive': player.alive
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
            'players': get_players_string(room),
            'alive': player.alive
            
        }
        emit('start_round', payload, room=player.id)


def process_choices_night(room):
    print(f'[{room}] Showing night results.')

    result_str_general = []
    result_str_private = []

    players = get_players(room)
    for player in players:
        if player.role == 'antagonist':
            update_player_marked(room, player.chosen, True)
            result_str_general.append(f'{player.chosen} was attacked.')

    for player in players:
        if player.role == 'doctor':
            update_player_marked(room, player.chosen, False)
            result_str_general.append(f'{player.chosen} was healed.')

    for player in players:
        if (player.marked):
            update_player_alive(player.code, player.username, False)
            result_str_general.append(f'{player.username} died.')
    
    process_win_conditions(room, players, 'night-results', 'Night', result_str_general, result_str_private)


def process_choices_day(room: str):
    print(f'[{room}] Showing day results.')

    result_str_general = []
    result_str_private = []

    player_dict = {}

    players = get_players(room)
    for player in players:
        if player.chosen in player_dict:
            player_dict[player.chosen] += 1
        else:
            player_dict[player.chosen] = 1
    
    player_killed = max(player_dict.items(), key=operator.itemgetter(1))[0]
    update_player_alive(room, player_killed, False)
    result_str_general.append(f'{player_killed} was killed.')

    process_win_conditions(room, players, 'day-results', 'Day', result_str_general, result_str_private)

def process_win_conditions(room, players, state, state_name, message_public, message_private):
    count_antag, count_rest = get_role_count(room)
    if count_antag >= count_rest:
        update_room_state(room, 'lobby')
        reset_game(room)
        payload = {
            'time': 5,
            'message': f'{state_name} results showing in...',
            'state_html': 'lobby',
            'state_name': f'{state_name} Results',
            'win': True,
            'win_message': 'Revenants won the game.'
        }

        emit('results', payload, room=room)
    elif count_antag == 0:
        update_room_state(room, 'lobby')
        reset_game(room)
        payload = {
            'time': 5,
            'message': f'{state_name} results showing in...',
            'state_html': 'lobby',
            'state_name': f'{state_name} Results',
            'win': True,
            'win_message': 'Villagers won the game.'
        }

        emit('results', payload, room=room)
    else:
        update_room_state(room, state)

        for player in players:

            payload = {
                'time': 5,
                'message': f'{state_name} results showing in...',
                'state_html': 'results',
                'state_name': f'{state_name} Results',
                'results': message_public,
                'results_private': message_private,
                'alive': player.alive
            }

            emit('results', payload, room=player.id)

def reset_game(room: str):
    reset_players(room)
    emit('update_players', {'players': get_players_string_lobby(room)}, room=room)