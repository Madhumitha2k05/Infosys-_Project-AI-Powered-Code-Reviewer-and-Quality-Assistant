# tests/_test_parser.py

import os

from core.parser.python_parser import PythonParser


def test_parse_examples():
    """Simple sanity test for the AST parser on the examples folder."""
    parser = PythonParser()
    base_dir = os.path.join(os.path.dirname(__file__), "..", "examples")

    modules = parser.parse_directory(base_dir)

    # We expect at least the two sample files
    assert len(modules) >= 2

    total_classes = sum(len(m.classes) for m in modules)
    total_functions = sum(len(m.functions) for m in modules)

    assert total_classes > 0
    assert total_functions > 0