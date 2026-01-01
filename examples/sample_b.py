# sample_b.py


def generator_example(n):
    """
    Generate a sequence of numbers up to n.
    
    Parameters
    ----------
    n : int
        The upper limit of the sequence.
    
    Returns
    -------
    None
    
    Notes
    -----
    This function is a placeholder for a more complex operation.
    It is intended to be used as an example of how to structure
    a function with a single argument.
    
    Examples
    --------
    >>> generator_example(n=10)
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
        The first value to be used in the exception.
    y : any
        The second value to be used in the exception.
    
    Returns
    -------
    None
    
    Raises
    ------
    Exception
        An example exception is raised when this function is called.
    """

    if y == 0:
        raise ValueError("division by zero")
    return x / y