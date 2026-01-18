import os
import ast

# ==========================================
# 1. CLASS FOR SYSTEM TESTS
# ==========================================
class PythonParser:
    def parse_file(self, file_path):
        """
        Method used by the System Tests.
        Returns a dictionary to satisfy test expectations.
        """
        if not os.path.exists(file_path):
             return {"file_path": file_path, "functions": [], "classes": []}
        
        with open(file_path, "r", encoding="utf-8") as f:
            return parse_code(f.read(), file_path)

# ==========================================
# 2. FUNCTION FOR MAIN_APP.PY
# ==========================================
def parse_path(path):
    """
    Scans a directory or file and returns a LIST OF DICTIONARIES.
    Used by: main_app.py
    """
    results = []
    files_to_scan = []

    # Get list of files
    if os.path.isfile(path):
        files_to_scan = [path]
    elif os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if f.endswith(".py"):
                    files_to_scan.append(os.path.join(root, f))

    # Parse each file
    for f_path in files_to_scan:
        try:
            with open(f_path, "r", encoding="utf-8") as file:
                # We return a pure DICTIONARY here so main_app.py can use file['file_path']
                data = parse_code(file.read(), f_path)
                results.append(data)
        except Exception:
            pass
            
    return results

#Helper function used by both
def parse_code(code, file_path):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"file_path": file_path, "functions": [], "classes": []}

    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Calculate complexity
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    complexity += 1

            doc = ast.get_docstring(node)
            
            functions.append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "returns": "None", 
                "has_docstring": bool(doc),
                "docstring": doc,
                "complexity": complexity,
                "start_line": node.lineno,
                "indent": node.col_offset
            })

    # CRITICAL: Returns a dict, NOT an object
    return {
        "file_path": file_path, 
        "functions": functions, 
        "classes": classes
    }