from flask import Flask
from flask_cors import CORS 

from app.webhook.routes import webhook
from app.extensions import init_app,mongo


# Creating our flask app
def create_app():

    app = Flask(__name__)
    CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_app(app)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
