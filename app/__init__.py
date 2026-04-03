from flask import Flask,render_template
from app.config import Config

from app.extensions import db, migrate, jwt
from app.routes import register_routes
from app.sockets.socket import init_socket


def create_app():
    app = Flask(__name__)


    app.config.from_object(Config)


    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    register_routes(app)


    init_socket(app)

    @app.route("/")
    def index():
        return render_template("backend is Running")

    return app