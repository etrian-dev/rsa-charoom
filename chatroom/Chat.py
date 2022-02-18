from time import time

class Chat:
    """Defines a chat between two users.
    """
    def __init__(self, user: str):
        self.recipient = user
        self.creation_tstamp = int(time.time())
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

@blueprint.route('/<username>', methods=['GET'])
def home_user(username=None):
    return render_template('index.html', username=username)

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
