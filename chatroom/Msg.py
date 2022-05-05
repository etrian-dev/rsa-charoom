class EncryptedMsg:
    def __init__(self, data: str, stamp: int):
        self.message = data
        self.timestamp = stamp
from chatroom.crypto import rsa

from . import db
from sqlite3 import Connection, Cursor, DatabaseError
from json import (load, loads, dump, dumps)
from os import fspath, path, SEEK_END, SEEK_SET
from time import time
import logging

from flask import (
    Blueprint, flash, g, current_app, redirect, render_template, request, session, url_for, make_response
)
from flask import Flask
from flask.json import jsonify

blueprint = Blueprint('msg', __name__, url_prefix='/msg')

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
    return str(num.to_bytes(num.bit_length() // 8 + 1, byteorder='big'), 'utf-8')

def encrypt_msg(recipient: int, plaintext: str) -> int:
    '''Encrypt the plaintext message with recipient's public key.
    '''
    # get the public key of the recipient
    cur = db.get_db().execute('''
    SELECT pk_e,pk_n,pk_d FROM Users WHERE user_id = ?
    ''', [recipient])
    res = cur.fetchone()
    pubkey_n = int.from_bytes(res['pk_n'], byteorder='big')
    pubkey_e = int.from_bytes(res['pk_e'], byteorder='big')
    # Encrypt this message with the recipient's public key
    orig_msg_int = msg_to_int(plaintext)
    encrypted_msg = rsa.rsa_encrypt(orig_msg_int, pubkey_e, pubkey_n)

    pubkey_d = int.from_bytes(res['pk_d'], byteorder='big')
    decrypted_msg = rsa.rsa_decrypt(encrypted_msg, pubkey_d, pubkey_n)
    assert orig_msg_int == decrypted_msg, "Messages differ"

    return encrypted_msg

def decrypt_message(recipient: int, data: bytes) -> str:
    '''Decrypts a bytes object directed to this user into a message'''
    cur = db.get_db().execute('''
    SELECT pk_n,pk_d FROM Users WHERE user_id = ?
    ''', [recipient])
    res = cur.fetchone()
    pubkey_n = int.from_bytes(res['pk_n'], byteorder='big')
    priv_key = int.from_bytes(res['pk_d'], byteorder='big')
    decrypted_msg = rsa.rsa_decrypt(int.from_bytes(data, byteorder='big'), priv_key, pubkey_n)
    return int_to_msg(decrypted_msg)

def get_msgstore(sender, receiver) -> str:
    # TODO: fix
    return fspath(f'{current_app.instance_path}/{sender}_{receiver}_sent.json')

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

        # get the timestamp
        tstamp = int(time())

        # insert the message
        cur.execute('''
        INSERT INTO Messages(chatref,sender,recipient,msg_data,tstamp)
        VALUES (?, ?, ?, ?, ?);
        ''', 
        [chat_id, 
        sender, 
        recipient, 
        encrypted_msg.to_bytes(length=encrypted_msg.bit_length() // 8 + 1, byteorder='big'),
        tstamp])
        # store the last row id == msg_id in this case
        msg_id = cur.lastrowid
        db_conn.commit()
        logging.info(f"{sender} sent message {msg_id} to {recipient} at {tstamp}")

        # Save the message to the msgstore
        msg_obj = {
            "msg_id": msg_id, 
            "sender": sender, 
            "recipient": recipient, 
            "data": msg_data, 
            "tstamp": tstamp}
        file_exists = path.exists(get_msgstore(sender,recipient))
        if file_exists:
            with open(get_msgstore(sender, recipient), 'r+b') as msgstore:
                # if there are no sent messages from sender to recipient, write a new array
                # with one element
                r = msgstore.read(2).decode(encoding='utf-8')
                if r == '[]':
                    msgstore.seek(0, SEEK_SET)
                    msgstore.write(('[ ' + dumps(msg_obj) + ' ]').encode(encoding='utf-8'))
                else:
                    # otherwise a line is added, by extending the array with a comma and a newline
                    # and then rewriting a ']' at the end
                    b = msgstore.seek(-1, SEEK_END)
                    msgstore.write((',\n' + dumps(msg_obj) + ' ]').encode(encoding='utf-8'))
        else:
            # creates and writes the array containing this message
            with open(get_msgstore(sender, recipient), 'a') as msgstore:
                msgstore.write('[ ' + dumps(msg_obj) + ' ]')
    except DatabaseError:
        flash(f"Failed to send the message")
    except:
        flash(f"Some error occurred")
    # Redirects the user to the chat page after creating the resource
    return redirect(url_for('chat.display_chat', user=sender, other=recipient))



@blueprint.route('/<int:msg_id>', methods=['GET', 'PUT'])
def edit_message(msg_id):
    # Get the message sender and receiver
    cur = db.get_db().execute('''
    SELECT sender,recipient FROM Messages WHERE msg_id = ?;
    ''', [msg_id])
    sender_recipient = cur.fetchone()
    # Modify the message
    if request.method == 'PUT':
        # get the new message (plaintext)
        newmsg_data = request.get_json()['msg']
        # encrypt the new message and update the db
        encrypted_msg = encrypt_msg(sender_recipient['recipient'], newmsg_data)
        cur.execute('''
        UPDATE Messages SET msg_data = ? WHERE msg_id = ?;
        ''', [encrypted_msg.to_bytes(encrypted_msg.bit_length() // 8 + 1, byteorder='big'), msg_id])
        db.get_db().commit()
        # update the message stored in the msgstore as well
        old = None
        newmsg = None
        with open(get_msgstore(sender_recipient['sender'], sender_recipient['recipient']), 'r') as msgstore:
            messages = load(msgstore)
            for msg in messages:
                if msg['msg_id'] == msg_id:
                    newmsg = msg
                    newmsg['data'] = newmsg_data
                    old = msg
                    break
        messages.remove(old)
        messages.append(newmsg)
        with open(get_msgstore(sender_recipient['sender'], sender_recipient['recipient']), 'w') as msgstore:
            msgstore.write(dumps(messages))
        flash(f"Message {msg_id} updated successfully")
        url = url_for('chat.display_chat', user=sender_recipient['sender'], other=sender_recipient['recipient'])
        return jsonify({"url": url})
    # Otherwise render the webpage containing the message to be modified
    msg_data = dict()
    msg_data['msg_id'] = msg_id
    with open(get_msgstore(sender_recipient['sender'], sender_recipient['recipient']), 'r') as msgstore:
        messages = load(msgstore)
        for msg in messages:
            if msg['msg_id'] == msg_id:
                msg_data['old_msg'] = msg['data']
                break
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
        # Delete from the msgstore as well
        to_delete = None
        with open(get_msgstore(sender_recipient['sender'], sender_recipient['recipient']), 'r') as msgstore:
            messages = load(msgstore)
            for msg in messages:
                if msg['msg_id'] == msg_id:
                    to_delete = msg
                    break
        messages.remove(to_delete)
        with open(get_msgstore(sender_recipient['sender'], sender_recipient['recipient']), 'w') as msgstore:
            msgstore.write(dumps(messages))
        db.get_db().commit()
        return jsonify({"url": url})
