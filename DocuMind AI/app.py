# app.py
import streamlit as st
import os
# Import our custom modules designed above
from ingestion import ingest_pdf
from chat_chain import get_rag_chain

# Configure basic web browser tab parameters
st.set_page_config(page_title="DocuMind AI", layout="wide")
st.title("🧠 DocuMind AI - Advanced Multimodal RAG")

# 'with st.sidebar:' renders a persistent left-hand configurations column on the web app interface
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Render a radio toggle selection interface to let the user select their core engine backend
    mode = st.radio("LLM & Embedding Provider", ["OpenAI (Cloud)", "Ollama (Local)"])
    # Boolean flag: sets to True if user picks Ollama, False otherwise
    use_local = mode == "Ollama (Local)"
    
    # Render operational slider UI elements to give the user dynamic runtime control over parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1) # Default 0.3 favors structured factuality
    top_k = st.slider("Top-K Retrieved Chunks", 1, 10, 4)       # Default 4 pulls the top 4 text matches
    
    st.write("---") # Visual separator line in the UI
    st.header("📂 Document Upload")
    # Render an interactive drag-and-drop file upload zone restricting files to PDFs
    uploaded_file = st.file_uploader("Upload a complex PDF (with tables/charts)", type=["pdf"])
    
    # If a user actually drops a file into the upload element
    if uploaded_file:
        # Establish a local directory path to store files coming through the web server
        temp_dir = "temp_docs"
        os.makedirs(temp_dir, exist_ok=True) # Build directory if it doesn't exist yet
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Write the file binary stream out of browser memory and down onto local disk storage
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # If the user presses the action button below the file upload slot
        if st.button("🚀 Process & Index Document"):
            # st.spinner shows a loading animation wheel while the long background process runs
            with st.spinner("Parsing document & generating embeddings..."):
                # Call our ingestion pipeline function passing the local file path and provider flag
                msg = ingest_pdf(file_path, use_local=use_local)
                # Show a green success banner containing the confirmation string returned by ingestion.py
                st.success(msg)

# Streamlit refreshes scripts from top-to-bottom on every interaction. 
# We use 'st.session_state' to ensure our chat log history isn't erased during UI updates.
if "messages" not in st.session_state:
    st.session_state.messages = [] # Initialize an empty array if this is a fresh user session

# Loop through and redraw previous messages from the session array to retain conversational UI flow
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 'if user_query :=' opens an active chat input line and assigns the user's typed string to 'user_query' upon enter
if user_query := st.chat_input("Ask something about your documents..."):
    # Append user's typed message to state array so it stays visible on next page rerender
    st.session_state.messages.append({"role": "user", "content": user_query})
    # Render user query right away into the interface inside a user chat bubble
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Open assistant response chat window box
    with st.chat_message("assistant"):
        with st.spinner("Searching context & thinking..."):
            try:
                # Instantiate our execution chain object dynamically based on the current sidebar state selections
                chain = get_rag_chain(use_local=use_local, temperature=temperature, top_k=top_k)
                
                # Run the query through our LangChain pipeline. 
                # This fetches data vectors, builds prompts, talks to the LLM, and returns a dictionary.
                response = chain.invoke({"input": user_query})
                answer = response["answer"] # Extract the text string answer out of response dictionary
                
                # Source tracking extraction block
                sources = response.get("context", []) # Safely extract the list of chunks used by the chain
                # Construct a clean markdown summary listing exactly where the answers were derived from
                source_text = "\n\n**Sources:**\n" + "\n".join([f"- Page {doc.metadata.get('page', 'Unknown')}: {doc.page_content[:100]}..." for doc in sources])
                
                # Combine the textual answer with the source list metadata
                full_response = answer + source_text
                # Output the finished combined text to the user layout
                st.markdown(full_response)
                
                # Save assistant's reply into session history array to persist across screen updates
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                # Fallback element: captures operational bugs safely without crashing the underlying web engine
                st.error(f"Error generating response: {e}")