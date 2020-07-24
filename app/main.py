import os
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio
from .firebase import db
from .helper import generate_room_code

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
            session['name'] = request.form.get('name')
            session['room'] = generate_room_code(4)
        elif request.form['action'] == 'join':
            session['name'] = request.form.get('name')
            session['room'] = request.form.get('room')
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
    room = session.get('room')
    join_room(room)

    # Adds a player to firestore.
    # If the room doesn't exist, it will also create it.
    db.collection(u'games').document(room).collection(u'players').document(session.get('name')).set({
        u'name': session.get('name'),
        u'character_name': ''
    })
    
    print('testing')

    # col = db.collection(u'games').document(room).collection(u'players').document().get()

    # for i in col:
    #     print(i)

    # emit('update_players', {'players': ''}, room=room)

@socketio.on('disconnect')
def left():
    room = session.get('room')
    leave_room(room)

    # Removes a player from firebase.
    db.collection(u'games').document(room).collection(u'players').document(session.get('name')).delete()

    # Removes the room from the database if there is no players.
    col = db.collection(u'games').document(room).collection(u'players').document().get()
    if col is None:
        db.collection(u'games').document(room).delete()
    else:
        emit('update_players', {'players': col}, room=room)

@socketio.on('start')
def text(message):
    print('start')
    room = session.get('room')
    emit('start_timer', {'time': 1000}, room=room)