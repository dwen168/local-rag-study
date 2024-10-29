from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import shutil

#TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
CHROMA_PATH = "chroma"
WORKING_PATH = "uploaded_files"
ARCHIVE_PATH = "archive"


def load_documents_into_database(model_name: str, documents_path: str) -> Chroma:
    """
    Loads documents from the specified directory into the Chroma database
    after splitting the text into chunks.

    Returns:
        Chroma: The Chroma database with loaded documents.
    """

    print("Creating embeddings and loading documents into Chroma")
    #clear_database()
    db = Chroma(
            persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
        )

    print("Loading documents")
    #read raw doc file path
    raw_documents = load_documents(documents_path)

    #split into chunks by text_splitter
    chunks = split_documents(raw_documents)

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        #db.persist()
    else:
        print("✅ No new documents to add")

    archive_files(WORKING_PATH, ARCHIVE_PATH)

    return db


def load_documents(path: str) -> List[Document]:
    """
    Loads documents from the specified directory path.

    This function supports loading of PDF, Markdown, and HTML documents by utilizing
    different loaders for each file type. It checks if the provided path exists and
    raises a FileNotFoundError if it does not. It then iterates over the supported
    file types and uses the corresponding loader to load the documents into a list.

    Args:
        path (str): The path to the directory containing documents to load.

    Returns:
        List[Document]: A list of loaded documents.

    Raises:
        FileNotFoundError: If the specified path does not exist.

    Return: Document Objs
            page_content = 'ABCD'
            metadata={'source': 'Research\\2305.14325.pdf', 'page': 0}

    Note: this is before split into chunks        
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    loaders = {
        ".pdf": DirectoryLoader(
            path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True,
        ),
        ".md": DirectoryLoader(
            path,
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
        ),
        ".txt": DirectoryLoader(
            path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True,
        ),
    }

    docs = []
    for file_type, loader in loaders.items():
        print(f"Loading {file_type} files")
        docs.extend(loader.load())
    return docs


def get_embedding_function():
    #embeddings = BedrockEmbeddings(
        #credentials_profile_name="default", region_name="us-east-1"
    #)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/doc_name.pdf:7:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def archive_files(source_dir, dest_dir):
    """
    Moves all files from the source directory to the destination directory.

    Parameters:
    - source_dir (str): Path to the source directory.
    - dest_dir (str): Path to the destination directory.

    Returns:
    - None
    """
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return

    # Ensure the destination directory exists; if not, create it
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Destination directory '{dest_dir}' created.")

    # Move all files from source_dir to dest_dir
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)
        
        # Check if it's a file (skip directories)
        if os.path.isfile(source_path):
            shutil.move(source_path, dest_path)
            print(f"Archived: {filename}")
        else:
            print(f"Skipped directory: {filename}")

    print("File archive completed.")

