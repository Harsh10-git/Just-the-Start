import os
from pypdf import PdfReader
from google import genai
import chromadb
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize the official modern Google GenAI Client
# It automatically reads the GEMINI_API_KEY environment variable from your terminal
client = genai.Client()

# 2. Setup ChromaDB Local Storage
# This creates a folder named 'chroma_data' in your project to save your vectors permanently
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_data"))
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# Create a collection (think of it like a SQL table) for our document vectors
collection = chroma_client.get_or_create_collection(name="documind_collection")


def process_pdf_document(file_path: str, doc_id: str):
    """Opens a PDF, extracts text, breaks it into overlapping chunks, 

    converts chunks to vectors via Gemini, and stores them in ChromaDB.
    """
    # Read text from PDF
    reader = PdfReader(file_path)
    extracted_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"

    # Break text down into small 1000-character windows with 200-character overlap
    # Overlap ensures that sentences broken in half don't lose their meaning!
    chunk_size = 1000
    overlap = 200
    chunks = []
    start = 0
    while start < len(extracted_text):
        end = start + chunk_size
        chunks.append(extracted_text[start:end])
        start += chunk_size - overlap

    print(f"Total fragments created: {len(chunks)}. Converting to vectors...")

    # Convert chunks to numerical vectors and save to database
    for idx, chunk in enumerate(chunks):
        # Generate semantic vector weights using Google's text-embedding model
        response = client.models.embed_content(
            model="gemini-embedding-2", contents=chunk
        )
        vector_embedding = response.embeddings[0].values

        # Store text along with its mathematical vector mapping in ChromaDB
        collection.add(
            ids=[f"{doc_id}_chunk_{idx}"],
            embeddings=[vector_embedding],
            documents=[chunk],
        )

    return len(chunks)


def query_knowledge_base(user_query: str) -> str:
    """Takes a user question, searches ChromaDB for matching text chunks,

    and passes those specific chunks to Gemini to get a accurate answer.
    """
    # Convert the user's incoming question into a math vector
    query_vector_resp = client.models.embed_content(
        model="gemini-embedding-2", contents=user_query
    )
    query_vector = query_vector_resp.embeddings[0].values

    # Query ChromaDB to fetch the Top 3 text chunks matching the question's meaning
    search_results = collection.query(query_embeddings=[query_vector], n_results=3)

    # Clean and merge the retrieved text blocks
    retrieved_texts = search_results.get("documents", [[]])[0]
    context_payload = (
        "\n---\n".join(retrieved_texts) if retrieved_texts else "No context found."
    )

    # Write a strict System Instruction so the AI doesn't hallucinate or make things up
    system_instruction = (
        "You are DocuMind AI, an advanced document intelligence system. "
        "Answer the user query using ONLY the provided context blocks. "
        "If the answer cannot be confidently deduced from the facts given, state: "
        "'I am sorry, but the uploaded documentation does not contain sufficient details to answer this.'"
    )

    # Format our complete prompt structure
    prompt_payload = (
        f"Context Blocks:\n{context_payload}\n\nUser Question: {user_query}"
    )

    # Run the fast flagship model to output the clean response
    ai_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_payload,
        config={"system_instruction": system_instruction},
    )

    return ai_response.text


def clear_knowledge_base():
    """Wipes the database clear so you can upload a completely new document."""
    global collection
    try:
        chroma_client.delete_collection(name="documind_collection")
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(
        name="documind_collection"
    )