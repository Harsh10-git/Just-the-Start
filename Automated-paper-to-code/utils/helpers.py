import streamlit as st

def init_session_state():
    """Initializes Streamlit session state variables for history tracking."""
    if "history" not in st.session_state:
        st.session_state.history = []

def add_to_history(code: str):
    """Adds generated code to the session history, keeping the last 5 results."""
    if "history" not in st.session_state:
        st.session_state.history = []
    
    st.session_state.history.append(code)
    
    # Keep only the last 5 items to avoid blowing up memory
    if len(st.session_state.history) > 5:
        st.session_state.history.pop(0)
