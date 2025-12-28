# core/parser/python_parser.py

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class FunctionInfo:
    name: str
    lineno: int
    end_lineno: int
    has_docstring: bool
    raw_docstring: Optional[str] = None        # 🔹 ADDED
    args: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    complexity: int = 1
    max_nesting: int = 0
    is_method: bool = False
    parent_class: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    lineno: int
    end_lineno: int
    has_docstring: bool
    methods: List[FunctionInfo] = field(default_factory=list)


@dataclass
class ModuleInfo:
    path: str
    module_name: str
    has_docstring: bool
    imports: List[str] = field(default_factory=list)
    parsing_errors: List[str] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)


def _compute_complexity_and_nesting(node: ast.AST) -> Tuple[int, int]:
    """
    Very simple cyclomatic complexity + max nesting depth.
    Complexity: 1 + number of branching/loop nodes.
    Nesting: maximum depth of those nodes.
    """
    branch_types = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.BoolOp,
        ast.IfExp,
    )

    complexity = 1
    max_depth = 0

    def _walk(n: ast.AST, depth: int) -> None:
        nonlocal complexity, max_depth
        if isinstance(n, branch_types):
            complexity += 1
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(n):
            _walk(child, depth)

    _walk(node, 0)
    return complexity, max_depth


def _get_returns_annotation(node: ast.AST) -> Optional[str]:
    """Return a simple string representation of the return annotation, if any."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    if node.returns is None:
        return None
    try:
        return ast.unparse(node.returns)  # type: ignore[attr-defined]
    except Exception:
        if isinstance(node.returns, ast.Name):
            return node.returns.id
        return None


class PythonParser:
    """
    Parses Python files using the ast module and extracts:
    - Module docstring
    - Imports
    - Classes and their methods
    - Top-level functions, with line numbers, args, returns, complexity, nesting
    """

    def parse_file(self, file_path: str) -> ModuleInfo:
        path_obj = Path(file_path)
        try:
            source = path_obj.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ModuleInfo(
                path=str(path_obj),
                module_name=path_obj.stem,
                has_docstring=False,
                parsing_errors=[f"File not found: {file_path}"],
            )

        try:
            tree = ast.parse(source)
            parsing_errors: List[str] = []
        except SyntaxError as exc:
            return ModuleInfo(
                path=str(path_obj),
                module_name=path_obj.stem,
                has_docstring=False,
                parsing_errors=[f"SyntaxError: {exc}"],
            )

        module_docstring = ast.get_docstring(tree)
        has_module_docstring = bool(module_docstring)

        imports: List[str] = []
        classes: List[ClassInfo] = []
        functions: List[FunctionInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                for alias in node.names:
                    if module_name:
                        imports.append(f"{module_name}.{alias.name}")
                    else:
                        imports.append(alias.name)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(self._parse_class(node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(
                    self._parse_function(
                        node,
                        is_method=False,
                        parent_class=None,
                    )
                )

        return ModuleInfo(
            path=str(path_obj),
            module_name=path_obj.stem,
            has_docstring=has_module_docstring,
            imports=imports,
            parsing_errors=parsing_errors,
            classes=classes,
            functions=functions,
        )

    def parse_directory(self, directory: str) -> List[ModuleInfo]:
        base_path = Path(directory)
        modules: List[ModuleInfo] = []

        for py_file in base_path.rglob("*.py"):
            if ".venv" in py_file.parts or "venv" in py_file.parts:
                continue
            modules.append(self.parse_file(str(py_file)))

        return modules

    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        class_docstring = ast.get_docstring(node)
        has_docstring = bool(class_docstring)
        methods: List[FunctionInfo] = []

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(
                    self._parse_function(
                        child,
                        is_method=True,
                        parent_class=node.name,
                    )
                )

        end_lineno = getattr(node, "end_lineno", node.lineno)

        return ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=end_lineno,
            has_docstring=has_docstring,
            methods=methods,
        )

    def _parse_function(
        self,
        node: ast.AST,
        is_method: bool,
        parent_class: Optional[str],
    ) -> FunctionInfo:
        func_node = node
        func_docstring = ast.get_docstring(func_node)
        has_docstring = bool(func_docstring)

        args: List[str] = []
        if isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in func_node.args.args:
                if is_method and arg.arg in ("self", "cls"):
                    continue
                args.append(arg.arg)

        returns = _get_returns_annotation(func_node)
        complexity, max_nesting = _compute_complexity_and_nesting(func_node)
        end_lineno = getattr(func_node, "end_lineno", func_node.lineno)

        return FunctionInfo(
            name=func_node.name,
            lineno=func_node.lineno,
            end_lineno=end_lineno,
            has_docstring=has_docstring,
            raw_docstring=func_docstring,   # 🔹 ADDED
            args=args,
            returns=returns,
            complexity=complexity,
            max_nesting=max_nesting,
            is_method=is_method,
            parent_class=parent_class,
        )