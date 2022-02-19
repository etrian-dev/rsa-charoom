from . import User
from . import db

# Create users
users = dict()
user_map = dict() # reverse lookup from username to user ID(s)
for u in ['mario', 'luigi', 'chiara' , 'jacopo', 'andrea', 'beatrice']:
    new_user = User.User(u, 'pwd')
    print('Created new user:', new_user, sep='\n')
    users[new_user] = False # not logged
    if u not in user_map.keys():
        user_map[u] = [new_user.user_id]
    else:
        user_map[u].append(new_user.user_id)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

blueprint = Blueprint('auth', __name__,url_prefix='/auth')

@blueprint.route('/', methods=['GET'])
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    print(request, request.get_data(as_text=True), sep='\n')
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['pwd']

        if (not username) or (not pwd):
            error = 'Username or password unspecified'
        else:
            cur = db.get_db().cursor()
            cur.execute('''
            SELECT user_id, username, password FROM Users WHERE username=?
            ''', (username))

            user_id = None
            row = cur.fetchone()
            while row is not None:
                if row['password'] == pwd:
                    user_id = row['user_id']
                    break;
                row = cur.fetchone()
            cur.close()
            if user_id is not None:
                return redirect(url_for('chat.home_user', user_id))
            error = 'Password incorrect'
            return render_template('login.html', error=error)
        if error is not None:
            print(error)
            # store error to be shown
            flash(error)
    return render_template('login.html', error=error)
