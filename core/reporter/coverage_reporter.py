# core/reporter/coverage_reporter.py

"""
Compute docstring coverage and write report to JSON.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from core.parser.python_parser import ModuleInfo


class DocstringCoverageReporter:
    """Calculate summary and per-file docstring coverage."""

    # ---------- internal helpers ----------

    def _count_docstrings(self, modules: List[ModuleInfo]) -> Dict[str, Any]:
        module_total = len(modules)
        module_with = sum(1 for m in modules if m.has_docstring)

        class_total = 0
        class_with = 0
        func_total = 0
        func_with = 0

        for module in modules:
            for cls in module.classes:
                class_total += 1
                if cls.has_docstring:
                    class_with += 1

                for method in cls.methods:
                    func_total += 1
                    if method.has_docstring:
                        func_with += 1

            for func in module.functions:
                func_total += 1
                if func.has_docstring:
                    func_with += 1

        def percent(part: int, whole: int) -> float:
            return round((part / whole * 100.0), 2) if whole > 0 else 0.0

        return {
            "modules": {
                "total": module_total,
                "documented": module_with,
                "coverage_percent": percent(module_with, module_total),
            },
            "classes": {
                "total": class_total,
                "documented": class_with,
                "coverage_percent": percent(class_with, class_total),
            },
            "functions_and_methods": {
                "total": func_total,
                "documented": func_with,
                "coverage_percent": percent(func_with, func_total),
            },
        }

    # 🔹 NEW: validation issue generator
    def _collect_validation_issues(self, modules: List[ModuleInfo]) -> List[str]:
        issues: List[str] = []

        for module in modules:
            # D100: Missing module docstring
            if not module.has_docstring:
                issues.append(
                    f"{module.path}:1 D100 Missing docstring in public module"
                )

            # Classes
            for cls in module.classes:
                if not cls.has_docstring:
                    issues.append(
                        f"{module.path}:{cls.lineno} D101 Missing docstring in public class '{cls.name}'"
                    )

                for method in cls.methods:
                    if not method.has_docstring:
                        issues.append(
                            f"{module.path}:{method.lineno} D102 Missing docstring in public method '{method.name}'"
                        )

            # Functions
            for func in module.functions:
                if not func.has_docstring:
                    issues.append(
                        f"{module.path}:{func.lineno} D103 Missing docstring in public function '{func.name}'"
                    )

        return issues

    # ---------- public API ----------

    def create_report(self, modules: List[ModuleInfo]) -> Dict[str, Any]:
        """Return summary + per-file coverage info."""
        summary = self._count_docstrings(modules)
        per_file: Dict[str, Any] = {}

        for module in modules:
            per_file[module.path] = {
                "has_module_docstring": module.has_docstring,
                "num_classes": len(module.classes),
                "num_classes_with_docstrings": sum(1 for c in module.classes if c.has_docstring),
                "num_functions": len(module.functions) + sum(len(c.methods) for c in module.classes),
                "num_functions_with_docstrings": (
                    sum(1 for f in module.functions if f.has_docstring)
                    + sum(
                        1
                        for c in module.classes
                        for m in c.methods
                        if m.has_docstring
                    )
                ),
            }

        # 🔹 ADD validation issues
        issues = self._collect_validation_issues(modules)

        return {
            "summary": summary,
            "per_file": per_file,
            "issues": issues,   # 🔹 THIS is what Validation page needs
        }

    def save_report(self, report: Dict[str, Any], output_path: str) -> None:
        """Write report dict to a JSON file."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=4), encoding="utf-8")