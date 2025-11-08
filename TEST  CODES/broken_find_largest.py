def find_largest(nums):
    # BUG: iterates the full list and then adds 1 to result
    largest = nums[0]
    for n in nums:        # should be for n in nums[1:]
        if n > largest:
            largest = n
    return largest + 1
