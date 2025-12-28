# no imports
# no module docstring


def generator_example(n):
    """generator_example function.
    
    Args:
        n (Any): Description of n.
    
    Returns:
        Any: Description of return value.
    
    """

    # no docstring
    i = 0
    while True:
        if i == n:
            break
        yield i
        i = i + 1


def raises_example(x):
    """raises_example function.
    
    Args:
        x (Any): Description of x.
    
    Returns:
        Any: Description of return value.
    
    """

    # misleading name, no raise
    if x < 0:
        print("bad value")
    else:
        return x * 2