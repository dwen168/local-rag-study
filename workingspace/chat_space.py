import streamlit as st
import streamlit.components.v1 as components
from query_rag import query_rag
from markmapcomponent import create_markmap_html, get_binary_file_downloader_html
from initialiseapp import get_chroma_instance, get_mongodb_instance
from langchain_community.llms import Ollama
from models import get_list_of_models
from datetime import datetime
from streamlit_mic_recorder import speech_to_text

def ui_chatspace():
    st.title("📚 Ask Me Anything!")
    st.write("I'll dig through your uploaded knowledge base to find the answer—like a librarian on a caffeine rush! If it's not there, don't worry, I'll improvise and give it my best shot!")
    if "list_of_models" not in st.session_state:
        st.session_state["list_of_models"] = get_list_of_models()
    
    selected_model = st.sidebar.selectbox(
        "Select a LLM model:", st.session_state["list_of_models"]
    )

    if st.session_state.get("selected_model") != selected_model:
        st.session_state["selected_model"] = selected_model
        st.session_state["llm"] = Ollama(model=selected_model)

    if 'mindmap_from_voc' not in st.session_state:
        st.session_state["mindmap_from_voc"] = '' 
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    if 'historyheader' not in st.session_state:
        st.session_state["historyheader"] = 'Start a new conversion here....'
    else:
        st.subheader (st.session_state["historyheader"])
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    #initialise chat_input
    if prompt := st.chat_input("Question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = get_rag_response(prompt)
            generate_mindmap(prompt,response)

    # sidebar menu
    if st.sidebar.button("Open a new talk",icon="😃",use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["historyheader"] = 'Start a new conversion here....'
        st.rerun()

    if st.sidebar.button("Save my conversion", icon=":material/save:",use_container_width=True):
        if st.session_state["messages"]:
            # Prepare the chat history document for saving
            chat_entry = {
                "timestamp": datetime.now(),
                "user_id": st.session_state.user_state['user_id'],
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
        else:
            st.write ("you have not asked me anything yet! Ask me something first....")

    with st.sidebar:
        st.write("---")
        st.write("Try voice input:")
        voice_question = record_voice()
        if voice_question:
            st.session_state.messages.append({"role": "user", "content": voice_question})
            with st.chat_message("assistant"):
                response = get_rag_response(voice_question)
                mindmap_from_voc = generate_mindmap(voice_question, response)
                st.session_state["mindmap_from_voc"] = mindmap_from_voc
                st.rerun()
    
    if len(st.session_state["mindmap_from_voc"]) > 1:
        st.subheader("Generated Mind Map")
        html_content = create_markmap_html(st.session_state["mindmap_from_voc"])
        components.html(html_content, height=400)
        st.markdown(get_binary_file_downloader_html(html_content), unsafe_allow_html=True) 
        st.session_state["mindmap_from_voc"] = ''


def get_rag_response(query):
    with st.spinner("I am thinking...."):
        response = query_rag(
                query,
                get_chroma_instance(),
                st.session_state["selected_model"],
                st.session_state.user_state['user_id'],
        ) 
    if "mind_map_mark" in response.lower():
        stream = response[response.find("mind_map_mark") + len("mind_map_mark"):].strip()
    else:
        stream = response
    st.session_state.messages.append({"role": "assistant", "content": stream})
    st.write(stream)
    return response

def generate_mindmap(query, rag_response):
    str_mindmap = ''
    if "mind_map_mark" in rag_response.lower():
        stream = rag_response[rag_response.find("mind_map_mark") + len("mind_map_mark"):].strip()
    else:
        stream = rag_response
    if ("mind map" in rag_response.lower() and "mind map" in query.lower()) or "mind_map_mark" in rag_response.lower():
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

    return str_mindmap
    



def record_voice(language="en"):
    # https://github.com/B4PT0R/streamlit-mic-recorder?tab=readme-ov-file#example

    state = st.session_state

    if "text_received" not in state:
        state.text_received = []

    with st.spinner("Taking your voice..."):
        text = speech_to_text(
            start_prompt="🎙️ Click and speak to ask question",
            stop_prompt="🔴 Stop recording 🔴",
            language=language,
            use_container_width=True,
            just_once=True,
        )

    if text:
        state.text_received.append(text)

    result = ""
    for text in state.text_received:
        result += text

    state.text_received = []

    return result if result else None


ui_chatspace()