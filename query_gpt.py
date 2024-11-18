import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, timeout


load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def query_gpt_model(selected_model, context_text, timeout_seconds = 5):
    try:
        response_text_api = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": context_text}
                ],
                max_tokens=1000,  # Adjust max_tokens as needed
                timeout=timeout_seconds
            )
        response_text = response_text_api.choices[0].message.content
        return response_text
    except timeout.Timeout as e:
        return f"Request timed out after {timeout_seconds} seconds. Please try again."
    except OpenAIError as e:
        return f"An OpenAI error occurred: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"