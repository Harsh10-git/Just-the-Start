import streamlit as st
import os
from backend import process_pdf_document, query_knowledge_base, clear_knowledge_base

# Configure the look and feel of the browser tab
st.set_page_config(page_title="DocuMind AI", page_icon="🧠", layout="wide")

st.title("🧠 DocuMind AI — Advanced Document RAG Platform")
st.caption("Empower local documents with instant contextual semantic lookup intelligence.")

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.header("🗂️ Document Control Panel")
    
    # Simple file upload widget
    uploaded_file = st.file_uploader("Upload Target PDF Document", type=["pdf"])
    
    if uploaded_file is not None:
        # Create a safe local folder to temporarily hold the file while parsing
        temp_dir = "temp_storage"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Write the uploaded bytes into the temporary file
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.get_buffer())
            
        # Button to trigger the backend RAG ingestion pipeline
        if st.button("⚡ Index Document Vectors", use_container_width=True):
            with st.spinner("Parsing text and running deep vector embeddings generation..."):
                # Call our backend function!
                total_chunks = process_pdf_document(temp_file_path, uploaded_file.name)
                st.success(f"Success! Fragmented file into {total_chunks} indexable blocks.")
                
        # Clean up the temporary file from the disk to keep things clean
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    st.markdown("---")
    
    # Clear session option
    if st.button("🗑️ Clear Vector Database Workspace", use_container_width=True):
        clear_knowledge_base()
        st.sidebar.warning("Local vector cache database dropped.")
        st.session_state.chat_history = []

# --- MAIN CHAT INTERFACE ---
# Initialize persistent chat memory inside the browser session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Redraw previous chat messages if the page refreshes
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Wait for new user text input
if user_input := st.chat_input("Ask anything relative to the processed technical documents..."):
    
    # 1. Display user query
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # 2. Compute response using our vector query logic
    with st.chat_message("assistant"):
        with st.spinner("Analyzing indexed knowledge segments..."):
            model_output = query_knowledge_base(user_input)
            st.markdown(model_output)
    st.session_state.chat_history.append({"role": "assistant", "content": model_output})