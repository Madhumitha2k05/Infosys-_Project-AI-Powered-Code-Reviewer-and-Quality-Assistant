import sys
from pathlib import Path

from core.parser.python_parser import PythonParser
from core.validator.validator import DocstringValidator


def run_validation(path: str, style: str = "google"):
    """
    Run docstring validation from CLI.
    """
    parser = PythonParser()
    modules = parser.parse_directory(path)

    print("\n🔍 Docstring Validation Report\n")

    for module in modules:
        print(f"📄 {Path(module.path).name}")

        functions = []
        functions.extend(module.functions)
        for cls in module.classes:
            functions.extend(cls.methods)

        for fn in functions:
            result = DocstringValidator.validate(fn, style)
            status = result["status"]
            reason = result["reason"]

            icon = "🟢" if status == "OK" else "🔴"
            print(f"  {icon} {fn.name} → {status} ({reason})")

        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m ai_powered.cli.commands <path> [style]")
        sys.exit(1)

    scan_path = sys.argv[1]
    doc_style = sys.argv[2] if len(sys.argv) > 2 else "google"

    run_validation(scan_path, doc_style)