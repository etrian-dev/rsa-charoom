
from time import time
from datetime import datetime
from sqlite3 import Connection, DatabaseError
from json import load
import logging

from flask import (Blueprint, request, render_template)
from . import db
from . import Msg
from . import Auth
from chatroom.decorators.auth import login_required
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
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


blueprint = Blueprint('chat', __name__, url_prefix='/chats')

@blueprint.route('/<int:user_id>', methods=['GET'])
@login_required
def home_user(user_id: int):
    if not Auth.authorized(user_id):
        return redirect(url_for('auth.login'))
    cur = db.get_db().cursor()
    user_data = dict()
    user_data['user_id'] = user_id
    try:
        # Fetch the username
        cur.execute(
            '''SELECT username FROM Users WHERE user_id = ?''',
            [user_id])
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
            ch.creation_time = datetime.strptime(
                row['creation_tm'], "%Y-%m-%d %H:%M:%S").isoformat()
            ch.last_activity = datetime.strptime(
                row['last_mod_tm'], "%Y-%m-%d %H:%M:%S").isoformat()
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
@login_required
def create_chat(creator):
    if not Auth.authorized(creator):
        return redirect(url_for('auth.login'))
    # TODO: check that the current session for this client is logged as
    # <creator>
    error = None
    matching_users = []
    if request.method == 'POST' and 'matching-users' in request.form:
        # get the username of the user the creator wants to chat with
        # this value exists in the database because checks are made by the search service
        # and it's unique because it's returned trough a form select
        user_id = request.form['matching-users']
        db_conn = db.get_db()
        try:
            cursor = db_conn.execute('''
            SELECT user_id, username, password
            FROM Users
            WHERE user_id=?;''', [user_id])
            # user_id is primary key, so at most one tuple is fetched from the db
            match = cursor.fetchone()
            if match is not None:
                # FIXME: probably should modify the db schema for the last two attributes -> timestamp
                cursor.execute('''
                INSERT INTO Chats(participant1, participant2, creation_tm, last_mod_tm)
                VALUES (?,?,datetime(),datetime());
                ''', [creator, match['user_id']])
                db_conn.commit()
                cursor.close()

                logging.info(f"Chat between {creator} and {match['user_id']} created at {datetime.now()}")
                return redirect(url_for('chat.display_chat',
                                user=creator, other=match['user_id']))
        except DatabaseError:
            error = 'DB lookup or insert failed'
    return "Unimplemented"


@blueprint.route('/<int:user>/<int:other>', methods=['GET'])
@login_required
def display_chat(user, other):
    if not Auth.authorized(user):
        return redirect(url_for('auth.login'))
    chat_info = {}
    chat_info['this_user_id'] = user
    chat_info['other_user_id'] = other
    db_conn = db.get_db()
    
    # fetch user IDs and usernames
    # of the current user and the other participant in the chat
    try:
        cur = db_conn.execute('''
        SELECT username FROM Users WHERE user_id = ?;
        ''', [user])
        chat_info['this_user'] = cur.fetchone()['username']
        cur.execute('''
        SELECT user_id,username FROM Users WHERE user_id = ?;
        ''', [other])
        chat_info['other_user'] = cur.fetchone()['username']
    except:
        logging.error(f"Either user {user} or {other} not found in the database")
        return render_template('404_not_found.html')
    
    # build breadcrumb
    breadcrumb = {}
    breadcrumb['home'] = url_for('chat.home_user', user_id=user)
    breadcrumb[chat_info['other_user']] = url_for(
        'chat.display_chat', user=user, other=other)
    chat_info['breadcrumb'] = breadcrumb

    # fetch the chat 
    # (the or is needed because we don't know who created the chat)
    cur.execute('''
    SELECT * FROM Chats
    WHERE (participant1 = ? AND ? = participant2) OR (participant1 = ? AND participant2 = ?);
    ''', [user, other, other, user])
    chat = cur.fetchone()
    # check if the chat exists
    if chat is None:
        logging.error(f"Chat between {user} and {other} not found")
        return render_template('404_not_found.html')
    # fetch all messages sent by the other user
    cur.execute('''
    SELECT * FROM Messages WHERE chatref = ? AND sender == ? ;
    ''', [chat['chat_id'], other])
    msgs_encoded = cur.fetchall()
    
    # decode messages
    messages = []
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
             'data': Msg.decrypt_message(user, msg['msg_data']),
             'tstamp': msg['tstamp']})
    # fetch all messages sent by this user from the msgstore
    try:
        with open(Msg.get_msgstore(user, other), 'r') as msgstore:
            sent_messages = load(msgstore)
            for msg in sent_messages:
                messages.append(
                    {'msg_id': msg['msg_id'],
                     'sender': chat_info['this_user'],
                     'receiver': chat_info['other_user'],
                     'data': msg['data'],
                     'tstamp': msg['tstamp']})
    except FileNotFoundError:
        pass  # no messages sent by this user yet
    messages.sort(key=lambda x: x['tstamp'])
    chat_info['messages'] = messages

    logging.info(f"User {user} requested the chat with {other}: {len(messages)} messages served")
    return render_template('messages.html', **chat_info)


@blueprint.route('/<creator>/<recipient>/', methods=['GET'])
@login_required
# TODO: delete
def delete_chat(creator, recipient):
    if not Auth.authorized(creator):
        return redirect(url_for('auth.login'))
    return "DELETED chat between " + creator + " and " + recipient
