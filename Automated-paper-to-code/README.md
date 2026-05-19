# Automated Paper-to-Code Implementation Agent

An automated pipeline that converts structured research papers (PDF) into working, runnable Python code using generative AI. Designed as a lightweight, purely Python-based Streamlit application.

## Features
- **PDF Upload:** Accepts research papers in PDF format.
- **Smart Text Extraction:** Extracts textual methodology and equations directly from the document.
- **Automated Generation:** Queries Google Gemini 2.5 Flash to write python implementations based on the extracted methodology.
- **Syntax Highlighting & Easy Copy:** Displays the code with appropriate syntax and a 1-click 'copy to clipboard' button.
- **Direct Download:** Allows downloading the generated output as a `.py` file.
- **Session History:** Keeps track of the last 5 generated code snippets.

## Architecture
```text
[User] 
  └─(uploads PDF)─> [Streamlit UI]
                         │
                         ├─> [PDF Plumber] --(extracts text)--> Memory
                         │                                         │
                         └─(triggers generation)─────────────────> ├─(text + prompt)
                                                                   │
    [Generated Code] <──(displays in UI)── [Streamlit app] <───── [Google GenAI]
```

## System Prerequisites
Tested on **Pop!_OS (Linux)**:
- Python 3.10 or newer (`python3`)
- `python3-venv` package (for creating virtual environments)
- Pip

Ensure `python3-venv` is installed:
```bash
sudo apt update
sudo apt install python3-venv
```

## Local Installation Guide 

**1. Clone or Download this Directory**
Navigate to wherever you saved or cloned this project in your terminal:
```bash
cd /path/to/paper-to-code-agent
```

**2. Create a Python Virtual Environment**
Creating a virtual environment ensures dependencies stay restricted to this project.
```bash
python3 -m venv venv
```

**3. Activate the Virtual Environment**
```bash
source venv/bin/activate
```
*(Your prompt should now be prefixed with `(venv)`)*

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure Environment Variables**
Copy the example environment configuration to an active `.env` file mapping:
```bash
cp .env.example .env
```
Open `.env` in a text editor (e.g., `nano .env`) and add your [Google Gemini API Key](https://aistudio.google.com/app/apikey).

*(Alternatively, you can skip `.env` and just paste your API key directly into the Streamlit sidebar when the app is running!)*

## Running the App locally

While inside your activated virtual environment, run:
```bash
streamlit run app.py
```
This will start a local server, and your default web browser should open automatically to `http://localhost:8501`.

## Deployment to Streamlit Community Cloud (Free)

This application is purposefully designed to be easily deployed to [Streamlit Community Cloud](https://share.streamlit.io/) with no Docker required.

1. **Push to GitHub**: Commit the project files (ensure `.env` is NOT committed – standard `.gitignore` applies) and push to a public or private GitHub repository.
2. **Login to Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. **Deploy an App**: Click "New app".
4. **Select Repository**: Pick your repository, branch, and set the **Main file path** to `app.py`.
5. **Set Secrets (Env variables)**: Click "Advanced settings" before deploying, and under "Secrets", input:
   ```toml
   GEMINI_API_KEY="your_actual_api_key_here"
   ```
6. **Deploy!**

## Documentation
For a deep dive into how various components work, please refer to the `DETAILED_GUIDE.md` provided alongside this file.
