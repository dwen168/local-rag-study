import streamlit as st
import streamlit.components.v1 as components
from query_rag import query_rag
from markmapcomponent import create_markmap_html, get_binary_file_downloader_html
from initialiseapp import get_chroma_instance, get_mongodb_instance
from langchain_community.llms import Ollama
from models import get_list_of_models
from datetime import datetime
from streamlit_mic_recorder import speech_to_text
import os
import streamlit as st
import ollama
from PIL import Image
import matplotlib.pyplot as plt

def ui_visionchat():
    st.title("Upload an image and ask me anything!")


    col1, col2 = st.columns([1, 1])
    
    
    #pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'


    if 'math_quiz' not in st.session_state:
        st.session_state["math_quiz"] = '' 
    # File uploader
    with col1:
        uploaded_visionfile = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

        if uploaded_visionfile is not None:
            image = Image.open(uploaded_visionfile)
            st.image(image, caption="Uploaded Image")

            image_path = uploaded_visionfile.name 
            image.save(image_path, optimize=True, quality=70)

    
            quiz = st.text_input("You question here...")
            if st.button("Submit question"):
                quiz_response = query_ollama_vision(image_path, quiz)
                st.session_state["math_quiz"] = quiz_response
                with col2:
                    st.write(quiz_response)

def query_ollama_vision(image_path, query_text):
    if not os.path.exists(image_path):
        return "Error: Image path is invalid or the file does not exist."

    if query_text.strip() == '':
        query_text = "describe what is in the picture"

    try:
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': query_text,
                'images': [image_path]
            }]
        )
    except Exception as e:
        return f"Error: {str(e)}"

    
    return response.message.content


ui_visionchat()