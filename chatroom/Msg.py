class EncryptedMsg:
    def __init__(self, data: str, stamp: int):
        self.message = data
        self.timestamp = stamp

from . import db
from sqlite3 import Connection, Cursor, DatabaseError

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

blueprint = Blueprint('msg', __name__, url_prefix='/msg')


@blueprint.route('/<sender>/<receiver>/', methods=['GET'])
def get_all_messages(sender, receiver):
    return f"GET all msg from {sender} to {receiver}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>/', methods=['GET'])
def get_message(sender, receiver, msg_id):
    return f"GET msg from {sender} to {receiver}: ID = {msg_id}"


@blueprint.route('/<int:sender>/<int:recipient>/', methods=['POST'])
# TODO: post
def send_message(sender, recipient):
    db_conn = db.get_db()
    try:
        # get the chat id
        cur = db_conn.execute('''
        SELECT chat_id FROM Chats
        WHERE :sender != :recipient
            AND :sender IN (participant1, participant2)
            AND :recipient IN (participant1, participant2);
        ''', {"sender": sender, "recipient": recipient})
        chat_id = cur.fetchone()['chat_id']
        # get the private key of this user
        cur.execute('''
        ''')
        # retrieve the message data
        msg_data = request.form['message']
        # insert the message
        cur.execute('''
        INSERT INTO Messages(chatref,sender,recipient,msg_data)
        VALUES (?, ?, ?, ?);
        ''', [chat_id, sender, recipient, msg_data.encode(encoding='utf-8')])
        db_conn.commit()
        print(f"{sender} said: {msg_data} to {recipient}")
        # return an empty response, with a 201 Created code
        return redirect(url_for('chat.display_chat', user=sender, other=recipient))
    except DatabaseError:
        return f"Error"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>', methods=['GET'])
def edit_message(sender, receiver, msg_id):
    return f"PUTed msg from {sender} to {receiver}: {msg_id}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>', methods=['GET'])
# TODO: delete
def delete_message(sender, receiver, msg_id):
    return f"DELETEed msg from {sender} to {receiver}"
