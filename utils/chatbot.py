import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from utils.helpers import sanitize_filename

# Load environment variables in case this module is imported standalone
dotenv.load_dotenv()

SYSTEM_PROMPT = """You are DocSensei, a helpful AI assistant. Answer the user's question using ONLY the provided context from uploaded documents and the chat history. 
If the context does not contain the answer, politely state that you do not know the answer based on the uploaded documents. Do not make up information or answer from external knowledge.

Context:
{context}

Chat History:
{chat_history}

Question:
{question}
"""

def query_chatbot(question: str, vector_store, chat_history=None, k: int = 4):
    """
    Retrieves relevant text chunks from the vector store and queries Google Gemini API
    to perform question answering, incorporating conversation history.
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
            source = sanitize_filename(os.path.basename(doc.metadata.get("source", "unknown")))
            page = doc.metadata.get("page", "unknown")
            context_text += f"\n--- Source: {source}, Page: {page} ---\n{doc.page_content}\n"
            
        # Format chat history text (last 6 turns)
        history_text = ""
        if chat_history:
            for msg in chat_history[-6:]:
                role = "User" if msg["role"] == "user" else "DocSensei"
                history_text += f"{role}: {msg['content']}\n"
                
        # Format prompt and invoke model
        prompt = SYSTEM_PROMPT.format(context=context_text, chat_history=history_text, question=question)
        
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

def generate_document_summary(processed_files):
    """
    Generates a structured summary of all processed files using Gemini API.
    """
    if not processed_files:
        return "⚠️ No documents loaded to summarize."
        
    try:
        combined_text = ""
        for name, data in processed_files.items():
            # Get document text
            doc_text = ""
            if "docs" in data and data["docs"]:
                # Concatenate text from doc dicts
                doc_text = "\n".join([doc["text"] for doc in data["docs"]])
            
            # Truncate text per file to stay within prompt limits
            truncated_text = doc_text[:8000]
            combined_text += f"\n--- Document: {name} ---\n{truncated_text}\n"
            
        summary_prompt = f"""You are DocSensei. Analyze the provided text extracts of the uploaded document(s) and generate a structured summary.
Your summary must contain:
1. **Core Overview**: A brief 2-3 sentence overview of what the document is about.
2. **Key Themes & Bullet Points**: Main ideas, topics, or sections covered in the document.
3. **Recommended Questions**: Provide 3-4 interesting questions that the user can ask DocSensei about these documents.

Text extracts:
{combined_text}
"""
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    except Exception as e:
        return f"❌ Error generating summary: {str(e)}"
