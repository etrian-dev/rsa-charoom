from . import User
from . import db

from chatroom.decorators.auth import login_required

from sqlite3 import Connection, Cursor, DatabaseError
from time import time_ns

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

blueprint = Blueprint('auth', __name__,url_prefix='/auth')

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    '''Register a new user.
    '''
    error = None
    if request.method == 'POST':
        # create a new user
        username = request.form['username']
        pwd = request.form['pwd']
        new_user = User.User(username, pwd)
        # insert the newly created user into the db
        conn = db.get_db()
        try:
            pk_n_bytes = new_user.pub_key[0].to_bytes(new_user.pub_key[0].bit_length() // 8 + 1,byteorder='big')
            pk_e_bytes = new_user.pub_key[1].to_bytes(new_user.pub_key[1].bit_length() // 8 + 1,byteorder='big')
            pk_d_bytes = new_user.priv_key.to_bytes(new_user.priv_key.bit_length() // 8 + 1,byteorder='big')
            cur = conn.execute('''
            INSERT INTO Users(username, password, pk_n, pk_e, pk_d)
            VALUES (?,?,?,?,?)''', [new_user.username, new_user.password, pk_n_bytes, pk_e_bytes, pk_d_bytes])
            # gets the rowid of the last row, which is the same as the new user_id
            # iff user_id is an integer primary key with autoincrement
            new_user.user_id = cur.lastrowid
        except DatabaseError:
            error = 'Insert failed'
            conn.rollback()
            return render_template('register.html',error=error)
        conn.commit()
        print('Created new user:', new_user, sep='\n')
        return redirect(url_for('chat.home_user', user_id=new_user.user_id))
    # display the registration form
    return render_template('register.html',error=error)

@blueprint.route('/', methods=['GET'])
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Login into user profile.
    '''
    error = None
    # get login data to authenticate user
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['pwd']

        if (not username) or (not pwd):
            error = 'Username or password unspecified'
        else:
            conn = db.get_db()
            cur = conn.execute('''
                SELECT user_id, username, password 
                FROM Users 
                WHERE username=?;''', [username])

            user_id = None
            row = cur.fetchone()
            while row is not None:
                if row['password'] == pwd:
                    user_id = row['user_id']

                    # create a session for this user
                    cur.execute('''
                        INSERT INTO Sessions(userref, login_tm)
                        VALUES (?,?)''', [user_id, time_ns()])
                    conn.commit()
                    break
                row = cur.fetchone()
            cur.close()
            # User found: redirect to its own chats page
            if user_id is not None:
                return redirect(url_for('chat.home_user', user_id=user_id))
            error = 'Password incorrect or user inexistent'
        if error is not None:
            # store error to be shown
            flash(error)
    return render_template('login.html', error=error)

@blueprint.route('/logout/<int:user_id>', methods=['GET'])
@login_required
def logout(user_id: int):
    conn = db.get_db()
    cur = conn.execute('''
        SELECT * FROM Sessions WHERE userref = ?;''', [user_id])
    if cur.fetchone() is not None:
        # delete the user session if present
        cur.execute('''
            DELETE FROM Sessions WHERE userref = ?;''', [user_id])
        conn.commit()
    return redirect(url_for('auth.login'))