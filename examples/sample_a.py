# sample_a.py



def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.
    
    Args:
        numbers (list): A list of numbers for which to calculate the average.
    
    Returns:
        None: The function does not return any value, but instead prints the calculated average to the console.
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
        None: This function does not return a value, but rather modifies the input variables.
    """

    return a + b


def process(data):
    """
    Processes the input data.
    
    Args:
        data: The input data to be processed.
    
    Returns:
        None
    """

    result = []
    for d in data:
        result.append(d * 2)
    return result