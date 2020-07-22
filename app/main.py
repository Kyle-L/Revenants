import os
from flask import Blueprint, render_template, request
from flask_socketio import SocketIO, emit
from . import socketio

app = Blueprint('main', __name__)

# route and function to handle the home page
@app.route('/')
def index():
    return render_template('index.html')

# route and function to handle the about page
@app.route('/about')
def about():
    return render_template('about.html')

# route and function to handle the license page
@app.route('/license')
def license():
    return render_template('license.html')

@socketio.on('status')
def handle_source(json_data):
    socketio.emit('status', {'msg': 'Someone accessed the about page'})
