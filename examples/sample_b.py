# sample_b.py



def generator_example(n):
    """
    Generates a sequence of numbers from 0 to n-1.
    
    Parameters:
        n (int): The upper limit of the sequence.
    
    Returns:
        None
    
    Raises:
        None
    """
    i = 0
    while i < n:
        yield i
        i += 1


def raises_example(x, y):
    """
    Raises an example exception if the input values are not equal.
    
    Parameters:
        x (int): The first value to compare.
        y (int): The second value to compare.
    
    Raises:
        ValueError: If x and y are not equal.
    """
    if y == 0:
        raise ValueError("division by zero")
    return x / y