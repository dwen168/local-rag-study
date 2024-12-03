from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from initialiseapp import get_chroma_instance
from langchain_community.llms import Ollama

def conversationalretrieval(query, chat_history, selected_model):
    # Contextualize question
    contextualize_q_system_prompt = (
        """
        Given a chat history and the latest user question 
        which might reference context in the chat history, 
        formulate a standalone question which can be understood 
        without the chat history. Do NOT answer the question, just 
        reformulate it if needed and otherwise return it as is.
        """
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    llm = Ollama(model=selected_model)
    db = get_chroma_instance()
    retriever = db.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {"user_id": "admin"} 
        }
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Answer question
    qa_system_prompt = (
        """
        You are an assistant for question-answering tasks. Use 
        the following pieces of retrieved context to answer the 
        question. If you don't know the answer, just say that you 
        don't know. And ask user if they want to extend their search out of local RAG database. 
        If they agree to extend their search, just answer their questions with your maximum knowledge without retrieving the data from local RAG
        {context}
        """
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt) 
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )

    response = rag_chain.invoke({"input": query, "chat_history": chat_history})

    # Usage: chat_history = [] # Collect chat history here (a sequence of messages) 
    return response['answer']
