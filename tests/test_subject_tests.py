from examples import test_subject

def test_add_positive():
    assert test_subject.add(1, 2) == 3

def test_add_negative():
    assert test_subject.add(-1, -2) == -3

def test_mul():
    assert test_subject.mul(3, 4) == 12

def test_max():
    assert test_subject.max_of_two(5, 2) == 5
