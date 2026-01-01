# core/docstring_engine/llm_integration.py

import os
from typing import Optional

from core.parser.python_parser import FunctionInfo

try:
    from groq import Groq
except ImportError:
    Groq = None


class LLMDocstringGenerator:
    """
    Uses Groq LLM to generate high-quality docstrings
    based on function signature and structure.
    """

    def __init__(self, api_key: Optional[str] = None):
        if Groq is None:
            raise ImportError("groq package not installed. Run: pip install groq")

        self.client = Groq(
            api_key=api_key or os.getenv("GROQ_API_KEY")
        )

    def generate_docstring(
        self,
        fn: FunctionInfo,
        style: str = "Google"
    ) -> str:
        """
        Generate an LLM-powered docstring for a function.
        """

        args = ", ".join(fn.args) if fn.args else "None"
        returns = "Returns a value" if fn.returns else "None"

        prompt = f"""
You are an expert Python developer.

Generate a HIGH-QUALITY {style}-style docstring.

Function name:
{fn.name}

Arguments:
{args}

Returns:
{returns}

Rules:
- Use proper {style} docstring format
- Be concise but clear
- Do NOT include code
- Do NOT repeat function name unnecessarily
- Use triple quotes
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You generate Python docstrings."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )

        docstring = response.choices[0].message.content.strip()

        # Safety cleanup
        if not docstring.startswith('"""'):
            docstring = f'"""\n{docstring}\n"""'

        return docstring