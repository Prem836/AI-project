import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings

@st.cache_resource
def get_embeddings_model():
    """
    Initializes and returns the Hugging Face local embeddings model.
    Uses streamlit's cache_resource to keep the model loaded in memory.
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
