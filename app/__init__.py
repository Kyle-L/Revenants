import os
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

def create_app():
    
    app.config['SECRET_KEY'] = 'secret-key-goes-here'


    # blueprint for non-auth parts of app
    from .main import app as app_blueprint
    app.register_blueprint(app_blueprint)

    from .errors import error as error_blueprint
    app.register_blueprint(error_blueprint)

    return app, socketio