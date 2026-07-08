from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_text(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits the loaded document contents into smaller manageable chunks for embedding generation.
    Supports page-aware splitting to retain page numbers for citations.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for doc in documents:
        metadata = doc.get("metadata", {})
        source = metadata.get("source", "unknown")
        total_pages = metadata.get("total_pages", 1)
        pages = metadata.get("pages", [])
        
        if pages:
            # Page-aware chunking
            for page in pages:
                page_num = page.get("page_num", 1)
                page_text = page.get("text", "")
                if not page_text.strip():
                    continue
                
                # Split this page's text
                page_chunks = splitter.split_text(page_text)
                for chunk in page_chunks:
                    chunks.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": source,
                            "page": page_num,
                            "total_pages": total_pages
                        }
                    ))
        else:
            # Fallback: split the whole document text
            doc_text = doc.get("text", "")
            if doc_text.strip():
                doc_chunks = splitter.split_text(doc_text)
                for chunk in doc_chunks:
                    chunks.append(Document(
                        page_content=chunk,
                        metadata={
                            "source": source,
                            "page": 1,
                            "total_pages": 1
                        }
                    ))
                    
    return chunks
