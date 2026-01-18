"""
LLM integration for docstring generation.

- Generates COMPLETE docstring using LLM only
- No templates
- No placeholders
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()


def generate_docstring_content(fn: dict) -> str:
    """
    Generate a FULL Python docstring using LLM.
    Returns a string wrapped in triple quotes.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=api_key
    )

    # ✅ SAFE ARG EXTRACTION (THIS FIXES YOUR ERROR)
    raw_args = fn.get("args", [])
    arg_names = []

    for a in raw_args:
        if isinstance(a, dict):
            arg_names.append(a.get("name"))
        elif isinstance(a, str):
            arg_names.append(a)

    prompt = f"""
Write a complete Python docstring for the following function.

Rules:
- Follow standard Python docstring conventions
- Include parameters, returns, and raises ONLY if applicable
- Do NOT use placeholders like TYPE or DESCRIPTION
- Do NOT include markdown
- Return ONLY the docstring wrapped in triple quotes
- Be concise and professional

Function name: {fn.get("name")}
Arguments: {arg_names}
Return type: {fn.get("returns")}
Raises: {fn.get("raises", [])}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content.strip()