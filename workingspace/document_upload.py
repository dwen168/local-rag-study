from document_loader import load_documents_into_database
import streamlit as st
import os

EMBEDDING_MODEL = "nomic-embed-text"
UPLOAD_DIR = "uploaded_files"

def ui_upload_file():
    st.title("Upload your own documents for building your knowledge database")

    # Ensure the directory exists, create it if it doesn't
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    if not os.path.isdir(UPLOAD_DIR):
        st.error(
            "The provided path is not a valid directory. Please enter a valid folder path."
        )

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

    if st.button("Save and Index Documents", icon="💾"):
        with st.spinner("building your knowledge database...."):
            st.session_state["db"] = load_documents_into_database(EMBEDDING_MODEL, UPLOAD_DIR)
        st.info("All set to answer questions!")


ui_upload_file()