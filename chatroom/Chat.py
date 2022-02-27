from . import db

from time import time
from datetime import datetime
from sqlite3 import Connection, Cursor, DatabaseError

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

class Chat:
    """Defines a chat between two users.
    """
    def __init__(self, user1: str, user2: str):
        self.chat_id = None
        self.participant1 = user1
        self.participant2 = user2
        self.creation_time = None
        self.last_activity = None
        self.messages = []

    def add_message(data: str, timestamp):
        """Adds a new message to this chat.
        """
        self.messages.append(Msg.EncryptedMsg(data, timestamp))
    def delete_message(target):
        """Deletes a message from this chat.
        """
        try:
            i = self.messages.index(target)
            del self.messages[i]
        except ValueError:
            print("Message", target, "not found")

from flask import (Blueprint, request, render_template)

blueprint = Blueprint('chat', __name__, url_prefix='/chats')

@blueprint.route('/<int:user_id>', methods=['GET'])
def home_user(user_id: int):
    cur = db.get_db().cursor()
    user_data = dict()
    user_data['user_id'] = user_id
    try:
        # Fetch the username
        cur.execute('''SELECT username FROM Users WHERE user_id = ?''', [user_id])
        user_data['username'] = cur.fetchone()['username']
        # fetch this users's chats
        # FIXME: maybe use ? IN (participant1, participant2)
        cur.execute('''
        SELECT *
        FROM Chats
        WHERE participant1 = ? or participant2 = ?''', [user_id, user_id])
        for row in cur.fetchall():
            # create a chat object
            ch = Chat(row['participant1'], row['participant2'])
            ch.chat_id = row['chat_id']
            ch.creation_time = datetime.strptime(row['creation_tm'], "%Y-%m-%d %H:%M:%S").isoformat()
            ch.last_activity = datetime.strptime(row['last_mod_tm'], "%Y-%m-%d %H:%M:%S").isoformat()
            # insert that into the user_data dict
            if 'chats' not in user_data:
                user_data['chats'] = [ch]
            else:
                user_data['chats'].append(ch)
    except DatabaseError:
        flash('Cannot retrieve user data')
        return render_template('chats.html')
    return render_template('chats.html', user_data=user_data)

@blueprint.route('/<int:creator>/', methods=['POST'])
def create_chat(creator):
    # TODO: check that the current session for this client is logged as <creator>
    error = None
    matching_users = []
    if request.method == 'POST':
        # get the username of the user the creator wants to chat with
        username = request.form['username']
        # get matching users
        db_conn = db.get_db()
        try:
            cursor = db_conn.execute('''
            SELECT user_id, username, password
            FROM Users
            WHERE username=?;''', [username])

            # TODO: handle multiple users with the same username
            match = cursor.fetchone()
            if match is not None:
                cursor.execute('''
                INSERT INTO Chats(participant1, participant2, creation_tm, last_mod_tm)
                VALUES (?,?,datetime(),datetime());
                ''', [creator, match['user_id']])
                db_conn.commit()
                cursor.close()

                return redirect(url_for('chat.display_chat', user=creator, other=match['user_id']))
        except DatabaseError:
            error = 'DB lookup or insert failed'
    return render_template('chat_choice.html', matching_users)

@blueprint.route('/<int:user>/<int:other>', methods=['GET'])
def display_chat(user, other):
    chat_info = dict()
    chat_info['this_user_id'] = user
    chat_info['other_user_id'] = other
    db_conn = db.get_db()
    # fetch user IDs and usernames
    # of the current user and the other participant in the chat
    cur = db_conn.execute('''
    SELECT username FROM Users WHERE user_id = ?;
    ''', [user])
    chat_info['this_user'] = cur.fetchone()['username']
    cur.execute('''
    SELECT user_id,username FROM Users WHERE user_id = ?;
    ''', [other])
    chat_info['other_user'] = cur.fetchone()['username']
    # fetch the chat
    cur.execute('''
    SELECT * FROM Chats
    WHERE (participant1 = ? AND ? = participant2) OR (participant1 = ? AND participant2 = ?);
    ''', [user, other, other, user])
    chat = cur.fetchone()
    # fetch all messages
    cur.execute('''
    SELECT * FROM Messages WHERE chatref = ?;
    ''', [chat['chat_id']])
    msgs_encoded = cur.fetchall()
    messages = []
    # build breadcrumb
    breadcrumb = dict()
    breadcrumb['home'] = url_for('chat.home_user', user_id=user)
    breadcrumb[chat_info['other_user']] = url_for('chat.display_chat', user=user, other=other)
    chat_info['breadcrumb'] = breadcrumb
    #decode messages
    for msg in msgs_encoded:
        sender = None
        receiver = None
        if msg['sender'] == user:
            sender = chat_info['this_user']
            receiver = chat_info['other_user']
        else:
            sender = chat_info['other_user']
            receiver = chat_info['this_user']
        messages.append(
            {'msg_id': msg['msg_id'],
            'sender': sender,
            'receiver': receiver,
            'data': msg['msg_data'].decode(encoding='utf-8')})
    chat_info['messages'] = messages

    return render_template('messages.html', **chat_info)

@blueprint.route('/<creator>/<recipient>/', methods=['GET'])
# TODO: delete
def delete_chat(creator, recipient):
    return "DELETED chat between " + creator + " and " + recipient
