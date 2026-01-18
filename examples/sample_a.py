# sample_a.py


def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.
    
    Parameters:
        numbers (list): A list of numbers to calculate the average from.
    
    Returns:
        None
    
    Raises:
        None
    """
    s = 0
    for i in numbers:
        s = s + i
    return s / len(numbers)



def add(a, b):
    """
    Adds two numbers together.
    
    Parameters:
        a (float): The first number to add.
        b (float): The second number to add.
    
    Returns:
        None
    
    Raises:
        None
    """
    return a + b


def process(data):
    """
    Process the input data.
    
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