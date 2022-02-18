import json
from socket import socket


def serialize_into(data) -> str:
    json_str = json.dumps(data, indent=4)
    return json_str
