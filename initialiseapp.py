from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pymongo import MongoClient,errors

CHROMA_PATH = "chroma"

def get_embedding_function():
    #embeddings = BedrockEmbeddings(
        #credentials_profile_name="default", region_name="us-east-1"
    #)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

def get_chroma_instance():
    try:
        chromadb = Chroma(
                persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
            )
    except Exception as e:
        print(f"An error occurred while initializing Chroma DB: {e}")
        return None
    return chromadb


def get_mongodb_instance():
    mongo_uri = "mongodb://localhost:27017"

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Access the database and collection
        # Database and collection setup
        db_name = "chatbot_db"
        collection_name = "chat_history"
        mongodb = client[db_name]

        # Ensure collection exists
        if collection_name not in mongodb.list_collection_names():
            mongodb.create_collection(collection_name)
    except errors.ServerSelectionTimeoutError:
        return None

    return mongodb


