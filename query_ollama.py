from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama


def query_ollama_model(prompt: str, model_name):
    """Queries the Ollama model and returns the response."""
    try:
        model = Ollama(model=model_name)
        response_text = model.invoke(prompt)
        return response_text
    except Exception as e:
        print(f"Error invoking Ollama model: {e}")
        return None