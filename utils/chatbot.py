import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load environment variables in case this module is imported standalone
dotenv.load_dotenv()

SYSTEM_PROMPT = """You are DocSensei, a helpful AI assistant. Answer the user's question using ONLY the provided context from uploaded documents. 
If the context does not contain the answer, politely state that you do not know the answer based on the uploaded documents. Do not make up information or answer from external knowledge.

Context:
{context}

Question:
{question}
"""

def query_chatbot(question: str, vector_store, k: int = 4):
    """
    Retrieves relevant text chunks from the vector store and queries Google Gemini API
    to perform question answering.
    Returns:
        dict: {"answer": str, "source_documents": list}
    """
    if not vector_store:
        return {
            "answer": "⚠️ No document index found. Please upload documents to build the knowledge database first.",
            "source_documents": []
        }
        
    try:
        # Perform similarity search
        retrieved_docs = vector_store.similarity_search(question, k=k)
        
        # Build context string
        context_text = ""
        for idx, doc in enumerate(retrieved_docs):
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            page = doc.metadata.get("page", "unknown")
            context_text += f"\n--- Source: {source}, Page: {page} ---\n{doc.page_content}\n"
            
        # Format prompt and invoke model
        prompt = SYSTEM_PROMPT.format(context=context_text, question=question)
        
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        response = llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "answer": response.content,
            "source_documents": retrieved_docs
        }
    except Exception as e:
        return {
            "answer": f"❌ Error querying Gemini API: {str(e)}",
            "source_documents": []
        }
