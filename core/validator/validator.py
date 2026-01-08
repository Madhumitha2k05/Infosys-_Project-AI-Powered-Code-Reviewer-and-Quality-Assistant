"""
Validator for docstrings.
Checks whether a function docstring is OK or needs FIX.
"""

from typing import Dict, List
from core.parser.python_parser import FunctionInfo


class DocstringValidator:
    """
    Validates docstrings against basic rules and style.
    """

    @staticmethod
    def validate(fn: FunctionInfo, expected_style: str) -> Dict:
        """
        Validate a function's docstring.

        Returns:
        {
            "status": "OK" | "FIX",
            "reason": str,
            "issues": List[str]
        }
        """

        issues: List[str] = []

        # ❌ No docstring at all
        if not fn.raw_docstring:
            issues.append("Missing docstring")

        else:
            doc = fn.raw_docstring.strip()

            # Normalize style name
            style = expected_style.lower()

            # ---- Google style check ----
            if style == "google":
                if "Args:" not in doc and "Arguments:" not in doc:
                    issues.append("Not Google style (missing Args section)")

            # ---- NumPy style check ----
            elif style == "numpy":
                if "Parameters" not in doc:
                    issues.append("Not NumPy style (missing Parameters section)")

            # ---- reST style check ----
            elif style == "rest":
                if ":param" not in doc:
                    issues.append("Not reST style (missing :param)")

        # ✅ Final decision
        if issues:
            return {
                "status": "FIX",
                "reason": issues[0],     # backward compatible
                "issues": issues         # ✅ NEW (for UI)
            }

        return {
            "status": "OK",
            "reason": "Docstring valid",
            "issues": []               # ✅ ALWAYS PRESENT
        }