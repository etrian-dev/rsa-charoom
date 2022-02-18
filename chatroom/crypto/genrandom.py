from secrets import randbits
from . import miller_rabin

def gen_prime(bitlen: int, iters: int) -> int:
    """Generates a probably prime integer of bitlen bits.

    The Miller-Rabin primality test is performed on a randomly
    generated integer of (at least) bitlen bits. If such number
    passes iters iterations of the test then it's declared prime
    and returned.
    """
    if bitlen <= 0 or iters <= 0:
        return -1
    guess = randbits(bitlen)
    # ensure the highest bit set and odd number
    mask = 0x1 << (bitlen - 1)
    guess = guess|mask|0x1
    while(not miller_rabin.miller_rabin_test(guess, iters)):
        guess += 2
    return guess

if __name__ == "__main__":
    bits = int(input("#bits = "))
    iter = int(input("iterations = "))
    print("probably prime:", gen_prime(bits, iter))
