def cbc_mode(msg: bytes, iv: bytes, encrypt, pk: (int, int) , blocksize=1024):
    """A generator that splits the message into blocks using CBC.

    This generator receives in input the message to be sent and splits it into
    fixed-lenght blocks (1K bits by default). Each block is derived from the previous
    using cipher block chaining (CBC).
    """
    offset = 0
    # An initialization vector (IV) is required to start the chain
    prev = int.from_bytes(iv, byteorder='big')
    while offset < len(msg):
        # Extracts the next block from the message
        block = msg[offset:offset+blocksize-1]
        print(f"block from {offset} to {offset+blocksize-1}")
        print(block)
        # Convert each block into an integer
        x = int.from_bytes(block, byteorder='big')
        print(f"x = {x}")
        # The plaintext is XOR'd with the previous block's ciphertext
        x = x ^ prev
        print(f"x ^ prev = {x}")
        # The resulting block is encrypted and sent to output
        cipher = encrypt(x, pk[0], pk[1])
        print(f"cipher = {cipher}")
        yield cipher
        # Updates the cipher block and the offset inside the message
        prev = cipher
        offset += blocksize

from . import genrandom
from . import rsa

if __name__ == "__main__":
    msg = input("msg: ")
    p = genrandom.gen_prime(384)
    q = genrandom.gen_prime(512)
    (e,n) = rsa.rsa_encrypt(p, q)
    # cipher in cbc mode
    gen = cbc_mode(
            bytes(msg, 'utf-8'),
            token_bytes(16),
            rsa.rsa_encrypt,
            (e,n),
            blocksize=16)
    for block in gen:
        print(f"=====\n{block}\n=====")
