"""
Madhumitha's AI Code Reviewer
Milestone 2 — AST-based static analysis & validation
"""

import json
import os
import sys
import difflib
from pathlib import Path
from typing import Dict, List, Optional
from core.docstring_engine.llm_integration import LLMDocstringGenerator

import streamlit as st

# ---------------------------------------------------------------------
# Ensure core imports
# ---------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Try-except to ensure imports work
try:
    from core.parser.python_parser import PythonParser, ModuleInfo, FunctionInfo
    from core.docstring_engine.generator import DocstringGenerator
    from core.reporter.coverage_reporter import DocstringCoverageReporter
except ImportError as e:
    st.error(f"Error importing core modules: {e}")
    st.stop()

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Madhumitha's AI Code Reviewer",
    layout="wide",
)

# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------
st.markdown("""
<style>
/* App Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    color: #e5e7eb;
}

/* Sidebar Background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #312e81;
}

/* Card Styling */
.card {
    background: linear-gradient(135deg,#020617,#0f172a);
    border-radius: 16px;
    padding: 1.6rem;
    border: 1px solid #312e81;
    margin-bottom: 1.2rem;
}

.metric-card {
    background: linear-gradient(135deg,#020617,#1e1b4b);
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    border: 1px solid #312e81;
}

.metric-card h3 {
    margin: 0;
    font-size: 1.8rem;
    color: #a78bfa;
}

.metric-card p {
    margin: 0;
    color: #c7d2fe;
}

/* Titles */
.title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #c7d2fe;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

/* Diff Box */
.diff {
    background-color: #020617;
    padding: 1rem;
    border-radius: 12px;
    font-family: monospace;
    font-size: 0.85rem;
    border: 1px solid #312e81;
}

/* Button Styling */
section[data-testid="stSidebar"] button {
    background: linear-gradient(90deg, #38bdf8, #a78bfa) !important;
    color: black !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------
if "project_path" not in st.session_state:
    st.session_state.project_path = "examples"

if "output_json" not in st.session_state:
    st.session_state.output_json = "storage/review_logs.json"

if "generate_baseline" not in st.session_state:
    st.session_state.generate_baseline = True

if "modules" not in st.session_state:
    st.session_state.modules: List[ModuleInfo] = []

if "coverage_report" not in st.session_state:
    st.session_state.coverage_report: Optional[Dict] = None

if "doc_style" not in st.session_state:
    st.session_state.doc_style = "Google"

# 🔥 FIX: Initialize specific state variables for selection
if "doc_file" not in st.session_state:
    st.session_state.doc_file = None
if "doc_fn" not in st.session_state:
    st.session_state.doc_fn = None

if "llm" not in st.session_state:
    try:
        st.session_state.llm = LLMDocstringGenerator()
    except Exception:
        st.session_state.llm = None
# ---------------------------------------------------------------------
# SCAN LOGIC
# ---------------------------------------------------------------------
def run_scan():
    parser = PythonParser()
    path_to_scan = str(Path(st.session_state.project_path).resolve())
    
    if os.path.exists(path_to_scan):
        modules = parser.parse_directory(path_to_scan)
        
        reporter = DocstringCoverageReporter()
        coverage = reporter.create_report(modules)

        suggestions = {}
        if st.session_state.generate_baseline:
            suggestions = DocstringGenerator.generate_missing_docstrings(modules)

        # Save to JSON
        out = Path(st.session_state.output_json)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                json.dumps({
                    "coverage_report": coverage,
                    "docstring_suggestions": suggestions,
                }, indent=4),
                encoding="utf-8"
            )
        except Exception:
            pass 

        st.session_state.modules = modules
        st.session_state.coverage_report = coverage
        return True
    return False

# ---------------------------------------------------------------------
# FILE WRITE LOGIC (UPDATES VS CODE)
# ---------------------------------------------------------------------
def apply_docstring_to_file(file_path: str, fn: FunctionInfo, new_doc: str):
    """
    Writes the docstring directly into the .py file (VS Code updates instantly).
    """
    if not new_doc:
        return

    path = Path(file_path)

    if not path.exists():
        st.error(f"File not found: {file_path}")
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()

        # AST lineno is 1-based
        def_index = fn.lineno - 1
        if def_index < 0 or def_index >= len(lines):
            return

        def_line = lines[def_index]

        # Detect indentation
        base_indent = def_line[:len(def_line) - len(def_line.lstrip())]
        doc_indent = base_indent + "    "

        # 🔥 IMPORTANT FIX:
        # Generator ALREADY contains """ → DO NOT add again
        doc_block = []
        for line in new_doc.splitlines():
            doc_block.append(doc_indent + line)
        doc_block.append("")  # blank line

        insert_at = def_index + 1

        # 🔥 SAFE OLD DOCSTRING REMOVAL
        if fn.raw_docstring:
            start = insert_at
            end = insert_at + len(fn.raw_docstring.splitlines()) + 2
            del lines[start:end]

        # 🔥 INSERT NEW DOCSTRING
        lines[insert_at:insert_at] = doc_block

        # 🔥 WRITE BACK TO FILE
        path.write_text("\n".join(lines), encoding="utf-8")

    except Exception as e:
        st.error(f"Failed to update file: {e}")

# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
st.sidebar.markdown("## 🧠 AI Code Reviewer")

view = st.sidebar.selectbox(
    "Select View",
    ["Home", "Docstrings", "Validation", "Metrics"],
    key="view_selector"
)

st.sidebar.text_input("Path to scan", key="project_path")
st.sidebar.text_input("Output JSON path", key="output_json")
st.sidebar.checkbox("Generate baseline docstrings", key="generate_baseline")

if st.sidebar.button("Scan"):
    if run_scan():
        st.sidebar.success("Scan completed successfully")
    else:
        st.sidebar.error("Invalid path")

# ---------------------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------------------
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ================= HOME =================
if view == "Home":
    st.markdown('<div class="title">AI-Powered Code Reviewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Milestone 2 · AST-based static analysis & validation</div>', unsafe_allow_html=True)

    report = st.session_state.coverage_report

    if report:
        summary = report["summary"]["functions_and_methods"]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><p>Overall Coverage</p><h3>{summary['coverage_percent']}%</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><p>Total Functions</p><h3>{summary['total']}</h3></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><p>Documented</p><h3>{summary['documented']}</h3></div>", unsafe_allow_html=True)

    if report:
        st.markdown("### 📁 File-wise Docstring Coverage")
        per_file = report["per_file"]
        for file_path, data in per_file.items():
            file_name = Path(file_path).name
            total = data["num_functions"]
            documented = data["num_functions_with_docstrings"]
            percent = round((documented / total) * 100, 2) if total else 100
            st.markdown(f"<div class='card'><b>{file_name}</b><br>Coverage: <b>{percent}%</b><br>Documented: {documented} / {total}</div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="card">
            <b>Important</b>
            <ul>
                <li>Coverage counts only actual code docstrings</li>
                <li>Coverage updates only after clicking ✅ Accept</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ================= DOCSTRINGS =================
# ================= DOCSTRINGS =================
elif view == "Docstrings":
    st.markdown('<div class="title">Docstring Review</div>', unsafe_allow_html=True)

    # -------------------------------------------------
    # Persistent UI State (🔥 FIX)
    # -------------------------------------------------
    if "doc_file" not in st.session_state:
        st.session_state.doc_file = None
    if "doc_fn" not in st.session_state:
        st.session_state.doc_fn = None

    # -------------------------------------------------
    # Docstring Style Selector
    # -------------------------------------------------
    st.markdown("### Docstring Styles")
    st.session_state.doc_style = st.radio(
        "",
        ["Google", "NumPy", "reST"],
        horizontal=True,
        key="doc_style_radio"
    )

    modules = st.session_state.modules

    if not modules:
        st.info("Please click 'Scan' in the sidebar first.")
        st.stop()

    # -------------------------------------------------
    # FILE SELECT (🔥 FIX: path-safe)
    # -------------------------------------------------
    file_paths = [str(Path(m.path)) for m in modules]

    if st.session_state.doc_file not in file_paths:
        st.session_state.doc_file = file_paths[0]

    selected_file = st.selectbox(
        "Files",
        file_paths,
        index=file_paths.index(st.session_state.doc_file),
        key="doc_file_select"
    )

    st.session_state.doc_file = selected_file

    module = next(
        (m for m in modules if str(Path(m.path)) == selected_file),
        None
    )

    if not module:
        st.warning("Module not found. Please re-scan.")
        st.stop()

    # -------------------------------------------------
    # COLLECT FUNCTIONS
    # -------------------------------------------------
    all_functions = []
    all_functions.extend(module.functions)
    for cls in module.classes:
        all_functions.extend(cls.methods)

    if not all_functions:
        st.info("This file has no functions. Select another file.")
        st.stop()

    fn_names = [fn.name for fn in all_functions]

    if st.session_state.doc_fn not in fn_names:
        st.session_state.doc_fn = fn_names[0]

    selected_fn = st.selectbox(
        "Functions",
        fn_names,
        index=fn_names.index(st.session_state.doc_fn),
        key="doc_fn_select"
    )

    st.session_state.doc_fn = selected_fn

    fn_obj = next(fn for fn in all_functions if fn.name == selected_fn)

    # -------------------------------------------------
    # DOCSTRINGS
    # -------------------------------------------------
    before_doc = fn_obj.raw_docstring or ""
    if st.session_state.llm:
        after_doc = st.session_state.llm.generate_docstring(
            fn_obj,
            style=st.session_state.doc_style
        )
    else:
        after_doc = DocstringGenerator.generate_function_docstring(fn_obj)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Before")
        st.code(
            before_doc if before_doc else "# No existing docstring",
            language="python"
        )

    with col2:
        st.markdown("### After (Preview)")
        st.code(after_doc, language="python")

    # -------------------------------------------------
    # DIFF VIEW
    # -------------------------------------------------
    st.markdown("### 🔍 Difference (Before vs After)")
    diff_text = "\n".join(difflib.unified_diff(
        before_doc.splitlines(),
        after_doc.splitlines(),
        fromfile="Before",
        tofile="After",
        lineterm=""
    ))

    st.code(
        diff_text if diff_text.strip() else "No changes detected",
        language="diff"
    )

    # -------------------------------------------------
    # ACTION BUTTONS (🔥 FIX: UNIQUE KEYS)
    # -------------------------------------------------
    st.markdown("### Actions")
    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "✅ Accept",
            key=f"accept_{selected_file}_{selected_fn}"
        ):
            apply_docstring_to_file(
                selected_file,
                fn_obj,
                after_doc
            )

            run_scan()  # refresh AST safely

            st.success("Docstring applied successfully ✔")
            st.rerun()

    with c2:
        if st.button(
            "❌ Reject",
            key=f"reject_{selected_file}_{selected_fn}"
        ):
            st.info("Suggestion rejected.")
            st.rerun()
# ================= VALIDATION =================
elif view == "Validation":
    st.markdown('<div class="title">📊 Validation</div>', unsafe_allow_html=True)
    if not st.session_state.coverage_report:
        st.info("Run Scan to validate.")
    else:
        per_file = st.session_state.coverage_report["per_file"]
        left, right = st.columns([1.2, 3])
        with left:
            st.markdown("### 📁 Files")
            selected = st.radio("", list(per_file.keys()), format_func=lambda x: Path(x).name)
        with right:
            data = per_file[selected]
            st.bar_chart({
                "Documented": [data["num_functions_with_docstrings"]],
                "Undocumented": [data["num_functions"] - data["num_functions_with_docstrings"]],
            })
            st.write(f"Total Functions: {data['num_functions']}")
            st.write(f"Documented: {data['num_functions_with_docstrings']}")

# ================= METRICS =================
elif view == "Metrics":
    st.markdown('<div class="title">📐 Code Metrics</div>', unsafe_allow_html=True)
    if st.session_state.modules:
        file_paths = [m.path for m in st.session_state.modules]
        selected_file = st.selectbox("Select File", file_paths)
        module = next(m for m in st.session_state.modules if m.path == selected_file)
        
        all_fns = []
        all_fns.extend(module.functions)
        for cls in module.classes:
            all_fns.extend(cls.methods)

        if all_fns:
            avg_comp = sum(f.complexity for f in all_fns) / len(all_fns)
            m_index = max(0, 100 - avg_comp * 10)
            st.markdown(f"<div class='metric-card'><p>Maintainability Index</p><h3>{round(m_index, 1)}</h3></div>", unsafe_allow_html=True)
            st.code(json.dumps([{"name": f.name, "complexity": f.complexity} for f in all_fns], indent=4), language="json")
    else:
        st.info("Run Scan first.")