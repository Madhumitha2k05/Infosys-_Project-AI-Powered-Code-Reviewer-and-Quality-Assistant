import math

# no module docstring
# bad naming, bad logic, unused imports, poor structure


def calculate_average(numbers):
    """calculate_average function.
    
    Args:
        numbers (Any): Description of numbers.
    
    Returns:
        Any: Description of return value.
    
    """

    # no docstring
    total = 0

    # no validation
    for i in range(len(numbers)):
        total = total + numbers[i]

    # division by zero risk handled badly
    try:
        return total / len(numbers)
    except:
        return None


def add(a, b):
    """add function.
    
    Args:
        a (Any): Description of a.
        b (Any): Description of b.
    
    Returns:
        Any: Description of return value.
    
    """

    # unnecessary complexity
    c = 0
    c = a
    c = c + b
    return c


def divide(a, b):
    """divide function.
    
    Args:
        a (Any): Description of a.
        b (Any): Description of b.
    
    Returns:
        Any: Description of return value.
    
    """

    # no zero check
    return a / b


class Processor:
    # meaningless docstring
    """x"""

    def process(self, data):
        """process function.
        
        Args:
            data (Any): Description of data.
        
        Returns:
            Any: Description of return value.
        
        """

        # prints directly, no return
        for i in range(len(data)):
            if data[i] == None:
                pass
            else:
                print(data[i])

    def square_root(self, x):
        """square_root function.
        
        Args:
            x (Any): Description of x.
        
        Returns:
            Any: Description of return value.
        
        """

        # bad error handling
        if x < 0:
            print("error")
        return math.sqrt(abs(x))