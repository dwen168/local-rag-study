from langchain.prompts import ChatPromptTemplate

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}

If the question is not about a mind map, respond as normal.

If the question is about generating a mind map:
- Your response MUST start with "mind_map_mark".
- Format the response in markdown for Markmap.

Example of mind map response:
Question: Generate a mind map of Python programming features.
Response:
mind_map_mark
# Python Features
- Simplicity
- Readability
- Applications
  - Web Development
  - Data Analysis
"""


def create_prompt(query_text: str, context_text: str):
    """Formats the prompt for the LLM using the retrieved context and query."""
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    return prompt