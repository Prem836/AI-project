import time
from contextlib import contextmanager

@contextmanager
def time_it():
    """
    Context manager to measure execution time of a block.
    Usage:
        with time_it() as timer:
            # do work
        elapsed_time = timer.elapsed
    """
    class Timer:
        def __init__(self):
            self.start = time.perf_counter()
            self.elapsed = 0.0

        def stop(self):
            self.elapsed = time.perf_counter() - self.start

    t = Timer()
    yield t
    t.stop()

def get_document_metrics(documents):
    """
    Computes statistics from a list of loaded documents.
    Returns a dict with doc count, page count, and total character length.
    """
    doc_count = len(documents)
    page_count = 0
    total_chars = 0
    
    # Calculate pages and length
    for doc in documents:
        metadata = doc.get("metadata", {})
        page_count += metadata.get("total_pages", 1)
        total_chars += len(doc.get("text", ""))
        
    return {
        "doc_count": doc_count,
        "page_count": page_count,
        "total_chars": total_chars
    }

def sanitize_filename(filename: str) -> str:
    """
    Removes duplicated extensions like .docx.docx or .pdf.pdf from filenames.
    Example: 'Summer_Training_Report_WebRAG.docx.docx' -> 'Summer_Training_Report_WebRAG.docx'
    """
    if not filename:
        return "unknown"
    import re
    return re.sub(r'(\.(docx|pdf))(?:\1)+$', r'\1', filename, flags=re.IGNORECASE)
