# tests/test_coverage_reporter.py

"""Tests for coverage reporter."""

import pytest
import os

from pathlib import Path
from core.reporter.coverage_reporter import compute_coverage
from core.parser.python_parser import parse_path


def test_system_check():
    assert 1 + 1 == 2

def test_core_folder_exists():
    core_path = Path("core")
    assert core_path.exists()  is True
    
def test_coverage_keys_exist():
    """Test coverage report structure."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    assert "aggregate" in report
    assert "coverage_percent" in report["aggregate"]
    assert "total_functions" in report["aggregate"]
    assert "documented" in report["aggregate"]


def test_coverage_threshold_check():
    """Test threshold checking in coverage report."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed, threshold=90)
    
    assert "meets_threshold" in report["aggregate"]
    assert isinstance(report["aggregate"]["meets_threshold"], bool)


def test_empty_input_handling():
    """Test coverage computation with empty input."""
    report = compute_coverage([])
    assert report["aggregate"]["total_functions"] == 0
    assert report["aggregate"]["coverage_percent"] == 0