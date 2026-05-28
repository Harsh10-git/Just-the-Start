# ingestion.py
import os
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

CHROMA_PATH = "chroma_db"

def ingest_pdf(file_path: str, use_local: bool = False):
    """Parses PDF, chunks text, and stores it in ChromaDB."""
    # 1. Advanced Parsing (Unstructured handles tables/layouts well)
    loader = UnstructuredPDFLoader(
        file_path=file_path, 
        strategy="hi_res", # "hi_res" is great for tables/complex layouts
        infer_table_structure=True
    )
    docs = loader.load()
    
    # 2. Smart Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    
    # 3. Choose Embeddings
    if use_local:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
    else:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
    # 4. Vector Storage
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    return f"Successfully ingested {len(chunks)} chunks into the vector store."