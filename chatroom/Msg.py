class EncryptedMsg:
    def __init__(self, data: str, stamp: int):
        self.message = data
        self.timestamp = stamp

from flask import Blueprint

blueprint = Blueprint('msg', __name__, url_prefix='/msg')


@blueprint.route('/<sender>/<receiver>/', methods=['GET'])
def get_all_messages(sender, receiver):
    return f"GET all msg from {sender} to {receiver}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>/', methods=['GET'])
def get_message(sender, receiver, msg_id):
    return f"GET msg from {sender} to {receiver}: ID = {msg_id}"


@blueprint.route('/<sender>/<receiver>/', methods=['GET'])
# TODO: post
def send_message(sender, receiver):
    return f"POSTed msg from {sender} to {receiver}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>', methods=['GET'])
# TODO: put
def edit_message(sender, receiver, msg_id):
    return f"PUTed msg from {sender} to {receiver}: {msg_id}"


@blueprint.route('/<sender>/<receiver>/<int:msg_id>', methods=['GET'])
# TODO: delete
def delete_message(sender, receiver, msg_id):
    return f"DELETEed msg from {sender} to {receiver}"
