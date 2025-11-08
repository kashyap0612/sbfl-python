def add(a, b):
    # BUG: should be a + b, but it's a - b
    return a - b

def mul(a, b):
    return a * b

def max_of_two(a, b):
    if a > b:
        return a
    else:
        return b
