# Detailed Guide: Automated Paper-to-Code Implementation Agent

This guide provides deep technical documentation for understanding, configuring, and operating the "Paper-to-Code Implementation Agent." It is intended for Linux users (specifically tailored to Pop!_OS) as a comprehensive resource.

## 1. System Architecture and Data Flow

The project consists of a purely Pythonic frontend hosted with **Streamlit** and a small backend package that utilizes **pdfplumber** and **Google GenAI**.

### Data Flow Lifecycle

1. **File Ingestion:** The user selects a document via Streamlit’s `st.file_uploader`. The PDF artifact is briefly held in server memory.
2. **Text Extraction:** In `backend/processor.py` → `extract_text_from_pdf()`, `pdfplumber` iterates over the document. It parses bounding boxes and layout configurations to seamlessly decode structured PDF text into a massive Python string.
3. **Prompt Injection:** The resulting text is inserted into a heavily engineered system prompt explicitly instructed to behave as an expert data scientist, strictly returning functional Python code and nothing else.
4. **LLM Invocation:** The text and prompt payload are transmitted to `gemini-2.5-flash` utilizing the `google-genai` SDK.
5. **Code Parsing:** The raw response is audited for "markdown pollution" (removing ```python bounds if the model decides to wrap the output).
6. **Delivery & Session Persistence:** The returned string code is forwarded to `st.code()` for highlighted rendering, appended into `st.session_state.history` for session persistence (found in the sidebar).

---

## 2. Environment Setup (Pop!_OS / Ubuntu-based Linux)

### Installing Core Python Developer Tools
Pop!_OS generally comes with Python 3 out of the box, but you must ensure that virtual environment dependencies natively supplied by Debian exist.

```bash
sudo apt update
sudo apt install software-properties-common python3-pip python3-venv build-essential
```

### Initializing the Project
From within your project folder:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### What are these dependencies?
- `streamlit`: The overarching frontend dashboard framework that serves Python logic interactively.
- `pdfplumber`: A robust document analysis library mapping the visual layer of PDFs exactly corresponding to characters.
- `google-genai`: The modern, official SDK utilized to interface directly with Google Gemini Models.
- `python-dotenv`: A utility responsible for loading environment variables structurally from `.env` files.

---

## 3. How to Connect to the LLM API

The agent delegates its cognitive capabilities directly to Google's Gemini models.

1. Navigate to: [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate an API Key (it is entirely free for moderate utilization).
3. Connect the key to the application in one of two ways:
    - **Local File Method:** Rename `.env.example` to `.env` and assign `GEMINI_API_KEY="your_api_key_here"`.
    - **App UI Method:** Enter your API key manually into the Streamlit Sidebar "Configuration" input box anytime you run the application.

### (Optional) Utilizing a Local LLM 

If you prefer to operate entirely locally utilizing `Ollama`:
1. Ensure Ollama is installed on your Pop!_OS desktop (`curl -fsSL https://ollama.com/install.sh | sh`).
2. Pull a local coding model: `ollama run llama3.1` or `ollama run qwen2.5-coder`.
3. Within `backend/processor.py`, you would replace the Google GenAI API calling loop with the OpenAI Compatible Ollama format:
   ```python
   # Requires `pip install openai`
   from openai import OpenAI
   client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
   response = client.chat.completions.create(model="llama3.1", messages=[...])
   ```

---

## 4. Deploying to Streamlit Community Cloud

Hosting your tool to the wider web is simplified utilizing Streamlit Community Cloud.

**Step 1: Version Control**
The deployment requires your project to be hosted in a GitHub repository. Initialize and push your folder to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YourUsername/YourRepository.git
git push -u origin main
```
*(Ensure `.env` matches rules located in `.gitignore` and is NEVER pushed!)*

**Step 2: Streamlit Setup**
1. Visit [Streamlit Cloud](https://share.streamlit.io).
2. Authorize via your GitHub account.
3. Click **New App** -> Use Existing Repository.
4. Fill out the application settings:
    - **Repository:** `YourUsername/YourRepository`
    - **Branch:** `main`
    - **Main file path:** `app.py`
5. Click **Advanced Settings**.
6. In the **Secrets** section, configure your environment variables safely:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
7. Hit **Deploy**. The containerization and package resolution is automatically tracked by Streamlit utilizing your `requirements.txt` implicitly.

---

## 5. Troubleshooting Local Issues

**Issue**: `ModuleNotFoundError: No module named 'streamlit'`
**Solution**: Your virtual environment is likely unactivated. Run `source venv/bin/activate` and ensure you ran `pip install -r requirements.txt`.

**Issue**: Output generates generic or incorrect Python code.
**Solution**: Gemini fundamentally tracks the quality of the prompt context. If the `pdfplumber` fails to extract image-based scans (PDFs lacking proper OCR), you must manually run the PDFs through an OCR tool beforehand or use Gemini’s multimodal vision capabilities instead. 

**Issue**: Port 8501 is already in use natively.
**Solution**: Streamlit allows you to define an alternative operating port locally via: `streamlit run app.py --server.port 8503`
