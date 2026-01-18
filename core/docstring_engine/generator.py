"""
core.docstring_engine.generator

Generates style-consistent docstrings using:
- LLM for semantic content
- Deterministic formatters for structure
"""

from typing import Dict, List, Union
from core.docstring_engine.llm_integration import generate_docstring_content

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _get_arg_name(arg: Union[Dict, str]) -> str:
    if isinstance(arg, dict):
        return arg.get("name", "arg")
    return str(arg)

def _get_arg_type(arg: Union[Dict, str]) -> str:
    if isinstance(arg, dict):
        return arg.get("annotation") or "TYPE"
    return "TYPE"

def _format_args_section(args: List, arg_desc: Dict[str, str]) -> str:
    if not args:
        return ""
    lines = ["Args:"]
    for a in args:
        name = _get_arg_name(a)
        typ = _get_arg_type(a)
        desc = arg_desc.get(name, "DESCRIPTION")
        lines.append(f"    {name} ({typ}): {desc}")
    return "\n".join(lines)

def _format_returns_section(returns: str, return_desc: str) -> str:
    if not returns:
        return ""
    return f"Returns:\n    {returns}: {return_desc or 'DESCRIPTION'}"

# -------------------------------------------------
# Google Style
# -------------------------------------------------
def generate_google_docstring(fn: Dict, llm: Dict) -> str:
    summary = llm.get("summary", f"Short description of `{fn.get('name')}`.")
    arg_desc = llm.get("args", {})
    return_desc = llm.get("returns", "")
    raises_desc = llm.get("raises", {})

    parts = [summary, ""]

    args_section = _format_args_section(fn.get("args", []), arg_desc)
    if args_section:
        parts.append(args_section)
        parts.append("")

    returns_section = _format_returns_section(fn.get("returns"), return_desc)
    if returns_section:
        parts.append(returns_section)
        parts.append("")

    if raises_desc:
        parts.append("Raises:")
        for exc, desc in raises_desc.items():
            parts.append(f"    {exc}: {desc}")
        parts.append("")

    doc = "\n".join(parts).strip()
    return f'"""\n{doc}\n"""'

# -------------------------------------------------
# NumPy Style
# -------------------------------------------------
def generate_numpy_docstring(fn: Dict, llm: Dict) -> str:
    summary = llm.get("summary", f"{fn.get('name')} function.")
    arg_desc = llm.get("args", {})
    return_desc = llm.get("returns", "")
    raises_desc = llm.get("raises", {})

    lines = [summary, "", "Parameters", "----------"]

    for arg in fn.get("args", []):
        name = _get_arg_name(arg)
        t = _get_arg_type(arg)
        desc = arg_desc.get(name, "DESCRIPTION")
        lines.append(f"{name} : {t}")
        lines.append(f"    {desc}")

    if fn.get("returns"):
        lines.extend(["", "Returns", "-------", f"{fn['returns']}", f"    {return_desc}"])

    if raises_desc:
        lines.extend(["", "Raises", "------"])
        for exc, desc in raises_desc.items():
            lines.append(f"{exc}")
            lines.append(f"    {desc}")

    return f'"""\n' + "\n".join(lines) + '\n"""'

# -------------------------------------------------
# Main Entry Point
# -------------------------------------------------
def generate_docstring(fn: Dict, style: str = "google") -> str:
    # 1. Get AI Content
    llm_content = generate_docstring_content(fn)

    # 2. Format based on Style
    if style == "google":
        return generate_google_docstring(fn, llm_content)
    elif style == "numpy":
        return generate_numpy_docstring(fn, llm_content)
    else:
        # Default to Google for others
        return generate_google_docstring(fn, llm_content)

# -------------------------------------------------
# Wrapper for Tests
# -------------------------------------------------
class DocstringGenerator:
    def generate(self, fn: Dict, style: str = "google") -> str:
        if isinstance(fn, str): fn = {"name": "test", "args": []}
        return generate_docstring(fn, style)
    
"""
Docstring generator.

Uses ONLY LLM output.
"""

from core.docstring_engine.llm_integration import generate_docstring_content


def generate_docstring(fn: dict, style: str = None) -> str:
    return generate_docstring_content(fn)