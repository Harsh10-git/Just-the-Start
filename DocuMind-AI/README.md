# 🧠 DocuMind AI — Advanced Document RAG Platform

DocuMind AI is a production-grade, context-grounded Retrieval-Augmented Generation (RAG) platform engineered to eliminate LLM hallucinations when interacting with complex local PDF files. By converting document sections into mathematical vector representations, the system ensures that responses are strictly derived from the uploaded text material.

---

## 🛠️ System Architecture & Data Flow

The application isolates processes into a distinct view layer (Streamlit Frontend) and calculation engine (Python/ChromaDB Backend).

[ Your Local PDF ] ──> [ Split into Chunks ] ──> [ Gemini embedding-2 ] ──> [ ChromaDB ]
│
▼
[ User Query ] ───────────────────────────────────────────> [ Semantic Search / Retrieval ]
│
▼
[ Gemini 2.5 Flash ] <── [ Prompt: Context + Query ] <─────────────────────────────┘
│
▼
[ Contextual Response ]

1. **Document Processing:** The script reads a dense PDF file using `pypdf` and breaks it down into small, readable 1000-character windows with a 200-character overlapping slider to preserve contextual sentence structure across boundaries.
2. **Vector Conversion:** Text blocks are pushed to Google's `text-embedding-004` model, converting semantic meaning into highly optimized mathematical vector matrices.
3. **Database Indexing:** Vectors are saved locally to a persistent **ChromaDB** instance on the Pop!_OS file system.
4. **Context Injection & Inference:** When a user queries the system, ChromaDB performs a similarity search to isolate the Top 3 closest context blocks. These text snippets are safely bound inside a strict system prompt and handled by `gemini-2.5-flash` for zero-hallucination execution.

---

## 🚀 Key Features

* **Secure Secrets Management:** Leverages `python-dotenv` to isolate application parameters and keep private Google API keys completely out of public Git repository branches.
* **Semantic Chunking:** Implements token-safe chunk size windows with overlapping boundary controls to preserve data integrity.
* **Low-Latency Vector Storage:** Uses ChromaDB for lightweight, configuration-free, high-speed mathematical nearest-neighbor vector updates.
* **Enterprise Interface:** Built with a stateful chat dialogue box and dynamic file-upload control board powered entirely by Streamlit.

---

## 💻 Tech Stack

* **Language:** Python 3
* **AI Models:** Google Gemini API (`gemini-2.5-flash` & `text-embedding-004`)
* **Vector Engine:** ChromaDB
* **UI Framework:** Streamlit
* **Environment Handler:** `python-dotenv`

---

## 📦 Project File Structure

```text
DocuMind-AI/
├── .env                  # Private API key file (Excluded from Git tracking)
├── .gitignore            # Specially configured security rule script
├── README.md             # Project documentation engine
├── requirements.txt      # Project library dependency records
└── src/
    ├── app.py            # Streamlit Interactive Web Interface Layout
    └── backend.py        # Core RAG Pipeline Ingestion Execution Engine