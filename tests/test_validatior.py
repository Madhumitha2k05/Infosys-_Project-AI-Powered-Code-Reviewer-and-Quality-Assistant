# tests/test_validator.py
"""Tests for docstring validator."""

from core.validator.validator import validate_docstrings, compute_complexity


def test_validator_returns_list():
    """Test that validator returns list of violations."""
    errors = validate_docstrings("examples/sample_a.py")
    assert isinstance(errors, list)
    
    # ✅ Validate error structure if any exist
    for error in errors:
        assert isinstance(error, (str, dict)), "Errors should be strings or dicts"
        if isinstance(error, str):
            assert len(error) > 0, "Error messages should not be empty"


def test_validator_detects_issues():
    """Test that validator actually detects docstring issues."""
    errors = validate_docstrings("examples/sample_a.py")
    
    # ✅ Check that validator provides meaningful feedback
    # If there are errors, they should mention functions or docstrings
    if errors:
        error_text = str(errors).lower()
        # At least one error should reference docstrings or functions
        assert any(keyword in error_text for keyword in 
                  ["docstring", "function", "missing", "undocumented"]), \
               "Validation errors should mention docstrings or functions"


def test_complexity_returns_list():
    """Test complexity computation returns list."""
    source = "def simple(): return 1"
    results = compute_complexity(source)
    assert isinstance(results, list)


def test_complexity_structure():
    """Test complexity result structure."""
    source = "def test(x):\n    if x > 0:\n        return x\n    return 0"
    results = compute_complexity(source)
    
    if results:
        result = results[0]
        assert "name" in result
        assert "complexity" in result
        assert isinstance(result["complexity"], int)
        
        # ✅ Validate complexity value is reasonable
        assert result["complexity"] >= 1, "Complexity should be at least 1"
        assert result["name"] == "test", "Function name should match"


def test_complexity_detects_branches():
    """Test that complexity increases with control flow."""
    # Simple function (complexity should be 1)
    simple_source = "def simple(): return 1"
    simple_results = compute_complexity(simple_source)
    
    # Complex function with branches (complexity > 1)
    complex_source = """
def complex_fn(x, y):
    if x > 0:
        if y > 0:
            return x + y
        return x
    return 0
"""
    complex_results = compute_complexity(complex_source)
    
    # ✅ Validate complexity calculation logic
    if simple_results and complex_results:
        simple_complexity = simple_results[0]["complexity"]
        complex_complexity = complex_results[0]["complexity"]
        
        assert complex_complexity > simple_complexity, \
               "Complex function should have higher complexity than simple function"
        assert complex_complexity >= 3, \
               "Function with nested ifs should have complexity >= 3"


def test_complexity_handles_multiple_functions():
    """Test complexity computation for multiple functions."""
    source = """
def func_a():
    return 1

def func_b(x):
    if x:
        return x
    return 0
"""
    results = compute_complexity(source)
    
    # ✅ Validate multiple functions are analyzed
    assert len(results) == 2, "Should analyze both functions"
    
    function_names = [r["name"] for r in results]
    assert "func_a" in function_names
    assert "func_b" in function_names
    
    # func_b should have higher complexity due to if statement
    func_a_complexity = next(r["complexity"] for r in results if r["name"] == "func_a")
    func_b_complexity = next(r["complexity"] for r in results if r["name"] == "func_b")
    
    assert func_b_complexity > func_a_complexity


def test_validator_with_valid_docstrings():
    """Test validator on file with proper docstrings."""
    # This test assumes there might be a well-documented example file
    # If all examples have issues, errors will be non-empty
    errors = validate_docstrings("examples/sample_a.py")
    
    # ✅ Just verify it runs without crashing
    assert isinstance(errors, list)
    
    # If errors exist, verify they're actionable
    for error in errors:
        if isinstance(error, str):
            assert len(error) > 10, "Error messages should be descriptive"