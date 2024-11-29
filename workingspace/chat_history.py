import streamlit as st
from initialiseapp import get_mongodb_instance
from collections import defaultdict
from datetime import datetime


def ui_chat_history():
    st.markdown(f"<h3 style='font-size:36px;'> Feel free to dive into your chat history—it's like a treasure trove of past conversations, and hey, the chat's still open for more! Keep the banter going! </h3>", unsafe_allow_html=True)

    user_id = st.session_state.user_state['user_id']
    
    # Initialize session history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "current_session" not in st.session_state:
        st.session_state["current_session"] = []

    mongodb = get_mongodb_instance()
    if mongodb != None:
        try:
            collection = mongodb["chat_history"]
            query_history = {"user_id": user_id}
            chat_history = list(collection.find(query_history).sort("timestamp", -1).limit(30))  # Sort by timestamp, newest first
            if chat_history:
                grouped_history = defaultdict(list)
                for chat_entry in chat_history:
                    date = chat_entry.get("timestamp", datetime.now()).strftime("%Y-%m-%d")
                    grouped_history[date].append(chat_entry)
                
                for date, entries in grouped_history.items():
                    st.subheader(f"Chat History: -{date}")
                    for idx, chat_entry in enumerate(entries):
                        timestamp = chat_entry.get("timestamp", "Unknown Time").strftime("%Y-%m-%d %H:%M:%S")
                        first_user_message = next((msg["content"] for msg in chat_entry["chat_history"] if msg["role"] == "user"), "No user messages")
                        button_label = f"{timestamp} - {first_user_message[:50]}..."
                        if st.button(button_label, key=f"session_{idx}"):
                            # Store selected session in session state
                            st.session_state["current_session"] = chat_entry["chat_history"]
                            st.session_state["timestamp"] = timestamp
                    st.write("---")
            else:
                st.info("No chat history found in the database.")
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
    else:
        st.error(f"Error loading chat history")

    # Chatbot functionality (if a session is selected)
    if st.session_state["current_session"]:
    # Display the selected session
        st.markdown(f"<h3 style='font-size:16px;'>Continuing Chat - {st.session_state['timestamp']}</h3>", unsafe_allow_html=True)
        for message in st.session_state["current_session"]:
            if message["role"] == "user":
                st.markdown(f"<p style='color:blue;'>🤠You: {message['content']}</p>", unsafe_allow_html=True)
            else:
                st.text(f"🤖Assistant: {message['content']}")
                #st.markdown(f"<p style='color:green;'>assistant: {message['content']}</p>", unsafe_allow_html=True)
                #st.markdown(f"<div style='color:dark grey;'>🤖Assistant: {message['content']}</div>", unsafe_allow_html=True)
        
        #st.session_state.selected_chat = st.session_state["current_session"]
        if st.button("Re-open this talk?", icon="✈️"):
            st.session_state["messages"] = st.session_state["current_session"]
            st.session_state["historyheader"] = f"Continuing Chat - {st.session_state['timestamp']}"
            st.page_link("workingspace/chat_space.py", label="Click Me to re-open this talk", icon="😃")

ui_chat_history()
