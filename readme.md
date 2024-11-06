
#This is the extention of https://github.com/amscotti/local-LLM-with-RAG/tree/main


# Local LLM with RAG


This project is an experimental sandbox for testing out ideas related to running local Large Language Models (LLMs) with [Ollama](https://ollama.ai/) to perform Retrieval-Augmented Generation (RAG) for answering questions based on sample PDFs and Texts. In this project, we are also using Ollama to create embeddings with the [nomic-embed-text](https://ollama.com/library/nomic-embed-text) to use with [Chroma](https://docs.trychroma.com/). 

There is also a web UI created using [Streamlit](https://streamlit.io/) to provide a different way to interact with Ollama.

## Requirements

- [Ollama](https://ollama.ai/) verson 0.1.26 or higher.

## Setup

1. Clone this repository to your local machine.
2. Create a Python virtual environment by running `python3 -m venv .venv`.
3. Activate the virtual environment by running `source .venv/bin/activate` on Unix or MacOS, or `.\.venv\Scripts\activate` on Windows.
4. Install the required Python packages by running `pip install -r requirements.txt`.

## Running the Project

**Note:** The first time you run the project, it will download the necessary models from Ollama for the LLM and embeddings. This is a one-time setup process and may take some time depending on your internet connection.

1. Ensure your virtual environment is activated.


## Running the Streamlit UI

1. Ensure your virtual environment is activated.
2. Navigate to the directory containing the `ui.py` script.
3. Run the Streamlit application by executing `streamlit run ui.py` in your terminal.

This will start a local web server and open a new tab in your default web browser where you can interact with the application. The Streamlit UI allows you to select models, select a folder, providing an easier and more intuitive way to interact with the RAG chatbot system compared to the command-line interface. The application will handle the loading of documents, generating embeddings, querying the collection, and displaying the results interactively.

## Technologies Used

- [Langchain](https://github.com/langchain/langchain): A Python library for working with Large Language Model
- [Ollama](https://ollama.ai/): A platform for running Large Language models locally.
- [Chroma](https://docs.trychroma.com/): A vector database for storing and retrieving embeddings.
- [PyPDF](https://pypi.org/project/PyPDF2/): A Python library for reading and manipulating PDF files.
- [Streamlit](https://streamlit.io/): A web framework for creating interactive applications for machine learning and data science projects.


## Project Files
1. ui.py: This is the main Streamlit app. Launch the app by running streamlit run ui.py in the terminal.

    Model Selection: Choose an existing model from a dropdown box. This automatically loads a model from Ollama, as well as the GPT-4-turbo-mini (gpt-4o-mini) model from OpenAI (requires your API key).
    Document Upload: Upload PDF or TXT documents through the UI. These documents are then embedded into your local Chroma database.
    Load and Index: Click "Load and Index Document" to save the document into your local Chroma DB.

2. models.py: Detects the available local models through Ollama.

3. document_loader.py: Handles document uploads, splitting, embedding, and loading into the Chroma database. It archives files in the archive folder and automatically detects and skips duplicate uploads.

4. query_rag.py: Provides a querying interface for the Chroma DB. If a relevant answer is found in the knowledge base, it generates a response based on local data. If not, it queries models from Ollama or ChatGPT.

5. query_router.py, query_ollama.py, and query_gpt.py: These files support the querying functionality described in point 4.