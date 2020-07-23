import os
from flask import Blueprint, redirect, render_template, url_for, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socketio

app = Blueprint('main', __name__)

# route and function to handle the home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# route and function to handle the license page
@app.route('/license')
def license():
    return render_template('license.html')






@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['name'] = request.form.get('name')
        session['room'] = request.form.get('room')
        return redirect(url_for('.game'))
    # elif request.method == 'GET':
    #     form.name.data = session.get('name', '')
    #     form.room.data = session.get('room', '')
    return render_template('index.html')

@app.route('/game')
def game():
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('game.html', name=name, room=room)

@socketio.on('joined', namespace='/game')
def joined(message):
    print('testing')
    room = session.get('room')
    join_room(room)
    emit('notify_join', {'username': session.get('name')}, room=room)


@socketio.on('text', namespace='/game')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/game')
def left(message):
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)


@socketio.on('status')
def text(message):
    print('testing2')