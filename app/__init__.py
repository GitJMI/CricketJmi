from flask import Flask,render_template
from flask_cors import CORS
from app.config import Config

from app.extensions import db, migrate, jwt
from app.routes import register_routes
from app.sockets.socket import init_socket


def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes


    app.config.from_object(Config)


    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    register_routes(app)


    init_socket(app)

    @app.route("/")
    def index():
        return "backend is running"

    return app