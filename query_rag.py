from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def retrieve_from_db(query_text: str, db, k=5):
    """Retrieves the most similar documents from the Chroma DB."""
    try:
        # Search the database with similarity score
        print("Query Chroma DB")
        results = db.similarity_search_with_score(query_text, k=k)
        if not results:
            raise ValueError("No relevant documents found in the database.")
        print("Result from Chroma DB")
        print(results)
        return results
    except Exception as e:
        print(f"Error retrieving from DB: {e}")
        return None

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

def format_response(response_text: str, sources: list):
    """Formats the final response with the answer and the sources."""
    return f"Response: {response_text}\nSources: {sources}"

def query_rag(query_text: str, db, selected_model):

    # Step 1: Retrieve relevant documents
    results = retrieve_from_db(query_text, db)
    
    if results:
        # Step 3: Prepare the context from the retrieved documents
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        # Step 4: Create the prompt for Ollama
        prompt = create_prompt(query_text, context_text)
        
        # Step 5: Query Ollama with the prompt
        response_text = query_ollama_model(prompt, selected_model)
        
        # Step 6: Extract document sources
        sources = [doc.metadata.get("id", None) for doc, _score in results]
        
        # Step 7: Format and return the response
        formatted_response = format_response(response_text, sources)
        print(formatted_response)
        return response_text
    else:
        # Fallback: If no documents were found, query Ollama directly without context
        print("No relevant documents found in the DB, querying Ollama directly...")
        response_text = query_ollama_model(query_text, selected_model)
        formatted_response = format_response(response_text, [])
        print(formatted_response)
        return response_text

