import os

from flask import Flask, render_template

from . import (Auth, Chat, Msg)


def create_app(testing=None):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #        SECRET_KEY='dev')
    # if testing is None:
    #    app.config.from_pyfile('config.py', silent=True)
    # else:
    #    app.config.from_mapping(testing)
    app.register_blueprint(Auth.blueprint)
    app.register_blueprint(Chat.blueprint)
    app.register_blueprint(Msg.blueprint)

    print(app.url_map)
    return app


