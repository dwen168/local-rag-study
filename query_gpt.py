import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def query_gpt_model(selected_model, context_text):
    response_text_api = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": context_text}
                ],
                max_tokens=1000,  # Adjust max_tokens as needed
            )
    response_text = response_text_api.choices[0].message.content
    return response_text