###AI-Powered Code Reviewer and Quality Assistant

🧠 AI-Powered Code Reviewer and Quality Assistant
� � � �
#📌 Project Description
The AI-Powered Code Reviewer and Quality Assistant is an intelligent system designed to automatically analyze Python codebases and improve overall code quality.
It combines static code analysis, Large Language Models (LLMs), and developer-friendly interfaces to assist in reviewing, validating, and enhancing code.
The tool detects missing or incomplete docstrings, evaluates quality metrics, validates documentation standards, and generates professional docstrings using AI.
An optional Streamlit web dashboard allows developers to visually inspect results, accept or reject AI suggestions, and run tests interactively.
This solution reduces manual review effort while enforcing consistent coding and documentation standards.
✨ Features
Automatic parsing of Python source code using AST
AI-generated docstrings for functions and methods
Supports Google, NumPy, and reST docstring styles
Docstring validation using PEP-257 rules
Code metrics analysis (complexity, maintainability)
Automated test execution with real pass/fail results
Interactive Streamlit dashboard
CLI-friendly architecture for CI/CD workflows
Exportable JSON coverage and review reports
🧪 Techniques Used
🧠 Natural Language Processing (NLP)
Code understanding through syntax and structure analysis
Semantic interpretation of function behavior
🧩 Prompt Engineering
Structured prompts to enforce docstring standards
Style-specific rules for Google, NumPy, and reST formats
Controlled and consistent AI output
🤖 LLM-Based Text Generation
Human-readable, professional docstring generation
Content adapts dynamically to function logic
No hardcoded or predefined documentation text
🛠️ Tech Stack
Programming Language
Python 3.10+
Libraries / Frameworks
ast – static code analysis
streamlit – web dashboard UI
pytest – automated testing
difflib – diff visualization
pydocstyle – docstring validation
json, os, subprocess – system utilities
AI / ML Technologies
Transformer-based Large Language Models
Prompt-driven text generation
Modular LLM integration architecture
🤖 LLM Details
Uses transformer-based LLMs
LLM backend is fully configurable
Supports cloud-based or local LLM models
Model name, temperature, and prompts can be customized
LLM is used only for content generation, not formatting
📂 Project Structure
AI_Powered_Code_Reviewer/
├── core/
│   ├── parser/           # AST parsing logic
│   ├── docstring_engine/ # LLM docstring generation
│   ├── validator/        # PEP-257 validation
│   ├── reporter/         # Coverage and metrics reports
│   └── test_runner/      # Test execution logic
│
├── examples/             # Sample Python files
├── tests/                # Unit and integration tests
├── storage/              # Generated reports and logs
├── main_app.py           # Streamlit application
├── pyproject.toml        # Configuration and rules
├── README.md
└── requirements.txt
⚙️ Installation Steps
1️⃣ Clone the Repository
git clone your_github_link
cd AI_Powered_Code_Reviewer
2️⃣ Create and Activate Virtual Environment
python -m venv ai_powered
ai_powered\Scripts\activate   (Windows)
3️⃣ Install Dependencies
pip install -r requirements.txt
▶️ How to Run the Project Locally
Run Streamlit Dashboard
streamlit run main_app.py
Run Code Scan
Enter the project path
Click Scan
Review coverage and documentation status
Generate Docstrings
Select docstring style
Preview AI-generated docstrings
Accept or reject suggestions
Run Tests
Click Run Tests in the Dashboard
View real passed/failed results as bar charts
🎓 Certification Use Case (Infosys)
This project demonstrates:
Practical application of AI and LLMs in software engineering
Real-world use of NLP and prompt engineering
Modular, maintainable system design
Metrics-driven quality validation
Test execution and reporting
Industry-ready Streamlit UI
It fully satisfies all four milestones defined in the Infosys certification program.
📄 License
This project is licensed under the MIT License.
You are free to use, modify, and distribute this software with attribution.

🧩 Milestone-wise Q&A for mentor questions
Just tell me 😊

