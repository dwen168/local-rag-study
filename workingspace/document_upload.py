from document_loader import load_documents_into_database
import streamlit as st
import os
from chromadb import Client
from chromadb.config import Settings
from initialiseapp import get_chroma_instance
import chromadb
import re

EMBEDDING_MODEL = "nomic-embed-text"
UPLOAD_DIR = "uploaded_files"
CHROMA_PATH = "chroma"

def ui_upload_file():
    
    st.sidebar.title("Manage knowledge base:")
    
    st.markdown(f"<h3 style='font-size:36px;'>Take control of your knowledge vault—upload new docs to expand your empire or delete old ones to make room for fresh wisdom!</h3>", unsafe_allow_html=True)
    app_mode = st.sidebar.radio("Choose an option", ["Upload Document", "Delete Document"])
    user_id = st.session_state.user_state['user_id']

    if app_mode == "Upload Document":
        st.markdown(f"<h3 style='font-size:20px;'> Upload your documents </h3>", unsafe_allow_html=True)
        # Ensure the directory exists, create it if it doesn't
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        if not os.path.isdir(UPLOAD_DIR):
            st.error(
                "The provided path is not a valid directory. Please enter a valid folder path."
            )
        
        # Set file size limit in MB
        MAX_FILE_SIZE_MB = 10
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

        # File uploader to allow multiple files
        uploaded_files = st.file_uploader("Choose files", type=None, accept_multiple_files=True)

        # Check if files were uploaded
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Display basic file information
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
                st.write(f"**File type:** {uploaded_file.type}")

                # Check file size
                if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                    st.error(f"File `{uploaded_file.name}` exceeds the size limit of {MAX_FILE_SIZE_MB} MB.")
                    continue
                
                # Create the full file path
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

                # Save the uploaded file to the specified directory
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.success(f"Saved file: {uploaded_file.name} to {UPLOAD_DIR}")

        if st.button("Save and Index Documents", icon="💾"):
            with st.spinner("building your knowledge database...."):
                db = load_documents_into_database(UPLOAD_DIR, user_id)
                if db:
                    st.info("All set to answer questions!")
                else:
                    st.error("An error occurred while initializing RAG")

    elif app_mode == "Delete Document":
        st.markdown(f"<h3 style='font-size:20px;'> Uploaded documents </h3>", unsafe_allow_html=True)
        doc_records = fetch_chromadb_records(user_id)
        if doc_records:
            st.write("Your knowledge database is built on these documents—feel free to toss any of them if they're throwing a wrench in your analysis! No hard feelings, just clearer insights ahead.")
            for doc in doc_records:
                with st.expander(doc):
                    if st.button(f"Delete {doc}", key=doc):
                        delete_record_by_user_and_file(user_id, doc)
        else:
            st.warning(f"No documents found for {user_id}.")



def fetch_chromadb_records(user_id):
    try:
        db = get_chroma_instance()
        existing_items = db.get(include=[],
                                where={"user_id": user_id}
                                ) 
        existing_ids = set(existing_items["ids"])
        doc_names = []
        for id in existing_ids:
            if id.startswith(f"{user_id}:uploaded_files/"):
                # Extract the file name using regex
                match = re.search(r"uploaded_files/(.*?):", id)
                if match:
                    doc_names.append(match.group(1))  # Extracted file name
        unique_doc_names = list(dict.fromkeys(doc_names))
        return unique_doc_names
    except Exception as e:
        st.error(f"Error fetching records: {e}")
        return None

def delete_record_by_user_and_file(user_id, doc_name):
    try:
        db = get_chroma_instance()
        existing_items = db.get(include=[],
                                where={"user_id": user_id}
                                ) 
        existing_ids = set(existing_items["ids"])
        # Filter IDs that match the user_id and file_name
        ids_to_delete = [
            id for id in existing_ids
            if id.startswith(f"{user_id}:uploaded_files/{doc_name}")
        ]
        db.delete(ids_to_delete)
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting record for file '{doc_name}': {e}")


ui_upload_file()