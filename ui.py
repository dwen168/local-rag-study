import streamlit as st
import os

from langchain_community.llms import Ollama
from langchain_core.documents import Document
from document_loader import load_documents_into_database

from models import get_list_of_models

from llm import getStreamingChain

from query_rag import query_rag


EMBEDDING_MODEL = "nomic-embed-text"
UPLOAD_DIR = "uploaded_files"


st.title("Local LLM with RAG 📚")

if "list_of_models" not in st.session_state:
    st.session_state["list_of_models"] = get_list_of_models()

selected_model = st.sidebar.selectbox(
    "Select a model:", st.session_state["list_of_models"]
)

if st.session_state.get("ollama_model") != selected_model:
    st.session_state["ollama_model"] = selected_model
    st.session_state["llm"] = Ollama(model=selected_model)


# Ensure the directory exists, create it if it doesn't
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# File uploader to allow multiple files
uploaded_files = st.file_uploader("Choose files", type=None, accept_multiple_files=True)

# Check if files were uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Display basic file information
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
        st.write(f"**File type:** {uploaded_file.type}")

        # Create the full file path
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        # Save the uploaded file to the specified directory
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"Saved file: {uploaded_file.name} to {UPLOAD_DIR}")


if UPLOAD_DIR:
    if not os.path.isdir(UPLOAD_DIR):
        st.error(
            "The provided path is not a valid directory. Please enter a valid folder path."
        )
    else:
        if st.sidebar.button("Index Documents"):
            if "db" not in st.session_state:
                with st.spinner(
                    "Creating embeddings and loading documents into Chroma..."
                ):
                    st.session_state["db"] = load_documents_into_database(EMBEDDING_MODEL, UPLOAD_DIR)
                st.info("All set to answer questions!")
            st.info("Connecting to Chroma....")
            st.session_state["db"] = load_documents_into_database(EMBEDDING_MODEL, UPLOAD_DIR)
            st.info("All set to answer questions!")
else:
    st.warning("Please enter a folder path to load documents into the database.")


# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    st.write(f"**{message['role']}:** {message['content']}")


user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    # Append user message to the session state
    st.session_state.messages.append({"role": "User", "content": user_input})

    # Query the RAG model
    #response = qa_chain.run(user_input)
    response = query_rag(  user_input, 
                                    st.session_state["db"], 
                                    st.session_state["ollama_model"])
    print("back to UI................................................................")
    print(response)

    # Append AI response to the session state
    st.session_state.messages.append({"role": "AI", "content": response})
    st.write(f"**AI:** {response}")

    # Clear the input field
    user_input = ""

# Optionally, you can add an info message if no input is given
if not user_input:
    st.info("Please enter your message above and click 'Send'.")
    

