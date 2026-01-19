
# AI-Powered Code Reviewer and Quality Assistant

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![AI](https://img.shields.io/badge/AI-NLP-orange?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 📄 Project Description

The **AI-Powered Code Reviewer and Quality Assistant** is a comprehensive tool designed to automate the code review process for Python projects. Modern codebases evolve rapidly, and manual reviews can be time-consuming and error-prone. 

This project leverages **Static Analysis (AST)** and **Large Language Models (LLMs)** to analyze code for:
- **Code Quality:** Complexity, maintainability, and style adherence.
- **Documentation:** Missing docstrings and adherence to PEP-257 standards.
- **Bugs & Security:** Identifying potential vulnerabilities and logic errors.

The tool provides a user-friendly **Streamlit Dashboard** for visualizing metrics and an automated workflow to ensure high-quality code delivery.

---

## 🚀 Features

- **📂 Automated Code Scanning:** Recursively scans directories to parse Python files.
- **🧠 AI-Driven Feedback:** Uses LLMs to generate natural language explanations and fixes.
- **📊 Interactive Dashboard:** Visualizes file metrics, coverage, and issue distribution.
- **📝 Docstring Generation:** Automatically generates docstrings in **Google, NumPy, or reST** styles.
- **✅ Validation Engine:** Calculates a "Quality Score" (0-100%) based on linting rules.
- **🎨 Theme Support:** Includes multiple UI themes (Cotton Candy, Dark Mode, etc.) for better user experience.
- **📥 Data Export:** Export review logs and coverage reports to CSV or JSON.

---

## 🧠 Techniques Used

This project implements advanced AI and Software Engineering techniques:

### 1. Natural Language Processing (NLP)
- **Tokenization & Context Understanding:** Break down code snippets to understand logic and intent.
- **Semantic Analysis:** Goes beyond syntax to understand the *purpose* of functions and classes.

### 2. Prompt Engineering
- **Few-Shot Learning:** Customized prompt templates guide the LLM to generate code-specific output (e.g., specific docstring formats).
- **Context Awareness:** Prompts are dynamically constructed using the AST-parsed function metadata (arguments, returns, exceptions).

### 3. LLM-Based Text Generation
- **Automated Refactoring:** Generates corrected code snippets based on best practices.
- **Documentation Synthesis:** Creates human-readable summaries for complex algorithms.

---

## 🛠️ Tech Stack

### Programming Language
- **Python 3.9+**

### Libraries & Frameworks
- **Streamlit:** For the web-based user interface.
- **Pandas:** For data manipulation and metric calculation.
- **AST (Abstract Syntax Tree):** Standard library for static code analysis.
- **PyTest:** For unit testing the application.

### LLM Details
- **Model:** Transformer-based LLM (Configurable).
- **Integration:** The system is designed to be model-agnostic, capable of integrating with OpenAI GPT, Llama, or HuggingFace models via API.

---

## 📂 Project Structure

```bash

AI_POWERED_CHATBOT/
│
├── ai_powered/
│   ├── cli/
│   │   └── commands.py
│   │
│   ├── core/
│   │   ├── docstring_engine/
│   │   │   └── generator.py
│   │   │   └── llm_integration.py
│   │   │
│   │   ├── parser/
│   │   │   └── python_parser.py
│   │   │
│   │   ├── reporter/
│   │   │   └── coverage_reporter.py
│   │   │
│   │   ├── review_engine/
│   │   │   └── ai_review.py
│   │   │
│   │   └── validator/
│   │       └── validator.py
│
├── examples/
│   ├── sample_a.py
│   └── sample_b.py
│
├── storage/
│   ├── reports/
│   └── review_logs.json
│
├── tests/
│   └── test_parser.py
│
├── main_app.py        # Streamlit UI
├── pyproject.toml
├── requirements.txt
├── README.md
```
```
-----


💻 Installation Steps
1. Clone the repository
```bash
   git clone your_github_link
  cd AI_Powered_Code_Reviewer
```
2. Create and activate virtual environment
```bash
python -m venv ai_powered
ai_powered\Scripts\activate   # Windows
# source ai_powered/bin/activate  # Mac/Linux
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
▶️ How to Run the Project Locally
1. Run Streamlit Dashboard
```bash
streamlit run main_app.py
```

**2. Run Code Scan**
- Enter the project path in the sidebar.
- Click **Scan**.
- Review coverage and documentation status.

**3. Generate Docstrings**
- Select docstring style (Google, NumPy, reST).
- Preview **AI-generated docstrings**.
- Click **Accept** or **Reject** changes.

**4. Run Tests**
- Use the **Run Tests** button in the Dashboard.
- View real passed/failed results displayed as bar charts.

---

## 🎓 Certification Use Case (Infosys)

This project demonstrates:
- **Practical use of AI and LLMs** in software engineering.
- **Real-world application** of NLP and prompt engineering.
- **Modular system design** and clean architecture.
- **Testing, validation, and metrics-driven** quality analysis.
- **Industry-ready Streamlit UI** for visualization.
- **CI-ready structure** suitable for enterprise workflows.

*It fully satisfies all four milestone requirements defined in the Infosys certification program.*

---

## 📜 License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute this software with attribution.

