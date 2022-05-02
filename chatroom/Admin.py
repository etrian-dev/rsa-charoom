from . import db

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlite3 import Connection, Cursor, DatabaseError

blueprint = Blueprint('admin', __name__,url_prefix='/admin')

@blueprint.route('/', methods=['GET'])
@blueprint.route('/users', methods=['GET'])
def show_users():
    '''Shows all users in the application'''
    conn = db.get_db()
    try:
        cursor = conn.execute('''
        SELECT * FROM Users''')
        all_users = dict()
        for user in cursor.fetchall():
            all_users[user['user_id']] = {
                "username": user['username'],
                "password": user['password']}
        return render_template('admin_console.html', all_users=all_users)
    except DatabaseError:
        return "DB error"