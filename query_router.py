import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, timeout
from langchain_community.llms.ollama import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
import json

# https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag_local/#components

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

### Retrieval Grader
# Doc grader instructions
DOC_GRADER_INSTRUCTIONS = """You are a grader assessing relevance of a retrieved document to a user question.

    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant."""

    # Grader prompt
DOC_GRADER_PROMPT = """Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}. 

    This carefully and objectively assess whether the document contains at least some information that is relevant to the question.

    Use the chromadb for questions on these topics. For all else, and especially for current events, use othersource.

    Return JSON with single key, datasource, that is 'chromadb' or 'othersource' depending on the question.

    Format the JSON in a single row."""

def doc_grader_prompt_formatted(doc_txt, query_txt):
    doc_grader_prompt_formatted = DOC_GRADER_PROMPT.format(
        document=doc_txt, question=query_txt
    )
    return doc_grader_prompt_formatted


def ollama_router(selected_model, human_content):
    llm_json_mode = Ollama(model=selected_model, format="json")
    result = llm_json_mode.invoke(
            [SystemMessage(content=DOC_GRADER_INSTRUCTIONS)]
                + [HumanMessage(content=human_content)]
        )
    print(f"routering....{selected_model}")
    print(result.strip())
    result = json.loads(result.strip())
    return result


def gpt_router(selected_model, human_content,timeout_seconds=5):
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": DOC_GRADER_INSTRUCTIONS},
                {"role": "user", "content": human_content}
            ],
            max_tokens=1000,  # Adjust max_tokens as needed
            timeout=timeout_seconds
        )
        print(f"routering....{selected_model}")
        result =  json.loads(response.choices[0].message.content.strip())
        print(result)
        return result
    except timeout.Timeout as e:
        return f"Request timed out after {timeout_seconds} seconds. Please try again."
    except OpenAIError as e:
        return f"An OpenAI error occurred: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"