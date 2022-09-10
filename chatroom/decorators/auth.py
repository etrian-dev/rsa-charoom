from chatroom import db
from functools import wraps

from flask import g, url_for, redirect, session

# decorator to allow the operation iff the user is logged in to a session
def login_required(fn):
    @wraps(fn)
    def login_wrapper(*args, **kwargs):
        if 'user_id' in session:
            # check for a session in the db
            cur = db.get_db().execute('''
                SELECT userref 
                FROM Sessions 
                WHERE userref = ?;''', [session['user_id']])
            row = cur.fetchone()
            print('user is', row['userref'])
            if row is not None:
                print('session ok')
                return fn(*args, **kwargs)
        print('session fail')
        return redirect(url_for('auth.login'))
    return login_wrapper
