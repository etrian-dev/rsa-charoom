from . import fastexp
import secrets

def miller_rabin_test(guess: int, iters: int) -> bool:
    """Performs a Miller-Rabin primality test.

    The Miller-Rabin test on the primality of guess ensures that,
    if true is returned, then guess is prime with probability
    1 - 4^(-iters). If the function returs False, then guess in
    certaintly composite.
    """
    w = 0
    z = guess - 1
    while(z % 2 == 0):
        w += 1
        z = z // 2
    i = 0;
    while i < iters:
        witness = 2 + secrets.randbelow(guess - 3)
        tmp = fastexp.fastexp(witness, z, guess)
        if not (tmp == 1 or tmp + 1 == guess):
            j = 1
            while j < w:
                tmp = fastexp.fastexp(tmp, 2, guess)
                if tmp + 1 == guess:
                    break
                j += 1
            if j >= w:
                return False
        i += 1
    return True

if __name__ == "__main__":
    n = int(input("number: "))
    iter = int(input("iterations: "))
    if miller_rabin_test(n,iter):
        print(n, "is probably prime (probability >=", 1.0 - 4.0**(-iter))
    else:
        print(n, "is certaintly composite")
