import os
import pdfplumber
import google.generativeai as genai


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from an uploaded PDF file using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")


def _clean_code_response(result_text: str) -> str:
    """
    Remove markdown fences if the model wraps the code in triple backticks.
    """
    if not result_text:
        return result_text

    text = result_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines.startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return text


 def generate_code_from_text(paper_text: str, api_key: str) -> str:
    """
    Send extracted paper text to Gemini to generate Python code.
    """
    if not api_key or not api_key.strip():
        raise ValueError("GOOGLE_API_KEY is missing from environment variables.")

    try:
        # Configure the API key
        genai.configure(api_key=api_key.strip())

        # Create the model (use a real model code; 2.5‑flash is still in preview)
        model = genai.GenerativeModel("gemini-1.5-flash")  # or whatever you want

        prompt = f"""
You are an expert Python engineer.

Read the following research paper text and write ONLY working, runnable Python code that implements the core method described in the paper.

Requirements:
- Output only Python code.
- Include necessary imports.
- Add a small test/demo under if __name__ == "__main__":.
- Keep the implementation simple, clean, and practical.
- Do not add markdown, explanations, or surrounding text.

Research paper text:
{paper_text[:200000]}
"""

        # Generate content
        response = model.generate_content(prompt)

        result_text = response.text or ""
        return _clean_code_response(result_text)

    except Exception as e:
        raise Exception(f"Failed to generate code via LLM: {e}")