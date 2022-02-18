from . import Chat
from chatroom.crypto import miller_rabin, genrandom, rsa

from secrets import token_bytes
from hashlib import sha3_256
from random import getrandbits

PRIME_LEN = 15
ITERATIONS = 10
SALT_LEN = 16


class User:
    def __init__(self, user: str, pwd: str):
        # User login info
        self.user_id = getrandbits(64)
        self.username = user
        # TODO: hash + salt pwd
        #hash_obj = sha3_256()
        #hash_obj.update(token_bytes(SALT_LEN))
        #hash_obj.update(bytes(pwd, encoding='UTF-8'))
        #self.password_hashsalt = hash_obj.digest()
        self.password = pwd
        # cryptographic key generation
        p = genrandom.gen_prime(PRIME_LEN, ITERATIONS)
        q = genrandom.gen_prime(PRIME_LEN, ITERATIONS)
        while (p == q) or (not miller_rabin.miller_rabin_test(q, ITERATIONS)):
            q += 2
        (e, d) = rsa.rsa_gen_keypair(p, q)
        self.pub_key = (p * q, e)
        self.priv_key = d
        # Chats info
        self.chats = dict()
    def check_pwd(self, guess: str) -> bool:
        return self.password == guess

    def create_chat(recipient: str):
        """Creates a new chat with the given recipient.
        """
        newchat = Chat(recipient)
        self.chats[recipient] = newchat
    def __repr__(self):
        return 'User.Chatroom_user(' + self.username + ')'
    def __str__(self):
        s = 'User ' + self.user_id.__str__() + '\n'
        s += 'Username: ' + self.username + '\n'
        s += 'Password: ' + self.password + '\n'
        s += self.chats.__str__() + '\n'
        s += 'PUB_KEY:\n\t' + 'n = ' + hex(self.pub_key[0])[2:] + '\n\t' + 'e = ' + hex(self.pub_key[1])[2:] + '\n'
        s += 'PRIV_KEY: ' + hex(self.priv_key)[2:] + '\n'
        return s
    def __hash__(self) -> int:
        return self.user_id
    def __eq__(self, other) -> bool:
        return self.user_id == other.user_id
