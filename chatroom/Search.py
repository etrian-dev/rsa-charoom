from . import db
from . import Msg

from time import time
from datetime import datetime
from sqlite3 import Connection, Cursor, DatabaseError
from json import dumps
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask.json import jsonify

blueprint = Blueprint('search', __name__, url_prefix='/search')


@blueprint.route('/', methods=['GET'])
def search_user():
    '''This method allows searching for users in the database.

    It receives a GET request with an URL like
    /search/?user=<str>, where the string may be empty (no matches in that case).
    The function returns a json array of objects
    { "user_id": <uid>, "username": <user> } whose username has a prefix 
    equal to the argument of the query. If the match is in the middle of the string
    that user is not added to the array.
    '''
    logging.debug(f"search query: {request.args}")
    matching_users = []
    # Does not match any user if the search query is empty
    if request.method == 'GET' and 'user' in request.args and len(request.args['user']) > 0 :
        query = request.args['user']
     
        db_conn = db.get_db()
        
        try:
            cursor = db_conn.execute('''
	    SELECT user_id, username
	    FROM Users
	    WHERE username LIKE ?
	    ORDER BY username DESC;
	    ''', [query + "%"])

            for row in cursor.fetchall():
                matching_users.append({
                    "user_id": row['user_id'],
                    "username": row['username']
                })
        except DatabaseError as err:
            print('SQLite error: %s' % (' '.join(err.args)))
            print("Exception class is: ", err.__class__)
    logging.debug(f"{len(matching_users)} mathches found: {matching_users}")
    return jsonify(matching_users)
