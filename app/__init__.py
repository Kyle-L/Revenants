import os
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

def create_app():
    from .models import Rooms

    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    if 'DATABASE_URL' in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    # Drops the database if it already exists.
    db.drop_all()

    # Create the database.
    db.create_all()

    # blueprint for non-auth parts of app
    from .main import app as app_blueprint
    app.register_blueprint(app_blueprint)

    from .errors import error as error_blueprint
    app.register_blueprint(error_blueprint)

    return app, socketio