# core/docstring_engine/generator.py

"""
Generate baseline Google-style docstrings for modules, classes and functions.

This module is non-destructive: it only returns docstring text and does not
modify any code files.
"""

from typing import Dict, List

from core.parser.python_parser import ModuleInfo, ClassInfo, FunctionInfo


def _format_args_section(args: List[str]) -> str:
    """Return a Google-style Args section for a list of argument names."""
    if not args:
        return ""

    lines: List[str] = ["Args:"]
    for arg in args:
        lines.append(f"    {arg} (Any): Description of {arg}.")
    return "\n".join(lines)


def _format_returns_section() -> str:
    """Return a generic Google-style Returns section."""
    return "Returns:\n    Any: Description of return value."


class DocstringGenerator:
    """
    Generates baseline Google-style docstrings for modules, classes and functions.
    """

    @staticmethod
    def generate_module_docstring(module: ModuleInfo) -> str:
        """Generate a baseline module-level docstring."""
        return f'''"""Module {module.module_name}.

This module was automatically analyzed by the AI-Powered Code Reviewer tool.
Add a more detailed description here.
"""'''

    @staticmethod
    def generate_class_docstring(cls: ClassInfo) -> str:
        """Generate a baseline class docstring."""
        return f'''"""{cls.name} class.

Describe the purpose of this class and its main responsibilities.
"""'''

    @staticmethod
    def generate_function_docstring(func: FunctionInfo) -> str:
        """Generate a Google-style docstring for a function or method."""
        lines: List[str] = [f'"""{func.name} function.', ""]

        # Args section
        args_section = _format_args_section(func.args)
        if args_section:
            lines.append(args_section)
            lines.append("")

        # Returns section
        returns_section = _format_returns_section()
        lines.append(returns_section)
        lines.append("")
        lines.append('"""')

        return "\n".join(lines)

    @staticmethod
    def generate_missing_docstrings(modules: List[ModuleInfo]) -> Dict[str, Dict]:
        """
        For each module, return suggested docstrings for everything that has no
        docstring yet.

        Structure:
        {
            module_path: {
                "module": <str or None>,
                "classes": {class_name: docstring},
                "functions": {func_name: docstring},
                "methods": {"ClassName.method_name": docstring}
            },
            ...
        }
        """
        suggestions: Dict[str, Dict] = {}

        for module in modules:
            module_entry: Dict[str, Dict] = {
                "module": None,
                "classes": {},
                "functions": {},
                "methods": {},  # keys will be strings, safe for JSON
            }

            # Module docstring
            if not module.has_docstring:
                module_entry["module"] = DocstringGenerator.generate_module_docstring(module)

            # Classes and methods
            for cls in module.classes:
                if not cls.has_docstring:
                    module_entry["classes"][cls.name] = DocstringGenerator.generate_class_docstring(cls)

                for method in cls.methods:
                    if not method.has_docstring:
                        key = f"{cls.name}.{method.name}"  # string key (no JSON error)
                        module_entry["methods"][key] = DocstringGenerator.generate_function_docstring(method)

            # Top-level functions
            for func in module.functions:
                if not func.has_docstring:
                    module_entry["functions"][func.name] = DocstringGenerator.generate_function_docstring(func)

            suggestions[module.path] = module_entry

        return suggestions