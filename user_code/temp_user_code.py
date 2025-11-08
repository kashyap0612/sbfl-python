def average(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums) + 1  # BUG: extra +1 shifts result

def multiply(a, b):
    return a * b

def is_even(x):
    return x % 2 == 0
