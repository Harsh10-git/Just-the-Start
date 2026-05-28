# 🧠 DocuMind AI – Advanced Multimodal RAG Chatbot

DocuMind AI is an advanced, layout-aware Retrieval-Augmented Generation (RAG) application. Unlike basic text-only RAG pipelines, DocuMind AI utilizes high-resolution structural parsing to extract text, tables, and complex formatting from local PDFs. It then chunks, indexes, and stores this data into a local vector database, allowing users to interact with their documents using either cloud-based or local Large Language Models (LLMs).

---

## 🛠️ The Tech Stack
* **Orchestration:** LangChain
* **Frontend UI:** Streamlit
* **Vector Database:** ChromaDB
* **Data Parsing Engine:** Unstructured (High-Res Layout Aware)
* **LLM Backends:** OpenAI API (`gpt-4o-mini`) & Ollama (`llama3` / `nomic-embed-text` for 100% free local compute)

---

## 📁 Repository Structure
```text
DocuMind AI/
├── app.py              # Streamlit Web User Interface & State Management
├── ingestion.py        # PDF Layout Parsing, Chunking & ChromaDB Vector Ingestion
├── chat_chain.py       # LangChain Retrieval & Context-Aware LLM Generation Loop
├── requirements.txt    # Frozen Project Dependency Versions
└── README.md           # Project Documentation