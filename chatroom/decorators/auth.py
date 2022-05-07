from chatroom import db
from functools import wraps

from flask import g, url_for, redirect

# decorator to allow the operation iff the user is logged in to a session
def login_required(f):
    @wraps(f)
    def login_wrapper(*args, **kwargs):
        if 'user_id' in kwargs:
            # check for a session in the db
            cur = db.get_db().execute('''
                SELECT userref FROM Sessions WHERE userref = ?;''', [kwargs['user_id']])
            if cur.fetchone() is not None:
                print('session ok')
                return f(*args, **kwargs)
            print('session fail')
            return redirect(url_for('auth.login'))
    return login_wrapper