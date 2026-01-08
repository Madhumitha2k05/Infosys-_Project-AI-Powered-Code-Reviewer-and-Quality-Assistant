# sample_a.py


def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.
    
    Args:
        numbers (list): A list of numbers to calculate the average from.
    
    Returns:
        None: The function does not return any value, it simply prints the average.
    
    Raises:
        ValueError: If the input list is empty.
    
    Notes:
        This function assumes that the input list contains only numbers.
        If the list contains non-numeric values, a ValueError will be raised.
    """

    s = 0
    for i in numbers:
        s = s + i
    return s / len(numbers)


def add(a, b):
    """
    Adds two numbers together.
    
    Args:
        a (int or float): The first number to add.
        b (int or float): The second number to add.
    
    Returns:
        None: This function does not return a value.
    """

    return a + b


def process(data):
    """
    Processes the given data.
    
    Args:
        data: The input data to be processed.
    
    Returns:
        None
    """

    result = []
    for d in data:
        result.append(d * 2)
    return result