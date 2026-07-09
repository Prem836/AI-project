import os
from langchain_community.vectorstores import FAISS

def create_vector_store(chunks, embeddings_model, store_path: str = "vector_db/faiss_index"):
    """
    Creates a FAISS vector store from the text chunks and embeddings model,
    saves it locally, and returns the store instance.
    """
    if not chunks:
        raise ValueError("Cannot create vector store: chunk list is empty.")
        
    db = FAISS.from_documents(chunks, embeddings_model)
    
    # Ensure directory exists and save local index
    os.makedirs(store_path, exist_ok=True)
    db.save_local(store_path)
    
    return db

def load_vector_store(store_path: str, embeddings_model):
    """
    Loads an existing FAISS vector store from a local path.
    """
    # Check if index files exist (faiss uses index.faiss and index.pkl)
    index_file = os.path.join(store_path, "index.faiss")
    pkl_file = os.path.join(store_path, "index.pkl")
    if not (os.path.exists(index_file) and os.path.exists(pkl_file)):
        return None
        
    return FAISS.load_local(
        store_path, 
        embeddings_model, 
        allow_dangerous_deserialization=True
    )
