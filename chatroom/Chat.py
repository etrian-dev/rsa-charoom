from . import db

from time import time
from sqlite3 import Connection, Cursor, DatabaseError

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
    try:
        # Fetch the username
        cur.execute('''SELECT username FROM Users WHERE user_id = ?''', [user_id])
        user_data['username'] = cur.fetchone()
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
            ch.creation_time = row['creation_tm']
            ch.last_activity = row['last_mod_tm']
            # insert that into the user_data dict
            if user_data['chats'] is None:
                user_data['chats'] = [ch]
            else:
                user_data['chats'].append(ch)
    except DatabaseError:
        flash('Cannot retrieve user data')
        return render_template('chats.html')
    return render_template('chats.html', user_data=user_data)

@blueprint.route('/<creator>/', methods=['GET'])
# TODO: post
def create_chat(creator):
    data = request.get_json()
    if data is not None:
        pass
    else:
        pass
    return "POSTed chat by " + creator


@blueprint.route('/<creator>/<recipient>/', methods=['GET'])
# TODO: delete
def delete_chat(creator, recipient):
    return "DELETED chat between " + creator + " and " + recipient
