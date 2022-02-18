from secrets import randbelow,token_bytes
from . import fastexp
from . import genrandom
from . import extended_euclid
from . import cbc

def rsa_gen_keypair(p: int, q: int) -> (int, int):
    """Generates a keypair (e,d) for the RSA cipher.

    Given the number of bits used to represent p and q, this
    function generates a suitable keypair for the rsa cipher
    whose modulus is n = pq. Hence the output pair (e,d) is
    such that e*d mod p*q = 1
    """
    # TODO: more checks on e
    phi = (p-1)*(q-1)
    e = phi
    while e >= phi or extended_euclid.extended_euclid(e, phi)[0] != 1:
        e = randbelow(phi)

    (_,d,_) = extended_euclid.extended_euclid(e, phi)
    if d < 0:
        d = phi + d
    return (e,d)

def rsa_encrypt(message: int, exponent: int, mod: int) -> int:
    """RSA encryption function.

    This function implements the encryption operation
    of the RSA cipher, that is,
    ciphertext = message^exponent mod modulus.
    If message > modulus then -1 is returned, meaning
    that a message greater than modulus is not allowed
    """
    if message > mod:
        return -1
    else:
        return fastext.fastexp(message, exponent, mod)

def rsa_decrypt(ciphertext: int, private_key: int, mod: int) -> int:
    """RSA decryption function.

    This function implements the decryption operation
    of the RSA cipher
    """
    if ciphertext > mod:
        # TODO: check this name
        raise IllegalArgument
    else:
        return fastexp.fastexp(ciphertext, private_key, mod)

if __name__ == "__main__":
    bits = int(input("#bits = "))
    iters = int(input("iterations = "))
    p = genrandom.gen_prime(bits, iters)
    q = genrandom.gen_prime(bits, iters)
    while p == q:
        q = genrandom.gen_prime(bits, iters)

    n = p * q
    print(f"n = {p} * {q} = {n}")
    (e,d) = rsa_gen_keypair(p,q)
    print(f"e = {e}\nd = {d}")
    msg = input("message: ")

    msg_int = int.from_bytes(bytes(msg, 'utf-8'), byteorder='big')
    x = fastexp.fastexp(msg_int, e * d, n)

    print(f"{msg_int}^({e}*{d}) = {x}");

    cipher = rsa_encrypt(msg_int, e, n)
    plain = rsa_decrypt(cipher, d, n)
    print(f"{msg_int} -E-> {cipher} -D-> {plain}")


