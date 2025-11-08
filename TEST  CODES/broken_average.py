def average(nums):
    # BUG: off-by-one in denominator
    return sum(nums) / (len(nums) - 1)
