def fastexp(x: int, y: int , m: int) -> int:
    """Modular exponentiation function.

    This function implements the operation
    x^y mod m, where x, y and m are integers,
    doing a logarithmic number of operations
    """
    next = x
    res = 1
    while y > 0:
        if y % 2 == 1:
            res = (res * next) % m
        next = (next * next) % m;
        y = y // 2 
    return res 

if __name__ == "__main__":
    x = input("Enter x: ")
    y = input("Enter y: ")
    m = input("Enter m: ")
    res = fastexp(int(x), int(y), int(m))
    print(f"{x}^{y} mod {m} = {res}") 
