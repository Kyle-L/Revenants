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
            session['name'] = request.form.get('name').upper()
            session['room'] = request.form.get('room').upper()
        return redirect(url_for('.game'))
    return render_template('index.html')


@app.route('/game')
def game():
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
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

    print(f'{name} has joined room {room}')

    emit('update_players', {'players': get_players_string(room)}, room=room)


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

    print(f'{name} has left room {room}')

    emit('update_players', {'players': get_players_string(room)}, room=room)


@socketio.on('ready')
def ready(message):
    name = session.get('name')
    room = session.get('room')

    player_ready(request.sid)
    state = get_room_state(room)

    if state == 'night':
        print(True)
    elif state == 'day':
        print(True)
    elif state == 'lobby':
        emit('update_players', {
             'players': get_players_string(room)}, room=room)

    if is_room_ready(room):
        unready_all_players(room)

        if state == 'lobby':
            lobby_finished(room)
        elif state == 'setup':
            setup_finished(room)
        elif state == 'night':
            night_finished(room)
        elif state == 'day':
            day_finished(room)


def lobby_finished(room):
    print(f'Room {room} finished lobby.')

    assign_roles(room)
    update_room_state(room, 'setup')
    players = get_players(room)
    for player in players:
        payload = {
            'time': 10,
            'message': 'Game starting in...',
            'state': 'Set Up',
            'role': get_role_name(player.role),
            'role_description': get_role_description(player.role)
        }
        emit('start_setup', payload, room=player.id)


def setup_finished(room):
    print(f'Room {room} finished setup.')

    update_room_state(room, 'night')
    payload = {
        'time': 10,
        'message': 'Night starting in...',
        'state': 'Night'
    }
    emit('start_round', payload, room=room)


def night_finished(room):
    print(f'Room {room} finished night.')

    update_room_state(room, 'day')
    payload = {
        'time': 10,
        'message': 'Day starting in...',
        'state': 'Day'
    }
    emit('start_round', payload, room=room)


def day_finished(room):
    update_room_state(room, 'night')
    payload = {
        'time': 10,
        'message': 'Night starting in...',
        'state': 'Night'
    }
    emit('start_round', payload, room=room)


def end(room):
    print(True)
