from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}

If the question is about to generate a mind map of the context, return markdown formatted answer as the input for mind map software.
The markdown formatted answer should be always start with Mind Map

If the question is about something else, just reply with the knowledge you have.
"""


def create_prompt(query_text: str, context_text: str):
    """Formats the prompt for the LLM using the retrieved context and query."""
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    return prompt

def query_ollama_model(prompt: str, model_name):
    """Queries the Ollama model and returns the response."""
    try:
        model = Ollama(model=model_name)
        response_text = model.invoke(prompt)
        return response_text
    except Exception as e:
        print(f"Error invoking Ollama model: {e}")
        return None