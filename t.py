import streamlit as st
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import chromadb
import numpy as np
import torch

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2")
model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")

# Sample documents for RAG
documents = [
    "The sky is blue and beautiful.",
    "Python is a programming language.",
    "Streamlit is a framework for building web apps.",
    "Machine learning is a subset of artificial intelligence."
]

# Create embeddings for documents
def create_embeddings(docs):
    inputs = tokenizer(docs, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.start_logits.softmax(dim=-1).numpy()

# Store documents in ChromaDB
def store_documents(docs):
    embeddings = create_embeddings(docs)
    for doc, embedding in zip(docs, embeddings):
        chroma_client.add(documents=[doc], embeddings=[embedding.tolist()])

store_documents(documents)

# Define the confidence threshold for fallback
CONFIDENCE_THRESHOLD = 0.7  # You can adjust this value

# Define a function for retrieval and response generation with fallback
def get_response(query):
    query_embedding = create_embeddings([query])
    results = chroma_client.query(query_embedding.tolist(), n_results=1)  # Retrieve the top document
    retrieved_doc = results[0][0]  # Get the top result document
    
    # Generate an answer based on the retrieved document
    inputs = tokenizer(retrieved_doc, return_tensors="pt")
    outputs = model(**inputs)
    
    start_logits = outputs.start_logits.softmax(dim=-1).numpy()[0]
    answer_start = np.argmax(start_logits)
    answer_confidence = start_logits[answer_start]

    # Generate answer based on start position
    answer_tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_start + 5])
    answer_text = tokenizer.decode(inputs["input_ids"][0][answer_start:answer_start + 5], skip_special_tokens=True)

    # Implement corrective fallback
    if answer_confidence < CONFIDENCE_THRESHOLD:
        fallback_responses = [
            "I'm not sure about that. Can you ask something else?",
            "I need to gather more information. Please rephrase your question.",
            "Let's try a different question."
        ]
        answer_text = np.random.choice(fallback_responses)

    return retrieved_doc, answer_text

# Streamlit app
st.title("RAG Chatbot with Corrective Fallback and ChromaDB")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for user_message, bot_response in st.session_state.chat_history:
    st.write(f"**You:** {user_message}")
    st.write(f"**Bot:** {bot_response}")

# Input for user message
user_input = st.text_input("Ask me anything:")
if user_input:
    retrieved_doc, answer = get_response(user_input)
    st.session_state.chat_history.append((user_input, answer))  # Update chat history
    st.write(f"**Retrieved Document:** {retrieved_doc}")
    st.write(f"**Bot:** {answer}")

