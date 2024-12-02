import os
from dotenv import load_dotenv
from openai import OpenAI
from query_router import ollama_router, gpt_router, doc_grader_prompt_formatted
from query_ollama import query_ollama_model
from query_gpt import query_gpt_model
from create_prompts import create_prompt


load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def retrieve_from_db(query_text: str, db, selected_model, user_id, k=5):
    
    retriever = db.as_retriever(
        search_kwargs={
            "k": k,
            "filter": {"user_id": user_id} 
        }
    )
    try:
        docs = retriever.invoke(query_text)
        if docs:
            doc_txt = docs[1].page_content
        else:
            print("No documents found for the query.")
            return None
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return None

    doc_grader_prompt_formatted_str = doc_grader_prompt_formatted(doc_txt, query_text)

    if selected_model != "gpt-4o-mini":
        result = ollama_router(selected_model, doc_grader_prompt_formatted_str)
    else:
        result = gpt_router(selected_model, doc_grader_prompt_formatted_str)
    
    if 'error' in str(result).lower() and 'incorrect api key provided:' in str(result).lower():
        return result
    elif result["datasource"] == "chromadb":
        #Retrieves the most similar documents from the Chroma DB
        vectordbresults = db.similarity_search_with_score(
            query_text,
            k=k,
            filter={"user_id": user_id},
        )
        return vectordbresults
    return None
    


def format_response(response_text: str, sources: list):
    """Formats the final response with the answer and the sources."""
    return f"{response_text}\n\nSources: {sources}"

def query_rag(query_text: str, db, selected_model, user_id, chat_mode):

    # Check the input 
    if query_text.strip() == '' or len(query_text.strip()) == 0:
        results = "please ask me anything..."
        return results

    if chat_mode == 'Chat Chain':
        print("do some thing")
        print(chat_mode)

    # Step 1: Retrieve relevant documents - check grade meet our requirement
    results = retrieve_from_db(query_text, db, selected_model, user_id)
    
    if 'error' in str(results).lower() and 'incorrect api key provided:' in str(results).lower():
        return results
    if results:
        # Step 3: Prepare the context from the retrieved documents
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        # Step 4: Create the prompt for Ollama with the context of retrieved documents
        prompt = create_prompt(query_text, context_text)
        
        # Step 5: Query Ollama with the prompt
        response_text = ''
        if selected_model != "gpt-4o-mini":
            response_text = query_ollama_model(prompt, selected_model)
        else:
            response_text = query_gpt_model(selected_model, prompt)
        
        # Step 6: Extract document sources
        sources = [doc.metadata.get("id", None) for doc, _score in results]
        
        # Step 7: Format and return the response
        formatted_response = format_response(response_text, sources)

        print(formatted_response)
        return formatted_response
    else:
        # Fallback: If no documents were found, query Ollama directly without context
        response_text = ''
        if selected_model != "gpt-4o-mini":
            print("No relevant documents found in the DB, querying Ollama directly...")
            response_text = query_ollama_model(query_text, selected_model)
        else:
            print("No relevant documents found in the DB, querying OpenAI directly...")
            response_text = query_gpt_model(selected_model, query_text)
        formatted_response = f"No knowledge was found in local vector database, there is the response from {selected_model} \n\n {response_text}"
        #print(formatted_response)
        return response_text

