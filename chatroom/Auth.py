from . import User
from . import db

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlite3 import Connection, Cursor, DatabaseError

blueprint = Blueprint('auth', __name__,url_prefix='/auth')

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        # create a new user
        username = request.form['username']
        pwd = request.form['pwd']
        new_user = User.User(username, pwd)
        # insert the newly created user into the db
        conn = db.get_db()
        try:
            cur = conn.execute('''
            INSERT INTO Users(username, password, pk_n, pk_e, pk_d)
            VALUES (?,?,?,?,?)''', [new_user.username, new_user.password, new_user.pub_key[0], new_user.pub_key[1], new_user.priv_key])
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
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['pwd']

        if (not username) or (not pwd):
            error = 'Username or password unspecified'
        else:
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute('SELECT user_id, username, password FROM Users WHERE username=?;', [username])

            user_id = None
            row = cur.fetchone()
            while row is not None:
                if row['password'] == pwd:
                    user_id = row['user_id']
                    # create a new session for this user
                    cur.execute('INSERT INTO Sessions(userref,login_tm) VALUES (?, CURRENT_TIMESTAMP)', [user_id])
                    conn.commit()
                    break;
                row = cur.fetchone()
            cur.close()
            if user_id is not None:
                return redirect(url_for('chat.home_user', user_id=user_id))
            error = 'Password incorrect'
            return render_template('login.html', error=error)
        if error is not None:
            print(error)
            # store error to be shown
            flash(error)
    return render_template('login.html', error=error)


