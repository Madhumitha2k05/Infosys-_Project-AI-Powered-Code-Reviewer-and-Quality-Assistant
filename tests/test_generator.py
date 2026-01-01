# tests/test_generator.py
"""Tests for docstring generator."""

from core.docstring_engine.generator import generate_docstring


def test_generate_google_docstring():
    """Test Google-style docstring generation."""
    fn = {
        "name": "add",
        "args": [{"name": "a", "annotation": "int"}, {"name": "b", "annotation": "int"}],
        "returns": "int"
    }
    
    doc = generate_docstring(fn, style="google")
    assert "Args:" in doc
    assert "Returns:" in doc
    assert "int" in doc  # Type annotation present


def test_generate_numpy_docstring():
    """Test NumPy-style docstring generation."""
    fn = {
        "name": "calculate",
        "args": [{"name": "x", "annotation": "float"}],
        "returns": "float"
    }
    
    doc = generate_docstring(fn, style="numpy")
    assert "Parameters" in doc
    assert "----------" in doc or "-------" in doc
    assert "Returns" in doc


def test_generate_rest_docstring():
    """Test reST-style docstring generation."""
    fn = {
        "name": "process",
        "args": [{"name": "data", "annotation": "str"}],
        "returns": "bool"
    }
    
    doc = generate_docstring(fn, style="rest")
    assert ":param" in doc
    assert ":return" in doc


def test_invalid_style_raises_error():
    """Test that invalid style raises ValueError."""
    fn = {"name": "test", "args": [], "returns": None}
    
    try:
        generate_docstring(fn, style="invalid_style")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown style" in str(e)
