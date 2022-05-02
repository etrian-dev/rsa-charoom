from . import db
from . import Msg

from time import time
from datetime import datetime
from sqlite3 import Connection, Cursor, DatabaseError
from json import dumps

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask.json import jsonify

blueprint = Blueprint('search', __name__, url_prefix='/search')


@blueprint.route('/', methods=['GET'])
def search_user():
    matching_users = []
    if request.method == 'GET':
        query = request.args['user']
        print(query)
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
            print(len(matching_users))
        except DatabaseError as err:
            print('SQLite error: %s' % (' '.join(err.args)))
            print("Exception class is: ", err.__class__)
        return jsonify(matching_users)
