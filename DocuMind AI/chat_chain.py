# chat_chain.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
# create_retrieval_chain handles the workflow loop: take query -> search DB -> pass context to LLM
from langchain.chains import create_retrieval_chain
# create_stuff_documents_chain takes a list of retrieved documents and "stuffs" them into the LLM prompt template
from langchain.chains.combine_documents import create_stuff_documents_chain
# ChatPromptTemplate formats structural system vs. human interactions neatly for modern LLMs
from langchain_core.prompts import ChatPromptTemplate

CHROMA_PATH = "chroma_db"

def get_rag_chain(use_local: bool = False, temperature: float = 0.7, top_k: int = 4):
    """
    Initializes the required embedding model, instantiates the vector store connection,
    configures the retriever, sets up the LLM, and binds them into a unified RAG execution chain.
    """
    
    # 1. Setup the respective Embedding and Chat Model based on the user's toggle switch
    if use_local:
        # Must match the exact embedding model used during data ingestion
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # Initialize local Llama 3 via Ollama. Temperature controls creativity (0.0 = deterministic, 1.0 = creative)
        llm = ChatOllama(model="llama3", temperature=temperature)
    else:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        # Initialize OpenAI's fast, cost-efficient model for general tasks
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        
    # Open an internal connection to our existing Chroma database directory using our embedding engine
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    # Convert our vector database vector space into a LangChain 'Retriever' interface.
    # search_kwargs={"k": top_k} instructs the database to return only the 'X' closest matching text blocks.
    retriever = db.as_retriever(search_kwargs={"k": top_k})
    
    # Create a system instruction prompt. 
    # This sets the boundaries for the AI, forcing it to use the injected context and preventing hallucination.
    system_prompt = (
        "You are DocuMind AI, an advanced document assistant.\n"
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know.\n\n"
        "Context:\n{context}"
    )
    
    # Compile the prompt array. The LLM processes this sequentially.
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt), # Internal instructions
        ("human", "{input}"),       # The actual user question
    ])
    
    # Build the document-stuffing sub-chain. This handles embedding the database results directly into the '{context}' field above.
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # Combine the retriever tool and our document-stuffing prompt chain into one comprehensive execution flow.
    # Execution process: input -> retriever (gets context) -> question_answer_chain (formats & sends to LLM) -> output
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    # Return the executable chain back to the web application
    return rag_chain