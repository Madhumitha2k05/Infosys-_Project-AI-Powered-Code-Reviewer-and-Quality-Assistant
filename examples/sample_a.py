# sample_a.py


def calculate_average(numbers):
    s = 0
    for i in numbers:
        s = s + i
    return s / len(numbers)



def add(a, b):
    """
    Adds two numbers together.
    
    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add.
    
    Returns
    -------
    None
    
    Raises
    ------
    None
    """
    return a + b


def process(data):
    """
    Processes the input data.
    
    Parameters:
        data (list): The input data to be processed.
    
    Returns:
        None
    
    Raises:
        None
    """
    result = []
    for d in data:
        result.append(d * 2)
    return result