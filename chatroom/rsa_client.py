from rsa import *
from rsa_server import rsa_server
import multiprocessing as mp


def msg_to_int(msg: str) -> int:
    """Simple bijective encoding function from strings to integers.
    """
    return int.from_bytes(bytes(msg, "utf-8"), byteorder='big')


def int_to_msg(num: int) -> str:
    """Simple bijective decoding function from integers to strings.
    """
    return str(num.to_bytes(num.bit_length(), byteorder='big'), 'utf-8')


if __name__ == "__main__":
    mp.set_start_method("spawn")
    # bidirectional pipe for message exchange
    client_pipe, serv_pipe = mp.Pipe(True)

    port_in = int(input("port_in:"))
    port_out = int(input("port_out:"))

    rsa_servobj = rsa_server()
    serv_proc = mp.Process(
        target=rsa_servobj,
        name="rsa_server",
        args=(serv_pipe, port_in, port_out)
    )
    serv_proc.start()

    client_pipe.send_bytes(b'ciao')

    serv_proc.join()
