class EncryptedMsg:
    def __init__(self, data: str, stamp: int):
        self.message = data
        self.timestamp = stamp

from . import db
from sqlite3 import Connection, Cursor, DatabaseError
from json import loads

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from flask.json import jsonify

blueprint = Blueprint('msg', __name__, url_prefix='/msg')


@blueprint.route('/<sender>/<receiver>/', methods=['GET'])
def get_all_messages(sender, receiver):
    return f"GET all msg from {sender} to {receiver}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>/', methods=['GET'])
def get_message(sender, receiver, msg_id):
    return f"GET msg from {sender} to {receiver}: ID = {msg_id}"


@blueprint.route('/<int:sender>/<int:recipient>/', methods=['POST'])
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


#TODO: PUT the message trough jQuery
@blueprint.route('/<int:msg_id>', methods=['GET', 'PUT'])
def edit_message(msg_id):
    if request.method == 'PUT':
        cur = db.get_db().execute('''
        SELECT sender,recipient FROM Messages WHERE msg_id = ?;
        ''', [msg_id])
        sender_recipient = cur.fetchone()
        newmsg = request.get_json()['msg']
        cur.execute('''
        UPDATE Messages SET msg_data = ? WHERE msg_id = ?;
        ''', [newmsg.encode(encoding='utf-8'), msg_id])
        db.get_db().commit()
        flash(f"Message {msg_id} updated successfully")
        url = url_for('chat.display_chat', user=sender_recipient['sender'], other=sender_recipient['recipient'])
        return jsonify({"url": url})
    # Otherwise render the webpage containing the message to be modified
    msg_data = dict()
    msg_data['msg_id'] = msg_id
    db_conn = db.get_db()
    cur = db_conn.execute('''
    SELECT * FROM Messages WHERE msg_id = ?;''', [msg_id])
    msg_row = cur.fetchone()
    msg_data['old_msg'] = msg_row['msg_data'].decode(encoding='utf-8')
    return render_template('edit_message.html', **msg_data)


@blueprint.route('/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    if request.method == 'DELETE':
        # Build the url of the chat where the user will be redirected after deletion
        cur = db.get_db().execute('''
        SELECT sender,recipient FROM Messages WHERE msg_id = ?;
        ''', [msg_id])
        sender_recipient = cur.fetchone()
        url = url_for('chat.display_chat', user=sender_recipient['sender'], other=sender_recipient['recipient'])
        # Delete the message
        cur.execute('''
        DELETE FROM Messages WHERE msg_id = ?;
        ''', [msg_id])
        db.get_db().commit()
        return jsonify({"url": url})
