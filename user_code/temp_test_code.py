def test_average_fail():
    assert abs(average([2, 4, 6]) - 4) < 1e-6

def test_multiply_pass():
    assert multiply(2, 3) == 6

def test_is_even_pass():
    assert is_even(4) == True
