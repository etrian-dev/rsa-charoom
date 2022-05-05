import os
import logging
from datetime import datetime

from flask import Flask, render_template

from . import (Admin, Auth, Chat, Msg, Search)
from . import db


def create_app(testing=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'chatroom.sqlite'),
        #EXPLAIN_TEMPLATE_LOADING=True,
    )

    # ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        try:
            os.makedirs(app.instance_path)
        except OSError:
            print(f"Failed creating instance directory at {app.instance_path}")
    
    # if testing is None:
    #    app.config.from_pyfile('config.py', silent=True)
    # else:
    #    app.config.from_mapping(testing)
    
    # setup logging
    logging.basicConfig(
        filename=os.path.join(app.instance_path, 'chatroom.log'),
        filemode='w',
        level=logging.DEBUG,
        encoding='utf-8')
    logging.info(f"Application launched at {datetime.now()}")

    app.register_blueprint(Auth.blueprint)
    app.register_blueprint(Chat.blueprint)
    app.register_blueprint(Msg.blueprint)
    app.register_blueprint(Search.blueprint)
    # admin urls
    app.register_blueprint(Admin.blueprint)

    # init the db
    db.init_app(app)

    return app


