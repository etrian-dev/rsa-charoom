class EncryptedMsg:
    def __init__(self, data: str, stamp: int):
        self.message = data
        self.timestamp = stamp
from chatroom.crypto import rsa

from . import db
from sqlite3 import Connection, Cursor, DatabaseError
from json import (load, loads, dump, dumps)
from os import fspath, path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from flask.json import jsonify

blueprint = Blueprint('msg', __name__, url_prefix='/msg')

def get_msgstore(sender: int, recipient: int):
    with open(fspath(f'{sender}_{recipient}_sent.json'), 'r') as msgstore:
        data = load(msgstore)
    # Create the message file
    open('sent.json', 'x')

def get_all_messages(sender, receiver):
    return f"GET all msg from {sender} to {receiver}"

# Get a specific message sent to receiver
def get_message(sender, receiver, msg_id):
    return f"GET msg from {sender} to {receiver}: ID = {msg_id}"

def msg_to_int(msg: str) -> int:
    """Simple bijective encoding function from strings to integers.
    """
    return int.from_bytes(bytes(msg, "utf-8"), byteorder='big')


def int_to_msg(num: int) -> str:
    """Simple bijective decoding function from integers to strings.
    """
    return str(num.to_bytes(num.bit_length(), byteorder='big'), 'utf-8')

def encrypt_msg(recipient: int, plaintext: str) -> int:
    '''Encrypt the plaintext message with recipient's public key.
    '''
    # get the public key of the recipient
    cur = db.get_db().execute('''
    SELECT pk_e,pk_n FROM Users WHERE user_id = ? 
    ''', [recipient])
    res = cur.fetchone()
    pubkey_n = res['pk_n']
    pubkey_e = res['pk_e']
    # Encrypt this message with the recipient's public key
    encrypted_msg = rsa_encrypt(msg_to_int(msg_data))
    return enctypted_msg


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
        # retrieve the message data
        msg_data = request.form['message']
        # encrypt
        encrypted_msg = encrypt_msg(recipient, msg_data)
        # insert the message
        cur.execute('''
        INSERT INTO Messages(chatref,sender,recipient,msg_data)
        VALUES (?, ?, ?, ?);
        ''', [chat_id, sender, recipient, enctypted_msg.to_bytes()])
        db_conn.commit()
        print(f"{sender} said: {msg_data} to {recipient}")
        # return an empty response, with a 201 Created code
        return redirect(url_for('chat.display_chat', user=sender, other=recipient))
    except DatabaseError:
        return f"Error"


@blueprint.route('/<int:msg_id>', methods=['GET', 'PUT'])
def edit_message(msg_id):
    if request.method == 'PUT':
        # Get the message sender and receiver
        cur = db.get_db().execute('''
        SELECT sender,recipient FROM Messages WHERE msg_id = ?;
        ''', [msg_id])
        sender_recipient = cur.fetchone()
        # get the new message (plaintext)
        newmsg = request.get_json()['msg']
        # encrypt the new message and update the db
        encrypted_msg = encrypt_msg(sender_recipient['recipient'], newmsg)
        cur.execute('''
        UPDATE Messages SET msg_data = ? WHERE msg_id = ?;
        ''', [encrypted_msg.to_bytes(), msg_id])
        db.get_db().commit()
        flash(f"Message {msg_id} updated successfully")
        url = url_for('chat.display_chat', user=sender_recipient['sender'], other=sender_recipient['recipient'])
        return jsonify({"url": url})
    # Otherwise render the webpage containing the message to be modified
    msg_data = dict()
    msg_data['msg_id'] = msg_id
    db_conn = db.get_db()
    cur = db_conn.execute('''
    SELECT msg_data  FROM Messages WHERE msg_id = ?;''', [msg_id])
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
