def extended_euclid(a: int, b: int) -> (int, int, int):
    if b == 0:
        return (a, 1, 0)
    (rem, x1, y1) = extended_euclid(b, a % b)
    #print(f"rem = {rem}, x1 = {x1}, y1 = {y1}")
    return (rem, y1, x1 - (a // b) * y1)

if __name__ == "__main__":
    a = int(input("a = "))
    b = int(input("b = "))
    print(f"Find x,y,z so that {a}x + {b}y = z")

    (z, x, y) = extended_euclid(a, b)
    print(f"z = {z}, x = {x}, y = {y}") 
