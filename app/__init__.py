import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    # blueprint for non-auth parts of app
    from .main import app as app_blueprint
    app.register_blueprint(app_blueprint)

    from .errors import error as error_blueprint
    app.register_blueprint(error_blueprint)

    return app