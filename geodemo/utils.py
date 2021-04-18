def random_string(string_length=3, use_seed=False):
    """Generates a random string of fixed length.
    Args:
        string_length (int, optional): Fixed length. Defaults to 3.
    Returns:
        str: A random string
    """
    import random
    import string

    if use_seed:
        random.seed(1001)
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(string_length))


def add(x, y):
    """Add Function"""
    return x + y


def subtract(x, y):
    """Subtract Function"""
    return x - y


def multiply(x, y):
    """Multiply Function"""
    return x * y


def divide(x, y):
    """Divide Function"""
    if y == 0:
        raise ValueError('Can not divide by zero!')
    return x / y 