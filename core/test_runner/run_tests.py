import subprocess
import os

def run_tests():
    """
    Runs pytest and generates JSON test report automatically.
    """
    os.makedirs("storage", exist_ok=True)

    cmd = [
        "pytest",
        "tests",
        "--json-report",
        "--json-report-file=storage/test_results.json"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }