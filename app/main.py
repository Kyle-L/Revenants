import os
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio
from .helper import *
from .database import *

app = Blueprint('main', __name__)

# route and function to handle the license page


@app.route('/how-to-play')
def how_to_play():
    return render_template('how-to-play.html')

# route and function to handle the license page


@app.route('/license')
def license():
    return render_template('license.html')

# TODO: Add error checking for names and rooms.


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
def joined(message):
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
def ready(message):
    name = session.get('name')
    room = session.get('room')

    player_ready(request.sid)
    state = get_room_state(room)

    if state == 'lobby':
        emit('update_players', {'players': get_players_string_lobby(room)}, room=room)
    else:
        emit('update_done', {'players': get_ready_count_string(room) + ' are ready.'}, room=room)

    if is_room_ready(room):
        unready_all_players(room)

        if state == 'lobby':
            start_setup(room)
        elif state == 'setup':
            start_night(room)
        elif state == 'night':
            process_choices_night(room)
        elif state == 'night-results':
            start_day(room)
        elif state == 'day':
            process_choices_day(room)
        elif state == 'day-results':
            start_night(room)


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
        }
        emit('start_setup', payload, room=player.id)


def start_day(room):
    print(f'[{room}] Starting day.')

    update_room_state(room, 'day')
    payload = {
        'time': 5,
        'message': 'Day starting in...',
        'state_html': 'round',
        'state_name': 'Day',
        'players': get_players_string(room),
    }
    emit('start_round', payload, room=room)


def start_night(room):
    print(f'[{room}] Starting night.')

    update_room_state(room, 'night')
    payload = {
        'time': 5,
        'message': 'Night starting in...',
        'state_html': 'round',
        'state_name': 'Night',
        'players': get_players_string(room),
    }
    emit('start_round', payload, room=room)

def end(room):
    print(True)

def process_choices_night(room):
    print(f'[{room}] Showing night results.')

    update_room_state(room, 'night-results')

    players = get_players(room)
    for player in players:
        payload = {
            'time': 5,
            'message': 'Night results showing in...',
            'state_html': 'results',
            'state_name': 'Night Results',
            'results': 'TODO: ADD FOR EACH PERSON - Night'
        }
    emit('results', payload, room=room)

def process_choices_day(room):
    print(f'[{room}] Showing day results.')

    update_room_state(room, 'day-results')

    players = get_players(room)
    for player in players:
        payload = {
            'time': 5,
            'message': 'Day results showing in...',
            'state_html': 'results',
            'state_name': 'Day Results',
            'results': 'TODO: ADD FOR EACH PERSON - Day'
        }
    emit('results', payload, room=room)