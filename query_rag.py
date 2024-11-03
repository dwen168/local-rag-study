from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
import json


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# create an router prompt


# Test
# https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag_local/#components

def retrieve_from_db(query_text: str, db, k=5):
    
    retriever = db.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query_text)
    doc_txt = docs[1].page_content

    ### Retrieval Grader
    # Doc grader instructions
    doc_grader_instructions = """You are a grader assessing relevance of a retrieved document to a user question.

    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant."""

    # Grader prompt
    doc_grader_prompt = """Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}. 

    This carefully and objectively assess whether the document contains at least some information that is relevant to the question.

    Use the chromadb for questions on these topics. For all else, and especially for current events, use othersource.

    Return JSON with single key, datasource, that is 'chromadb' or 'othersource' depending on the question.

    Format the JSON in a single row."""

    doc_grader_prompt_formatted = doc_grader_prompt.format(
        document=doc_txt, question=query_text
    )
    llm_json_mode = Ollama(model="llama3:latest", format="json")
    result = llm_json_mode.invoke(
        [SystemMessage(content=doc_grader_instructions)]
            + [HumanMessage(content=doc_grader_prompt_formatted)]
    )
    print("routering....")
    print(result.strip())
    result = json.loads(result.strip())


    if result["datasource"] == "chromadb":
        """Retrieves the most similar documents from the Chroma DB."""
        vectordbresults = db.similarity_search_with_score(query_text, k=5)
        return vectordbresults
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
    return f"{response_text}\n\nSources: {sources}"

def query_rag(query_text: str, db, selected_model):

    # Step 1: Retrieve relevant documents - check grade meet our requirement
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
        return formatted_response
    else:
        # Fallback: If no documents were found, query Ollama directly without context
        print("No relevant documents found in the DB, querying Ollama directly...")
        response_text = query_ollama_model(query_text, selected_model)
        formatted_response = f"No knowledge was found in local vector database, there is the response from {selected_model} \n\n {response_text}"
        #print(formatted_response)
        return response_text

