import streamlit as st
from pymongo import MongoClient, errors
from datetime import datetime
from initialiseapp import get_chroma_instance, get_mongodb_instance


def ui_chat_history():
    st.title("Chatbot: Load and Display Chat History")

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
        
        # User input for continuing the chat
        #user_input = st.text_input("You:", "")
        if st.button("re-start from here"):
            st.session_state.selected_chat = st.session_state["current_session"]
            st.session_state.ui_mode = "default"
            print("hello kitty")
            #if user_input:
                # Add user input to session history
                #st.session_state["current_session"].append({"role": "user", "content": user_input})

                # Generate bot response (dummy response here)
                #bot_response = f"Echo: {user_input}"
                #st.session_state["current_session"].append({"role": "bot", "content": bot_response})



ui_chat_history()