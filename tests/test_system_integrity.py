import os
import pytest
from pathlib import Path

# This is a REAL test that checks if your project structure is correct
def test_project_structure_exists():
    """Checks if critical folders exist."""
    required_folders = ["core", "storage", "examples"]
    for folder in required_folders:
        assert os.path.exists(folder), f"Missing folder: {folder}"

def test_main_app_exists():
    """Checks if the main application file exists."""
    assert os.path.exists("main_app.py"), "main_app.py is missing!"

def test_storage_permissions():
    """Checks if we can write to the storage folder."""
    test_file = Path("storage/test_write.txt")
    try:
        test_file.write_text("write check")
        assert test_file.exists()
        test_file.unlink() # Delete after test
    except Exception as e:
        pytest.fail(f"Cannot write to storage: {e}")

def test_python_files_validity():
    """Checks if all python files compile (no syntax errors)."""
    # This scans your real project files
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and "venv" not in root:
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        compile(f.read(), path, "exec")
                except Exception as e:
                    # We mark this as failed but don't stop the whole suite
                    pytest.fail(f"Syntax Error in {file}: {e}")