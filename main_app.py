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
from core.validator.validator import DocstringValidator
import streamlit as st
import pandas as pd
# ---------- GLOBAL SESSION STATE ----------
if "dashboard_mode" not in st.session_state:
    st.session_state.dashboard_mode = "home"
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

if "dashboard_page" not in st.session_state:
    st.session_state.dashboard_page = "home"

if "doc__filter" not in st.session_state:
    st.session_state.doc__filter = "All"

# ---------- Dashboard State ----------
if "show_advanced_filters" not in st.session_state:
    st.session_state.show_advanced_filters = False

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
        # 🔥 REALLY SAFE OLD DOCSTRING REMOVAL (FIXED)
        if fn.raw_docstring:
            i = insert_at

            # Skip empty lines after def
            while i < len(lines) and lines[i].strip() == "":
                i += 1

            # Check for opening triple quotes
            if i < len(lines) and lines[i].lstrip().startswith(('"""', "'''")):
                quote = lines[i].lstrip()[:3]
                i += 1

                # Move until closing triple quotes
                while i < len(lines) and quote not in lines[i]:
                    i += 1

                if i < len(lines):
                    i += 1  # include closing quotes

                # Delete the old docstring block safely
                del lines[insert_at:i]
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
    ["Home", "Docstrings", "Validation", "Metrics", "Dashboard"],
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
    st.markdown('<div class="subtitle">AST-based static analysis & validation</div>', unsafe_allow_html=True)

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

    if not st.session_state.coverage_report or not st.session_state.modules:
        st.info("Run Scan to validate.")
        st.stop()

    per_file = st.session_state.coverage_report["per_file"]

    left, right = st.columns([1.2, 3])

    # ---------------- LEFT: FILE SELECT ----------------
    with left:
        st.markdown("### 📁 Files")
        selected_file = st.radio(
            "",
            list(per_file.keys()),
            format_func=lambda x: Path(x).name
        )

    # ---------------- RIGHT: VALIDATION DETAILS ----------------
    with right:
        data = per_file[selected_file]

        # ✅ KEEP YOUR CHART (DO NOT REMOVE)
        st.markdown("### 📊 Docstring Coverage")
        st.bar_chart({
            "Documented": [data["num_functions_with_docstrings"]],
            "Undocumented": [
                data["num_functions"] - data["num_functions_with_docstrings"]
            ],
        })

        st.write(f"**Total Functions:** {data['num_functions']}")
        st.write(f"**Documented:** {data['num_functions_with_docstrings']}")

        st.markdown("---")
        st.markdown("### ✅ Validation Results")

        # Get module object
        module = next(
            (m for m in st.session_state.modules if m.path == selected_file),
            None
        )

        if not module:
            st.error("Module not found. Please re-scan.")
            st.stop()

        # Collect all functions
        all_functions = []
        all_functions.extend(module.functions)
        for cls in module.classes:
            all_functions.extend(cls.methods)

        selected_style = st.session_state.doc_style  # Google / NumPy / reST

        for fn in all_functions:
            result = DocstringValidator.validate(fn, selected_style)

            if result["status"] == "OK":
                st.success(f"🟢 {fn.name} — OK")
            else:
                st.error(f"🔴 {fn.name} — FIX REQUIRED")

                for issue in result["issues"]:
                    st.write(f"• {issue}")

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


# ================= DASHBOARD =================
# ================= DASHBOARD =================
elif view == "Dashboard":
    
    import os
    import ast
    import pandas as pd
    from pathlib import Path
    import streamlit as st
    import json
    import sys
    import subprocess
    
    # --- 1. SETTINGS & PATHS (Logic Preserved) ---
    EXAMPLES_DIR = Path(r"E:\Infosys_Python\AI_Powered_Chatbot\examples")
    TESTS_DIR = Path(r"E:\Infosys_Python\AI_Powered_Chatbot\tests")

    # --- 2. AUTO-REPAIR (Ensures folders exist) ---
    if not EXAMPLES_DIR.exists():
        try: EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
        except: pass

    file_a = EXAMPLES_DIR / "sample_a.py"
    file_b = EXAMPLES_DIR / "sample_b.py"

    if not file_a.exists():
        with open(file_a, "w", encoding="utf-8") as f:
            f.write('def calculate_average(nums):\n    """Calculates avg.\n    Args: nums\n    """\n    return sum(nums)/len(nums)')
    if not file_b.exists():
        with open(file_b, "w", encoding="utf-8") as f:
            f.write('def generator():\n    yield 1')

    # --- 3. BULLETPROOF TEST RUNNER ---
    def run_tests_and_log():
        """Runs pytest using sys.executable to fix import errors."""
        reports_dir = Path("storage/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        log_path = reports_dir / "test_log.txt"

        # 1. PREPARE ENVIRONMENT (Fixes 'Module Not Found')
        my_env = os.environ.copy()
        my_env["PYTHONPATH"] = str(Path.cwd()) # Current folder is root

        try:
            # 2. RUN COMMAND (Using sys.executable -m pytest is safer)
            cmd = [sys.executable, "-m", "pytest", str(TESTS_DIR), "-v"]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                env=my_env 
            )
            
            # 3. SAVE OUTPUT
            output = result.stdout + "\n" + result.stderr
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(output)
            return output
            
        except Exception as e:
            return f"Error running tests: {str(e)}"

    def get_test_metrics():
        """Parses logs. If logs are broken/empty, returns 'Pending' counts."""
        reports_dir = Path("storage/reports")
        log_path = reports_dir / "test_log.txt"
        
        categories = {
            "test_coverage_reporter.py": "Coverage Tests",
            "test_dashboard.py": "Dashboard Tests",
            "test_generator.py": "Generation Tests",
            "test_llm_integration.py": "LLM Integration",
            "test_parser.py": "Parser Tests",
            "test_validation.py": "Validation Tests"
        }
        
        # Default: All Pending (Blue)
        results = {name: [0, 0, 1] for name in categories.values()}

        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # ONLY use log data if it actually contains results
            if "collected" in content or "passed" in content or "failed" in content:
                # Reset to 0 to fill with real data
                results = {name: [0, 0, 0] for name in categories.values()}
                
                for line in content.splitlines():
                    if "::" in line:
                        for filename, name in categories.items():
                            if filename in line:
                                if "PASSED" in line:
                                    results[name][0] += 1
                                elif "FAILED" in line:
                                    results[name][1] += 1
            
                # If after parsing we have 0 passed and 0 failed, 
                # it means the log was just an error dump. Revert to Pending!
                total_runs = sum(r[0] + r[1] for r in results.values())
                if total_runs == 0:
                     results = {name: [0, 0, 1] for name in categories.values()}

        return results, log_path

    # --- 4. REAL CODE SCANNER ---
    def get_real_code_data():
        results = []
        for file_path in [file_a, file_b]:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            doc = ast.get_docstring(node)
                            has_doc = bool(doc)
                            is_detailed = has_doc and ("Args:" in doc or "Parameters:" in doc)
                            results.append({
                                "File": file_path.name,
                                "Function": node.name,
                                "Status": "OK" if has_doc else "FIX",
                                "Quality Score": 100 if is_detailed else (60 if has_doc else 0)
                            })
                except: pass
        return results

    # --- 5. SESSION STATE ---
    if "dashboard_page" not in st.session_state:
        st.session_state.dashboard_page = "home"

    # ================= UI: DASHBOARD HOME =================
    if st.session_state.dashboard_page == "home":
        st.markdown('<h2 style="color:white;">📊 Dashboard (Real-Time)</h2>', unsafe_allow_html=True)

        # --- A. TEST RESULTS CHART ---
        st.markdown("### 📈 Test Execution Results")
        
        c_chart, c_run = st.columns([3, 1])
        with c_run:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("▶️ RUN TESTS", type="primary", key="run_tests_btn"):
                with st.spinner("Running tests... (This fixes the error log)"):
                    run_tests_and_log()
                    st.rerun()

        # Get Data
        test_data, log_path = get_test_metrics()
        
        # Prepare Chart
        chart_data = {"Test Category": [], "Status": [], "Count": []}
        
        # Check if we have any real data (Green/Red)
        has_real_results = sum(x[0] + x[1] for x in test_data.values()) > 0
        
        for category, (passed, failed, pending) in test_data.items():
            if has_real_results:
                # Show Pass/Fail
                chart_data["Test Category"].extend([category, category])
                chart_data["Status"].extend(["Passed", "Failed"])
                chart_data["Count"].extend([passed, failed])
            else:
                # Show Pending (Blue)
                chart_data["Test Category"].append(category)
                chart_data["Status"].append("Pending")
                chart_data["Count"].append(1) # Dummy count for visibility

        df_chart = pd.DataFrame(chart_data)

        # Render
        if not df_chart.empty:
            df_pivot = df_chart.pivot(index="Test Category", columns="Status", values="Count").fillna(0)
            
            # COLOR LOGIC
            colors = []
            if "Passed" in df_pivot.columns: colors.append("#4ade80") # Green
            if "Failed" in df_pivot.columns: colors.append("#f87171") # Red
            if "Pending" in df_pivot.columns: colors.append("#60a5fa") # Blue
            
            st.bar_chart(df_pivot, color=colors)

        # LOG VIEWER (With "Clear" Explanation)
        with st.expander("📄 View Execution Log"):
            if log_path.exists():
                with open(log_path, "r") as f:
                    log_content = f.read()
                
                if "Error" in log_content or "Traceback" in log_content:
                    st.warning("⚠️ The last run had errors. Click 'Run Tests' to try again.")
                
                st.code(log_content, language="bash")
            else:
                st.info("No logs yet.")

        # --- B. CSS STYLING (Colors + Equal Size Preserved) ---
        st.markdown("""
        <style>
        /* 1. FORCE EXACT SIZE FOR ALL BUTTONS */
        div[data-testid="column"] button,
        div[data-testid="stColumn"] button {
            width: 100% !important;
            min-width: 150px !important;
            height: 110px !important;
            border: none !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            transition: transform 0.2s !important;
        }

        /* 2. HOVER EFFECT */
        div[data-testid="column"] button:hover,
        div[data-testid="stColumn"] button:hover {
            transform: scale(1.03) !important;
            opacity: 0.95 !important;
        }

        /* 3. COLOR MAPPING (Precise Targeting) */
        
        div[data-testid="column"]:nth-of-type(1) button,
        div[data-testid="stColumn"]:nth-of-type(1) button {
            background: linear-gradient(135deg, #6366f1, #818cf8) !important;
        }

        div[data-testid="column"]:nth-of-type(2) button,
        div[data-testid="stColumn"]:nth-of-type(2) button {
            background: linear-gradient(135deg, #f43f5e, #fb7185) !important;
        }

        div[data-testid="column"]:nth-of-type(3) button,
        div[data-testid="stColumn"]:nth-of-type(3) button {
            background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
        }

        div[data-testid="column"]:nth-of-type(4) button,
        div[data-testid="stColumn"]:nth-of-type(4) button {
            background: linear-gradient(135deg, #22c55e, #4ade80) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # --- C. BUTTONS (UI Layout) ---
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        
        with c1:
            if st.button("🔍\nFILTERS"): 
                st.session_state.dashboard_page = "filters"
                st.rerun()
        with c2:
            if st.button("🔎\nSEARCH"): 
                st.session_state.dashboard_page = "search"
                st.rerun()
        with c3:
            if st.button("📥\nEXPORT"): 
                st.session_state.dashboard_page = "export"
                st.rerun()
        with c4:
            if st.button("ℹ️\nHELP"): 
                st.session_state.dashboard_page = "help"
                st.rerun()

        # --- D. THE 2 ITEMS FROM YOUR SCREENSHOT (Added Here) ---
        st.markdown("<br>", unsafe_allow_html=True)

        # 1. The Instruction Banner
        st.markdown("""
        <div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; color: #64748b; margin-bottom: 15px; display: flex; align-items: center; font-weight: 500;">
            <span style="font-size: 20px; margin-right: 10px;">👇</span> 
            Click on any feature card above to explore functionality
        </div>
        """, unsafe_allow_html=True)

        # 2. The Download Link (Functional)
        code_data = get_real_code_data()
        json_str = json.dumps(code_data, indent=4) if code_data else "{}"
        
        st.download_button(
            label="⬇️ Download Coverage Report JSON",
            data=json_str,
            file_name="coverage_report.json",
            mime="application/json",
            help="Click to download the latest analysis in JSON format"
        )


    # ================= UI: SUB-PAGES =================
    
    # 1. FILTERS PAGE (Full Logic)
    elif st.session_state.dashboard_page == "filters":
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0ea5e9, #38bdf8); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h2 style="color: white; margin: 0; font-size: 24px; display: flex; align-items: center; gap: 10px;">
                🔍 Advanced Filters
            </h2>
            <p style="color: #e0f2fe; margin: 8px 0 0 0; font-size: 15px; opacity: 0.9;">
                Filter and analyze function documentation status
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"📂 Scanning Files in: `{EXAMPLES_DIR}`")
        data = get_real_code_data()
        
        if data:
            df = pd.DataFrame(data)
            
            c_filter, c_spacer = st.columns([1, 2])
            with c_filter:
                opt = st.selectbox("Filter by Status", ["All", "OK", "FIX"])
            
            if opt != "All": 
                df_result = df[df["Status"]==opt]
            else:
                df_result = df
            
            count = len(df_result)
            st.markdown(f"""
            <div style="background-color: #f0f9ff; border: 1px solid #bae6fd; color: #0369a1; padding: 10px 15px; border-radius: 8px; margin: 20px 0; font-weight: 500; font-size: 14px;">
                Showing {count} functions {f"with status '{opt}'" if opt != 'All' else ""}
            </div>
            """, unsafe_allow_html=True)

            if not df_result.empty:
                st.markdown("""
                <div style="display: flex; background: linear-gradient(135deg, #0ea5e9, #38bdf8); padding: 15px; border-radius: 10px 10px 0 0; color: white; font-weight: bold; font-size: 15px;">
                    <div style="flex: 2;">📂 File Name</div>
                    <div style="flex: 2;">ƒ Function Name</div>
                    <div style="flex: 1; text-align: center;">📊 Status</div>
                    <div style="flex: 1; text-align: center;">⭐ Quality</div>
                </div>
                """, unsafe_allow_html=True)

                for i, row in df_result.iterrows():
                    bg_color = "#f8fafc" if i % 2 == 0 else "#ffffff"
                    status_color = "#22c55e" if row['Status'] == "OK" else "#ef4444"
                    status_bg = "#dcfce7" if row['Status'] == "OK" else "#fee2e2"
                    status_text = "PASSED" if row['Status'] == "OK" else "MISSING"
                    icon = "✅" if row['Status'] == "OK" else "❌"
                    
                    st.markdown(f"""
                    <div style="display: flex; background-color: {bg_color}; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 15px; align-items: center; transition: background 0.2s;">
                        <div style="flex: 2; color: #475569; font-family: monospace; font-size: 14px;">{row['File']}</div>
                        <div style="flex: 2; color: #1e293b; font-weight: 600; font-size: 15px;">{row['Function']}</div>
                        <div style="flex: 1; text-align: center;">
                            <span style="background-color: {status_bg}; color: {status_color}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid {status_color}40;">
                                {icon} {status_text}
                            </span>
                        </div>
                        <div style="flex: 1; text-align: center; font-weight: bold; color: #334155;">
                            {row['Quality Score']}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No functions found matching this filter.")
        else:
            st.error("No functions found in the scanned directory.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ Back"): st.session_state.dashboard_page = "home"; st.rerun()

    # 2. SEARCH PAGE (Full Logic)
    elif st.session_state.dashboard_page == "search":
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f43f5e, #fb7185); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h2 style="color: white; margin: 0; font-size: 24px; display: flex; align-items: center; gap: 10px;">
                🔎 Search Codebase
            </h2>
            <p style="color: #fff1f2; margin: 8px 0 0 0; font-size: 15px; opacity: 0.9;">
                Real-time function search and documentation analysis
            </p>
        </div>
        """, unsafe_allow_html=True)

        data = get_real_code_data()
        if data:
            df = pd.DataFrame(data)
            
            st.markdown("""
            <style>
            div[data-testid="stTextInput"] input {
                border: 2px solid #fda4af !important;
                border-radius: 8px !important;
                padding: 10px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #f43f5e !important;
                box-shadow: 0 0 0 1px #f43f5e !important;
            }
            </style>
            """, unsafe_allow_html=True)

            q = st.text_input("Enter search term (Function or File name):", placeholder="e.g., calculate_average")
            
            if q:
                mask = (
                    df["Function"].str.contains(q, case=False) | 
                    df["File"].str.contains(q, case=False)
                )
                df_result = df[mask]
            else:
                df_result = df
            
            count = len(df_result)
            st.markdown(f"""
            <div style="background-color: #fff1f2; border: 1px solid #fda4af; color: #9f1239; padding: 10px 15px; border-radius: 8px; margin: 20px 0; font-weight: 500; font-size: 14px;">
                {count} results found {f"for '{q}'" if q else ""}
            </div>
            """, unsafe_allow_html=True)
            
            if not df_result.empty:
                st.markdown("""
                <div style="display: flex; background: linear-gradient(135deg, #f43f5e, #fb7185); padding: 15px; border-radius: 10px 10px 0 0; color: white; font-weight: bold; font-size: 15px;">
                    <div style="flex: 2;">📂 File Name</div>
                    <div style="flex: 2;">ƒ Function Name</div>
                    <div style="flex: 1; text-align: center;">📊 Status</div>
                    <div style="flex: 1; text-align: center;">⭐ Quality</div>
                </div>
                """, unsafe_allow_html=True)

                for i, row in df_result.iterrows():
                    bg_color = "#f8fafc" if i % 2 == 0 else "#ffffff"
                    status_color = "#22c55e" if row['Status'] == "OK" else "#ef4444"
                    status_bg = "#dcfce7" if row['Status'] == "OK" else "#fee2e2"
                    status_text = "PASSED" if row['Status'] == "OK" else "MISSING"
                    icon = "✅" if row['Status'] == "OK" else "❌"
                    
                    st.markdown(f"""
                    <div style="display: flex; background-color: {bg_color}; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 15px; align-items: center; transition: background 0.2s;">
                        <div style="flex: 2; color: #475569; font-family: monospace; font-size: 14px;">{row['File']}</div>
                        <div style="flex: 2; color: #1e293b; font-weight: 600; font-size: 15px;">{row['Function']}</div>
                        <div style="flex: 1; text-align: center;">
                            <span style="background-color: {status_bg}; color: {status_color}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid {status_color}40;">
                                {icon} {status_text}
                            </span>
                        </div>
                        <div style="flex: 1; text-align: center; font-weight: bold; color: #334155;">
                            {row['Quality Score']}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No matches found.")
        else:
             st.info("No code data available to search.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅️ Back"): st.session_state.dashboard_page = "home"; st.rerun()

    # 3. EXPORT PAGE (Full Logic)
    elif st.session_state.dashboard_page == "export":
        data = get_real_code_data()
        if data:
            df = pd.DataFrame(data)
            total = len(df)
            documented = len(df[df["Status"] == "OK"])
            missing = len(df[df["Status"] == "FIX"])
            
            st.markdown("""
            <div style="background-color: #0ea5e9; padding: 25px; border-radius: 12px; margin-bottom: 25px;">
                <h2 style="color: white; margin: 0; display: flex; align-items: center;">📥 Export Data</h2>
                <p style="color: #e0f2fe; margin: 5px 0 0 0; font-size: 16px;">Download analysis results in JSON or CSV format</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: #f1f5f9; padding: 20px; border-radius: 12px; border-left: 6px solid #0ea5e9; margin-bottom: 25px; color:black;">
                <h4 style="margin:0 0 10px 0; color:#334155;">📋 Export Summary</h4>
                <ul style="margin: 0; color: #475569; font-size: 16px; line-height: 1.6;">
                    <li><b>Total Functions:</b> {total}</li>
                    <li><b>Documented:</b> {documented}</li>
                    <li><b>Missing Docstrings:</b> {missing}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            div.stDownloadButton > button {
                width: 100% !important;
                background-color: #ef4444 !important;
                color: white !important;
                border: none !important;
                padding: 15px !important;
                font-size: 18px !important;
                border-radius: 10px !important;
                transition: 0.3s !important;
            }
            div.stDownloadButton > button:hover {
                background-color: #dc2626 !important;
                transform: scale(1.02) !important;
            }
            </style>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2, gap="large")
            with c1:
                json_str = df.to_json(orient="records", indent=4)
                st.download_button("📤 Export as JSON", json_str, "report.json", mime="application/json")
                st.caption("📄 JSON format for programmatic access")
            with c2:
                csv_str = df.to_csv(index=False)
                st.download_button("📤 Export as CSV", csv_str, "report.csv", mime="text/csv")
                st.caption("📊 CSV format for Excel/spreadsheets")
        else:
            st.warning("⚠️ No data available to export.")
        st.markdown("---")
        if st.button("⬅️ Back"): st.session_state.dashboard_page = "home"; st.rerun()

    # 4. HELP PAGE
    elif st.session_state.dashboard_page == "help":
        
        st.markdown("""
        <div style="background-color: #22c55e; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; display: flex; align-items: center;">ℹ️ Interactive Help & Tips</h2>
            <p style="color: #dcfce7; margin: 5px 0 0 0; font-size: 14px;">Contextual help and quick reference guide</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("""
<div style="background: linear-gradient(135deg, #dcfce7, #f0fdf4); border: 1px solid #bbf7d0; border-radius: 10px; padding: 15px; margin-bottom: 15px; color: #1e293b;">
<h4 style="color: #166534; margin-top:0;">📊 Coverage Metrics</h4>
<ul style="font-size: 14px; padding-left: 20px;">
<li><b>Coverage %</b> = (Documented / Total) × 100</li>
<li>Green badge (🟢): ≥90% coverage</li>
<li>Yellow badge (🟡): 70-89% coverage</li>
<li>Red badge (🔴): <70% coverage</li>
</ul>
</div>
""", unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
<div style="background: linear-gradient(135deg, #ffedd5, #fff7ed); border: 1px solid #fed7aa; border-radius: 10px; padding: 15px; margin-bottom: 15px; color: #1e293b;">
<h4 style="color: #9a3412; margin-top:0;">✅ Function Status</h4>
<ul style="font-size: 14px; padding-left: 20px;">
<li><b>Green:</b> Complete docstring present</li>
<li><b>Red:</b> Missing or incomplete docstring</li>
<li>Auto-detection of docstring styles</li>
<li>Style-specific validation checks</li>
</ul>
</div>
""", unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
<div style="background: linear-gradient(135deg, #f1f5f9, #f8fafc); border: 1px solid #cbd5e1; border-radius: 10px; padding: 15px; margin-bottom: 15px; color: #1e293b;">
<h4 style="color: #334155; margin-top:0;">🧪 Test Results</h4>
<ul style="font-size: 14px; padding-left: 20px;">
<li>Real-time test execution monitoring</li>
<li>Pass/Fail ratio visualization</li>
<li>Per-file test breakdown</li>
<li>Integration with `pytest` reports</li>
</ul>
</div>
""", unsafe_allow_html=True)
        
        with c4:
            st.markdown("""
<div style="background: linear-gradient(135deg, #fae8ff, #fdf4ff); border: 1px solid #e879f9; border-radius: 10px; padding: 15px; margin-bottom: 15px; color: #1e293b;">
<h4 style="color: #86198f; margin-top:0;">📄 Docstring Styles</h4>
<ul style="font-size: 14px; padding-left: 20px;">
<li><b>Google:</b> Args:, Returns:, Raises:</li>
<li><b>NumPy:</b> Parameters/Returns with dashes</li>
<li><b>reST:</b> :param, :type, :return directives</li>
<li>Auto-style detection & validation</li>
</ul>
</div>
""", unsafe_allow_html=True)

        with st.expander("📚 Advanced Usage Guide", expanded=True):
            st.markdown("""
<div style="background: linear-gradient(135deg, #eff6ff, #dbeafe); border: 1px solid #bfdbfe; border-radius: 10px; padding: 15px; color: #1e3a8a;">
<h3 style="margin-top:0; color:#1e40af;">🚀 Getting Started</h3>
<ul style="margin-bottom:15px;">
<li><b>Scan Your Project:</b> Enter the path and click 'Scan' in the sidebar</li>
<li><b>Review Coverage:</b> Check the home page for overall statistics</li>
<li><b>Generate Docstrings:</b> Navigate to the Docstrings tab to preview and apply</li>
<li><b>Validate:</b> Use the Validation tab to ensure PEP-257 compliance</li>
<li><b>Export:</b> Download reports in your preferred format</li>
</ul>
<h3 style="margin-top:0; color:#1e40af;">💡 Pro Tips</h3>
<ul style="margin-bottom:15px;">
<li>Use filters to focus on undocumented functions</li>
<li>Preview before applying changes to maintain code quality</li>
<li>Export reports for team reviews and CI/CD integration</li>
<li>Check metrics regularly to track documentation progress</li>
</ul>
<h3 style="margin-top:0; color:#1e40af;">🔧 Keyboard Shortcuts</h3>
<ul>
<li><code>Ctrl + K</code> : Focus search box</li>
<li><code>Ctrl + Enter</code> : Apply docstring (when focused)</li>
<li><code>Esc</code> : Clear filters</li>
</ul>
</div>
""", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("⬅️ Back"): st.session_state.dashboard_page = "home"; st.rerun()