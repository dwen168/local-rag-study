import streamlit as st
from initialiseapp import get_chroma_instance, get_mongodb_instance
from query_rag import query_rag
from langchain_community.llms import Ollama
from models import get_list_of_models


def ui_chat_history():
    st.title("Chatbot: Load and Display Chat History")

    if "list_of_models" not in st.session_state:
        st.session_state["list_of_models"] = get_list_of_models()
    
    selected_model = st.sidebar.selectbox(
        "Select a LLM model:", st.session_state["list_of_models"]
    )

    if st.session_state.get("selected_model") != selected_model:
        st.session_state["selected_model"] = selected_model
        st.session_state["llm"] = Ollama(model=selected_model)
    
    
    # Initialize session history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "current_session" not in st.session_state:
        st.session_state["current_session"] = []

    mongodb = get_mongodb_instance()
    if mongodb != None:
        try:
            collection = mongodb["chat_history"]
            chat_history = list(collection.find().sort("timestamp", -1))  # Sort by timestamp, newest first
            if chat_history:
                st.subheader("Chat History")
                for idx, chat_entry in enumerate(chat_history):
                    timestamp = chat_entry.get("timestamp", "Unknown Time").strftime("%Y-%m-%d %H:%M:%S")
                    first_user_message = next((msg["content"] for msg in chat_entry["chat_history"] if msg["role"] == "user"), "No user messages")
                    button_label = f"{timestamp} - {first_user_message[:50]}..."
                    if st.button(button_label, key=f"session_{idx}"):
                        # Store selected session in session state
                        st.session_state["current_session"] = chat_entry["chat_history"]
                        st.session_state["timestamp"] = timestamp
            else:
                st.info("No chat history found in the database.")
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
    else:
        st.error(f"Error loading chat history")

    # Chatbot functionality (if a session is selected)
    if st.session_state["current_session"]:
    # Display the selected session
        st.subheader(f"Continuing Chat - {st.session_state['timestamp']}")
        for message in st.session_state["current_session"]:
            if message["role"] == "user":
                st.text(f"you: {message['content']}")
            else:
                st.text(f"assistant: {message['content']}")
        
        #st.session_state.selected_chat = st.session_state["current_session"]
        if st.button("Re-open this talk?", icon="✈️"):
            st.session_state["messages"] = st.session_state["current_session"]
            st.session_state["historyheader"] = f"Continuing Chat - {st.session_state['timestamp']}"
            st.page_link("workingspace/chat_space.py", label="Click Me to re-open this talk", icon="😃")

ui_chat_history()