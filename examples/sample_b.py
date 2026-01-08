# sample_b.py



def generator_example(n):
    """
    Generate an example generator.
    
    Parameters
    ----------
    n : int
        The input value used to generate the example.
    
    Returns
    -------
    None
    
    Notes
    -----
    This function serves as an example of a generator function.
    It does not perform any meaningful computation, but rather
    demonstrates the basic structure of a generator.
    """

    i = 0
    while i < n:
        yield i
        i += 1


def raises_example(x, y):
    """
    Raises an example exception.
    
    Parameters
    ----------
    x : any
        The first value to raise an exception with.
    y : any
        The second value to raise an exception with.
    
    Returns
    -------
    None
    
    Raises
    ------
    Exception
        An example exception is raised with the values x and y.
    """

    if y == 0:
        raise ValueError("division by zero")
    return x / y