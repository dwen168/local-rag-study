import streamlit as st
import os
import streamlit.components.v1 as components

from langchain_community.llms import Ollama
from document_loader import load_documents_into_database
from models import get_list_of_models
from query_rag import query_rag
from markmapcomponent import create_markmap_html, get_binary_file_downloader_html, escape_markdown_for_js


EMBEDDING_MODEL = "nomic-embed-text"
UPLOAD_DIR = "uploaded_files"


st.title("Build your own RAG 📚")

if "list_of_models" not in st.session_state:
    st.session_state["list_of_models"] = get_list_of_models()

selected_model = st.sidebar.selectbox(
    "Select a LLM model:", st.session_state["list_of_models"]
)

if st.session_state.get("selected_model") != selected_model:
    st.session_state["selected_model"] = selected_model
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
        st.sidebar.text(f"The embedding model is : \n{EMBEDDING_MODEL}")
        if st.sidebar.button("Load and Index Documents"):
            if "db" not in st.session_state:
                with st.spinner(
                    "Creating embeddings and loading documents into Chroma..."
                ):
                    st.session_state["db"] = load_documents_into_database(EMBEDDING_MODEL, UPLOAD_DIR)
                st.info("All set to answer questions!")
            else:
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "db" not in st.session_state:
            st.write("please select a LLM model and index it first")
        else:
            response = query_rag(
                prompt,
                st.session_state["db"],
                st.session_state["selected_model"],
            )
            if "mind_map_mark" in response.lower():
                stream = response[response.find("mind_map_mark") + len("mind_map_mark"):].strip()
            else:
                stream = response
            st.session_state.messages.append({"role": "assistant", "content": stream})
            st.write(stream)
            if ("mind map" in response.lower() and "mind map" in prompt.lower()) or "mind_map_mark" in response.lower():
                start_index = stream.find("#")
                end_index = stream.find("Sources: [", start_index)
                if start_index > -1 and end_index > -1:
                    str_mindmap = stream[start_index : end_index].strip()
                elif start_index > -1 and end_index == -1:
                    str_mindmap = stream[start_index :]
                else:
                    str_mindmap = stream
                st.subheader("Generated Mind Map")
                html_content = create_markmap_html(str_mindmap)
                components.html(html_content, height=400)
                # Add button to open in new tab
                st.markdown(get_binary_file_downloader_html(html_content), unsafe_allow_html=True)