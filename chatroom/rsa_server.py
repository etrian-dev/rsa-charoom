import select
from socket import *
from select import POLLERR, POLLIN, POLLOUT, poll
from json import *
from collections import deque

import msg_api


class rsa_server:
    LISTEN_ADDR = '127.0.0.1'
    LISTEN_PORT = 22222
    BUFLEN = 1024

    def __init__(self, *args):
        msg_pipe = None
        self.sock_buf = bytearray(rsa_server.BUFLEN)
        self.pipe_buf = bytearray(rsa_server.BUFLEN)
        self.in_dq = deque()
        self.out_dq = deque()

    def __call__(self, *args):
        # set the message pipe from the client
        msg_pipe = args[0]
        port_in = args[1]
        port_out = args[2]
        # create a datagram socket to send & receive encrypted messages
        listen_sock = socket(family=AF_INET, type=SOCK_DGRAM)
        listen_sock.bind(
            (rsa_server.LISTEN_ADDR, port_in))
        # while the message is not quit, poll for new data
        keep_running: bool = True
        poller = select.poll()
        poller.register(listen_sock, POLLIN | POLLOUT | POLLERR)
        poller.register(msg_pipe, POLLIN | POLLOUT)
        while keep_running:
            print("polling...")
            readylist = poller.poll()
            print(readylist)
            for (fd, readyop) in readylist:
                if fd == msg_pipe.fileno() and (readyop & POLLIN) != 0:
                    poller.modify(fd, 0)
                    poller.modify(listen_sock, POLLIN | POLLOUT | POLLERR)
                    print('pipe')
                    read_len = msg_pipe.recv_bytes_into(self.pipe_buf, 0)
                    msg = msg_api.serialize_into(
                        {"data": str(self.pipe_buf[:read_len], 'UTF-8')})
                    # build the request
                    req = str()
                    req += " ".join(["POST", "/msg/me/you",
                                    "HTTP/1.1", "\r\n"])
                    req += " ".join(["Host:", rsa_server.LISTEN_ADDR, "\r\n"])
                    req += " ".join(["Content-type:",
                                    "application/json", "\r\n"])
                    req += " ".join(["Content-Lenght:",
                                    len(msg).__str__(), "\r\n"])
                    req += "".join(["\r\n", msg, "\r\n"])
                    print(req)
                    self.in_dq.append(req)
                # socket ready for input
                elif fd == listen_sock.fileno() and (readyop & POLLIN) != 0:
                    print('sk read')
                    (nread, addr) = listen_sock.recvfrom_into(
                        self.sock_buf, len(self.sock_buf))
                    print(f"recv'd {nread} bytes from address {addr}")
                    print(str(self.sock_buf[:nread], 'UTF-8'))
                    self.out_dq.append(self.sock_buf[:nread])
                elif fd == listen_sock.fileno() and (readyop & POLLOUT) != 0:
                    print('sk write')
                    try:
                        el = self.in_dq.popleft()
                        poller.modify(msg_pipe.fileno(), POLLIN)
                        listen_sock.sendto(
                            bytes(el, encoding='UTF-8'), (rsa_server.LISTEN_ADDR, port_out))
                        print('new msg written')
                    except IndexError:
                        poller.modify(fd, POLLIN | POLLERR)

        listen_sock.close()
