import os
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio
from .helper import generate_room_code
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
    name = session.get('name')
    room = session.get('room')
    join_room(room)

    player_join(name, room)
    
    print(get_players(room))

    emit('update_players', {'players': get_players(room)}, room=room)

@socketio.on('disconnect')
def left():
    name = session.get('name')
    room = session.get('room')
    leave_room(room)

    # Removes a player from firebase.
    player_leave(name, room)
    
    emit('update_players', {'players': get_players(room)}, room=room)


@socketio.on('ready')
def text(message):
    print('start')
    name = session.get('name')
    room = session.get('room')

    player_ready(name, room)

    emit('update_players', {'players': get_players(room)}, room=room)
    if is_room_ready(room):
        emit('start_timer', {'time': 10, 'message': 'Starting in...'}, room=room)
