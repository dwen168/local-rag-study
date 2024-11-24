import streamlit as st
import streamlit.components.v1 as components
from query_rag import query_rag
from markmapcomponent import create_markmap_html, get_binary_file_downloader_html
from initialiseapp import get_chroma_instance, get_mongodb_instance
from langchain_community.llms import Ollama
from models import get_list_of_models
from datetime import datetime

def ui_chatspace():
    st.title("📚 Ask Me Anything!")
    st.write("I'll dig through your uploaded knowledge base to find the answer—like a librarian on a caffeine rush! If it's not there, don't worry, I'll improvise and give it my best shot!")
    if "list_of_models" not in st.session_state:
        st.session_state["list_of_models"] = get_list_of_models()
    
    if "db" not in st.session_state:
        st.session_state["db"] = get_chroma_instance()
    
    selected_model = st.sidebar.selectbox(
        "Select a LLM model:", st.session_state["list_of_models"]
    )

    if st.session_state.get("selected_model") != selected_model:
        st.session_state["selected_model"] = selected_model
        st.session_state["llm"] = Ollama(model=selected_model)
    
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
            response = query_rag(
                prompt,
                st.session_state["db"],
                #get_chroma_instance(),
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

    if st.button("Save"):
        if st.session_state["messages"]:
            # Prepare the chat history document for saving
            chat_entry = {
                "timestamp": datetime.now(),
                "chat_history": st.session_state["messages"],
            }
            # Save to MongoDB
            mongodb = get_mongodb_instance()
            if mongodb != None:
                collection = mongodb["chat_history"]
                collection.insert_one(chat_entry)
                st.success("Chat history saved successfully!")
            else:
                st.error("Could not connect to chat history database. Your chat history won't be saved!")


ui_chatspace()