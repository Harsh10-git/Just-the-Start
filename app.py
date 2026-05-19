import os
import streamlit as st
from dotenv import load_dotenv
from backend.processor import extract_text_from_pdf, generate_code_from_text
from utils.helpers import init_session_state, add_to_history

load_dotenv()

st.set_page_config(
    page_title="Automated Paper-to-Code Agent",
    page_icon="📄",
    layout="centered",
)

init_session_state()

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1117 0%, #151823 100%);
        color: #f5f7fb;
    }
    .hero {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .hero h1 {
        font-size: 2.7rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        color: #ffffff;
    }
    .hero p {
        font-size: 1.05rem;
        color: #c8ceda;
        margin: 0 auto;
        max-width: 820px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>📄 Automated Paper-to-Code Agent</h1>
        <p>Upload a research paper PDF and receive working Python code that implements the paper’s core method.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_a, col_b = st.columns([1, 1])

with col_a:
    uploaded_file = st.file_uploader("Upload research paper (PDF)", type=["pdf"])

with col_b:
    sample_clicked = st.button("Use Sample PDF", use_container_width=True)

if sample_clicked:
    sample_path = "samples/sample_paper.pdf"
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            st.session_state.sample_pdf_bytes = f.read()
        st.success("Sample PDF loaded. You can now generate code from it.")
    else:
        st.error("Sample PDF not found in samples/sample_paper.pdf")

if "current_code" not in st.session_state:
    st.session_state.current_code = None

if "sample_pdf_bytes" in st.session_state and st.session_state.sample_pdf_bytes:
    st.info("A sample PDF is selected. Uploading a new PDF will replace it.")

col1, col2 = st.columns([1, 1])

with col1:
    generate_clicked = st.button("Generate Code", type="primary", use_container_width=True)

with col2:
    reset_clicked = st.button("Reset Output", use_container_width=True)

if reset_clicked:
    st.session_state.current_code = None
    st.rerun()

file_to_process = uploaded_file

if not file_to_process and "sample_pdf_bytes" in st.session_state and st.session_state.sample_pdf_bytes:
    file_to_process = st.session_state.sample_pdf_bytes

if generate_clicked:
    if not file_to_process:
        st.error("Please upload a PDF first or click Use Sample PDF.")
    else:
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key:
            st.error("Server configuration error: API key is missing.")
        else:
            with st.spinner("Extracting text and generating code..."):
                try:
                    if isinstance(file_to_process, bytes):
                        from io import BytesIO
                        paper_text = extract_text_from_pdf(BytesIO(file_to_process))
                    else:
                        paper_text = extract_text_from_pdf(file_to_process)

                    if not paper_text.strip():
                        st.error(
                            "Could not extract any text from the PDF. It may be scanned or image-based."
                        )
                    else:
                        with st.status("Generating implementation with Gemini...", expanded=False):
                            code = generate_code_from_text(paper_text, api_key)

                        st.session_state.current_code = code
                        add_to_history(code)
                        st.success("Code generated successfully!")

                except Exception as e:
                    st.error(f"Error occurred: {e}")

if st.session_state.current_code:
    st.markdown("### Generated Python Code")
    st.code(st.session_state.current_code, language="python")

    st.download_button(
        label="Download Code as .py",
        data=st.session_state.current_code,
        file_name="generated_implementation.py",
        mime="text/x-python",
        use_container_width=True,
    )