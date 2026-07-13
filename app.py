import streamlit as st
import os
from utils.loader import load_document
from utils.splitter import split_text
from utils.embeddings import get_embeddings_model
from utils.vectorstore import create_vector_store
from utils.chatbot import query_chatbot, generate_document_summary
from utils.helpers import get_document_metrics, time_it

# Developer mode toggle. Set to True to display developer test/clear buttons.
# Can be dynamically enabled by visiting: http://localhost:8501/?dev=true
DEVELOPER_MODE = False
try:
    if hasattr(st, "query_params"):
        DEVELOPER_MODE = st.query_params.get("dev", "false").lower() == "true"
except Exception:
    pass

# Helper to update vector store
def update_vector_store():
    """
    Rebuilds or clears the FAISS vector store based on current processed files.
    """
    all_chunks = []
    for name, data in st.session_state.processed_files.items():
        all_chunks.extend(data["chunks"])
        
    if all_chunks:
        try:
            embeddings_model = get_embeddings_model()
            st.session_state.vector_store = create_vector_store(all_chunks, embeddings_model)
        except Exception as e:
            st.error(f"❌ Error building vector store: {str(e)}")
    else:
        st.session_state.vector_store = None
        import shutil
        if os.path.exists("vector_db"):
            shutil.rmtree("vector_db", ignore_errors=True)

# Set page configuration with premium tab title and layout
st.set_page_config(
    page_title="DocSensei - AI Document QA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS styling for visual excellence (Dark theme, glassmorphism, smooth animations)
st.markdown("""
<style>
    /* Main App Background & Text */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1e1e2f 100%);
        color: #f0f2f6;
    }
    
    /* Premium Title Header */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    .main-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa 0%, #ec4899 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 300;
        margin-top: 0;
    }
    
    /* Card design with glassmorphism & hover state transitions */
    .card {
        background: rgba(30, 41, 59, 0.4);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover {
        box-shadow: 0 10px 30px rgba(167, 139, 250, 0.08);
        border-color: rgba(167, 139, 250, 0.25);
        transform: translateY(-2px);
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Tech Stack tag style */
    .tech-tag {
        display: inline-block;
        background: rgba(167, 139, 250, 0.15);
        color: #c084fc;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    /* Day progress status classes */
    .status-badge {
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        float: right;
    }
    .status-completed {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
    }
    .status-pending {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
    }
    .status-upcoming {
        background: rgba(148, 163, 184, 0.1);
        color: #94a3b8;
    }
    
    /* Stats box design for document metrics */
    .stat-container {
        display: flex;
        justify-content: space-between;
        gap: 0.8rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .stat-box {
        flex: 1;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.8rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-box:hover {
        transform: translateY(-2px);
        border-color: rgba(167, 139, 250, 0.3);
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #a78bfa;
        margin-bottom: 0.2rem;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Custom file uploader style */
    div[data-testid="stFileUploader"] {
        background-color: rgba(15, 23, 42, 0.2) !important;
        border: 1px dashed rgba(167, 139, 250, 0.2) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: border-color 0.3s ease, background-color 0.3s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(167, 139, 250, 0.6) !important;
        background-color: rgba(15, 23, 42, 0.4) !important;
    }
    
    /* Monospace previewer field styling */
    div[data-testid="stTextArea"] textarea {
        font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
        font-size: 0.85rem !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        line-height: 1.5 !important;
    }
    
    /* Global button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        text-align: center !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        filter: brightness(1.1) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Input text elements styling */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 1rem 0;'><h2 style='color:#a78bfa; font-weight:700;'>🎓 DocSensei</h2><p style='color:#64748b; font-size:0.9rem;'>AI PDF & DOCX QA System</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("📤 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="doc_uploader"
    )
    
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "summary" not in st.session_state:
        st.session_state.summary = None

    if uploaded_files:
        st.session_state.last_action = "upload"
        # Identify removed files
        current_uploaded_names = [f.name for f in uploaded_files]
        removed_any = False
        for name in list(st.session_state.processed_files.keys()):
            if name not in current_uploaded_names:
                del st.session_state.processed_files[name]
                st.session_state.summary = None
                removed_any = True
                
        # Identify files that need to be processed
        new_files_to_process = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
        
        if new_files_to_process:
            st.session_state.summary = None
            os.makedirs("uploads", exist_ok=True)
            with st.spinner("🔍 Extracting text from documents..."):
                for f in new_files_to_process:
                    file_path = os.path.join("uploads", f.name)
                    try:
                        # Write file content
                        with open(file_path, "wb") as temp_file:
                            temp_file.write(f.getbuffer())
                        # Load, extract text and split into chunks
                        with time_it() as timer:
                            docs = load_document(file_path)
                            chunks = split_text(docs)
                        st.session_state.processed_files[f.name] = {
                            "docs": docs,
                            "chunks": chunks,
                            "time_taken": timer.elapsed,
                            "size": f.size
                        }
                    except Exception as e:
                        st.error(f"❌ Error processing {f.name}: {str(e)}")
            with st.spinner("🧠 Generating embeddings & building FAISS index..."):
                update_vector_store()
        elif removed_any:
            with st.spinner("🧠 Rebuilding FAISS index..."):
                update_vector_store()

        # Collect all successfully loaded documents
        all_documents = []
        for name, data in st.session_state.processed_files.items():
            all_documents.extend(data["docs"])
            
        if all_documents:
            st.success(f"📁 {len(uploaded_files)} file(s) loaded, chunked, and indexed in FAISS!")
        else:
            st.warning("⚠️ No documents could be successfully processed.")
    else:
        # Sync: if uploader is empty but we had uploader files, clear them
        if "last_action" in st.session_state and st.session_state.last_action == "upload":
            if st.session_state.processed_files:
                st.session_state.processed_files.clear()
                update_vector_store()
                st.warning("⚠️ Cache cleared: uploader emptied.")
                
        if not st.session_state.processed_files:
            st.warning("⚠️ No documents uploaded yet. Please upload files to get started.")
        else:
            st.success(f"📁 {len(st.session_state.processed_files)} file(s) loaded, chunked, and indexed in FAISS!")

    # Developer Quick-Load / Reset buttons at the bottom of the Upload card
    if DEVELOPER_MODE and os.path.exists("test_files"):
        test_files = [f for f in os.listdir("test_files") if f.endswith((".pdf", ".docx"))]
        if test_files:
            st.markdown("---")
            st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;'>💡 Developer Quick-Load</p>", unsafe_allow_html=True)
            col_dev1, col_dev2 = st.columns(2)
            with col_dev1:
                if st.button("📁 Load Test Files", use_container_width=True):
                    st.session_state.last_action = "dev_load"
                    loaded_any = False
                    for fname in test_files:
                        file_path = os.path.join("test_files", fname)
                        if fname not in st.session_state.processed_files:
                            try:
                                with time_it() as timer:
                                    docs = load_document(file_path)
                                    chunks = split_text(docs)
                                # Copy to uploads directory to mimic standard upload behavior
                                os.makedirs("uploads", exist_ok=True)
                                dest_path = os.path.join("uploads", fname)
                                import shutil
                                shutil.copy2(file_path, dest_path)
                                
                                st.session_state.processed_files[fname] = {
                                    "docs": docs,
                                    "chunks": chunks,
                                    "time_taken": timer.elapsed,
                                    "size": os.path.getsize(file_path)
                                }
                                st.session_state.summary = None
                                loaded_any = True
                            except Exception as e:
                                st.error(f"❌ Error loading test file {fname}: {str(e)}")
                    if loaded_any:
                        with st.spinner("🧠 Generating embeddings & building FAISS index..."):
                            update_vector_store()
                    st.rerun()
            with col_dev2:
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    st.session_state.processed_files.clear()
                    st.session_state.messages.clear()
                    st.session_state.summary = None
                    if "last_action" in st.session_state:
                        del st.session_state.last_action
                    update_vector_store()
                    st.rerun()

    st.markdown("---")
    st.subheader("🛠 Technologies Used")
    st.markdown("""
    <span class='tech-tag'>Streamlit</span>
    <span class='tech-tag'>LangChain</span>
    <span class='tech-tag'>Hugging Face</span>
    <span class='tech-tag'>FAISS</span>
    <span class='tech-tag'>Google Gemini</span>
    <span class='tech-tag'>PyPDF & Docx</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📅 Project Roadmap & Status")
    st.markdown("""
    * **Day 1: Base UI Setup** <span class='status-badge status-completed'>Completed</span>
    * **Day 2: Doc Loading & Text Extraction** <span class='status-badge status-completed'>Completed</span>
    * **Day 3: Text Chunking** <span class='status-badge status-completed'>Completed</span>
    * **Day 4: Embeddings & Vector Store** <span class='status-badge status-completed'>Completed</span>
    * **Day 5: Gemini LLM Integration** <span class='status-badge status-completed'>Completed</span>
    * **Day 6: Chat History Interface** <span class='status-badge status-completed'>Completed</span>
    * **Day 7: Document Summarization** <span class='status-badge status-completed'>Completed</span>
    * **Day 8: Styling & Custom CSS** <span class='status-badge status-completed'>Completed</span>
    * **Day 9: End-to-End Verification** <span class='status-badge status-pending'>In Progress</span>
    * **Day 10: Final Prep, Report & PPT** <span class='status-badge status-upcoming'>Upcoming</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #475569; font-size:0.8rem;'>DocSensei v1.0.0 &copy; 2026</div>", unsafe_allow_html=True)


# --- MAIN AREA LAYOUT ---
st.markdown("""
<div class="header-container">
    <div class="main-title">DocSensei</div>
    <div class="subtitle">Interact with your PDFs & Word documents using the power of local Embeddings & Google Gemini</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.processed_files:
    # --- LANDING DASHBOARD VIEW ---
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem; background: rgba(30, 41, 59, 0.25); border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.1); margin-bottom: 2rem; backdrop-filter: blur(10px);">
        <p style="font-size: 5.5rem; margin-bottom: 0.5rem; animation: pulse 2s infinite;">🧠</p>
        <h1 style="font-family: 'Outfit', sans-serif; font-weight: 800; background: linear-gradient(90deg, #a78bfa 0%, #ec4899 50%, #f43f5e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; letter-spacing: -0.5px;">Welcome to DocSensei</h1>
        <p style="color: #94a3b8; font-size: 1.15rem; font-weight: 300; max-width: 650px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
            Unlock the hidden insights in your research papers, notes, or business files. Upload PDF or Word documents to instantly chat with them, search keywords, and generate summaries.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards Grid
    col_feat1, col_feat2 = st.columns(2, gap="large")
    with col_feat1:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <h3 style="color: #a78bfa; margin-top: 0; font-family: 'Outfit', sans-serif;">🤖 Context-Aware Q&A Chat</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">Ask questions in natural language. The assistant answers strictly based on the content of your documents with clickable source page citations to prevent hallucinations.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="height: 100%;">
            <h3 style="color: #f43f5e; margin-top: 0; font-family: 'Outfit', sans-serif;">📋 AI-Powered Summarization</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">Generate rich, bulleted summaries of all loaded documents on-demand, including auto-suggested questions tailored specifically to the file content.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_feat2:
        st.markdown("""
        <div class="card" style="height: 100%;">
            <h3 style="color: #ec4899; margin-top: 0; font-family: 'Outfit', sans-serif;">🔍 Highlighting Keyword Search</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">Perform instant keyword searches across all loaded files. Highlights matching text blocks and overlays yellow markers over key terms.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="height: 100%;">
            <h3 style="color: #34d399; margin-top: 0; font-family: 'Outfit', sans-serif;">💾 Secure Local FAISS Database</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">Your documents are chunked and indexed locally using secure sentence embeddings from Hugging Face for privacy and speed.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div style="background: rgba(167, 139, 250, 0.05); border: 1px solid rgba(167, 139, 250, 0.2); padding: 1.2rem; border-radius: 12px; text-align: center; margin-top: 2rem; color: #a78bfa; font-weight: 500;">
        👈 To get started, please drag and drop or choose PDF/DOCX files in the uploader inside the left sidebar.
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# --- WORKSPACE VIEW (FILES LOADED) ---
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    # Collect all loaded docs
    all_documents = []
    for name, data in st.session_state.processed_files.items():
        all_documents.extend(data["docs"])
        
    if all_documents:
        # Metrics Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📊 Extraction & Chunking Metrics")
        metrics = get_document_metrics(all_documents)
        total_chunks = sum(len(data.get("chunks", [])) for data in st.session_state.processed_files.values())
        avg_chunk_size = metrics['total_chars'] / total_chunks if total_chunks > 0 else 0
        
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-box">
                <div class="stat-number">{metrics['doc_count']}</div>
                <div class="stat-label">Documents</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{metrics['page_count']}</div>
                <div class="stat-label">Total Pages</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{total_chunks}</div>
                <div class="stat-label">Total Chunks</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{metrics['total_chars']:,}</div>
                <div class="stat-label">Characters</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 0.85rem; color: #94a3b8; text-align: center; margin-bottom: 1rem;'>💡 Average Chunk Size: <strong>{avg_chunk_size:.1f}</strong> characters &bull; Target Chunk Size: <strong>1000</strong> &bull; Overlap: <strong>200</strong></div>", unsafe_allow_html=True)
        
        # File list detail
        for name, data in st.session_state.processed_files.items():
            chunks_count = len(data.get("chunks", []))
            st.markdown(f"<div style='margin-bottom: 0.5rem;'><span style='color: #a78bfa; font-weight: 500;'>📄 {name}</span> <span style='color: #64748b; font-size: 0.85rem;'>({data['size'] / 1024:.1f} KB) &bull; {chunks_count} chunks generated in {data['time_taken']:.2f}s</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Keyword Search & Highlighting Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔍 Document Keyword Search")
        st.write("Find occurrences of keywords in the document database:")
        search_query = st.text_input("Enter keyword or phrase to search:", key="keyword_search_input")
        if search_query.strip():
            import re
            matches_found = []
            for fname, fdata in st.session_state.processed_files.items():
                doc_text = ""
                if "docs" in fdata and fdata["docs"]:
                    doc_text = "\n".join([doc["text"] for doc in fdata["docs"]])
                
                pattern = re.compile(re.escape(search_query), re.IGNORECASE)
                paragraphs = doc_text.split("\n")
                for para in paragraphs:
                    if search_query.lower() in para.lower() and len(para.strip()) > 5:
                        highlighted = pattern.sub(f"<span style='background-color: #fef08a; color: #1e293b; padding: 0.1rem 0.3rem; border-radius: 4px; font-weight: 600;'>\\g<0></span>", para.strip())
                        matches_found.append({"file": fname, "text": highlighted})
            
            if matches_found:
                st.markdown(f"**Found {len(matches_found)} match(es):**")
                st.markdown("<div style='max-height: 250px; overflow-y: auto; padding-right: 0.5rem;'>", unsafe_allow_html=True)
                for m in matches_found[:12]:
                    st.markdown(f"<div style='background: rgba(255,255,255,0.02); border-left: 3px solid #a78bfa; padding: 0.6rem; margin-bottom: 0.6rem; border-radius: 0 8px 8px 0; font-size: 0.85rem;'><span style='color: #a78bfa; font-weight: 500;'>📄 {m['file']}</span><br/>{m['text']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                if len(matches_found) > 12:
                    st.info(f"Showing first 12 matches of {len(matches_found)}")
            else:
                st.warning("No matches found for the search query.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Text Previewer Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔍 Text Previewer")
        selected_file = st.selectbox(
            "Choose a document to inspect:",
            options=list(st.session_state.processed_files.keys()),
            key="doc_previewer_select"
        )
        if selected_file:
            file_data = st.session_state.processed_files[selected_file]
            full_text = file_data["docs"][0]["text"]
            preview_len = min(1000, len(full_text))
            preview_text = full_text[:preview_len]
            if len(full_text) > 1000:
                preview_text += "\n\n... [Truncated: Showing first 1000 characters] ..."
            st.text_area(
                f"Content Preview ({preview_len:,} / {len(full_text):,} chars):",
                value=preview_text,
                height=200,
                disabled=True,
                key="doc_previewer_area"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Document Summary Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📋 Document Summary")
        
        if st.session_state.summary is None:
            st.write("Generate an AI-powered structured summary of the loaded documents:")
            if st.button("⚡ Generate Summary", use_container_width=True, key="generate_summary_btn"):
                with st.spinner("🧠 Analyzing documents and generating summary..."):
                    st.session_state.summary = generate_document_summary(st.session_state.processed_files)
                st.rerun()
        else:
            st.markdown(st.session_state.summary)
            if st.button("🔄 Regenerate Summary", use_container_width=True, key="regenerate_summary_btn"):
                st.session_state.summary = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # Split subheader, Download, and Clear Chat buttons using columns
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    with col_header1:
        st.subheader("💬 Interactive Assistant")
    with col_header2:
        if st.session_state.processed_files and st.session_state.messages:
            # Generate markdown text for chat history
            md_lines = ["# 🎓 DocSensei - Chat Conversation Log\n"]
            import datetime
            md_lines.append(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            md_lines.append("---\n")
            for msg in st.session_state.messages:
                role_name = "👤 User" if msg["role"] == "user" else "🤖 DocSensei"
                md_lines.append(f"### {role_name}\n{msg['content']}\n")
                if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
                    md_lines.append("\n**Sources Cited:**\n")
                    for src in msg["sources"]:
                        md_lines.append(f"- {src['file']} (Page {src['page']})\n")
                    md_lines.append("\n")
                md_lines.append("---\n")
            chat_md = "".join(md_lines)
            
            st.download_button(
                label="📥 Download Chat",
                data=chat_md,
                file_name="docsensei_chat.md",
                mime="text/markdown",
                use_container_width=True,
                key="download_chat_history_btn"
            )
    with col_header3:
        if st.session_state.processed_files and st.session_state.messages:
            if st.button("🧹 Clear Chat", use_container_width=True, key="clear_chat_history_btn"):
                st.session_state.messages.clear()
                st.rerun()
    
    # Placeholder layout for Day 1 & Day 2
    if not st.session_state.processed_files:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
            <p style="font-size: 4rem; margin-bottom: 1rem;">📚</p>
            <h3>Knowledge Database Empty</h3>
            <p>Upload documents in the left panel or load test files to allow the assistant to read and answer questions from them.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Chat Message History Container
        chat_container = st.container(height=450)
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align: center; padding: 2rem 1rem; color: #64748b;">
                    <p style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</p>
                    <h4>Hello! I am DocSensei</h4>
                    <p style="font-size: 0.9rem;">Ask me any questions about the loaded documents. I can search their content, generate citations, and recall our conversation history.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                        if msg["role"] == "assistant":
                            if "latency" in msg:
                                st.markdown(f"<p style='color: #64748b; font-size: 0.75rem; margin-top: -0.5rem; margin-bottom: 0.5rem;'>⚡ Response generated in {msg['latency']:.2f}s</p>", unsafe_allow_html=True)
                            if "sources" in msg and msg["sources"]:
                                with st.expander("📖 View Citations"):
                                    for idx, source in enumerate(msg["sources"]):
                                        st.markdown(f"**[Citation {idx+1}]** {source['file']} (Page {source['page']})")
                                        st.markdown(f"*\"{source['snippet']}...\"*")
                                        
        # Chat input for querying
        user_query = st.chat_input("Ask a question about your documents...", key="chat_query_input")
        
        if user_query:
            # Append user message immediately
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # Query chatbot with history
            with st.spinner("🤔 DocSensei is thinking..."):
                with time_it() as timer:
                    res = query_chatbot(
                        question=user_query,
                        vector_store=st.session_state.vector_store,
                        chat_history=st.session_state.messages[:-1]
                    )
                    
                # Format source documents
                sources = []
                for doc in res["source_documents"]:
                    sources.append({
                        "file": os.path.basename(doc.metadata.get("source", "unknown")),
                        "page": doc.metadata.get("page", "unknown"),
                        "snippet": doc.page_content[:180].strip()
                    })
                    
                # Append assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": res["answer"],
                    "latency": timer.elapsed,
                    "sources": sources
                })
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Document details card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📖 Quick Instructions")
    st.markdown("""
    1. **Upload Documents**: Drag and drop PDF or DOCX files on the left sidebar.
    2. **Wait for Processing**: DocSensei will parse the text, split it into chunks, and store embeddings locally using FAISS.
    3. **Start Chatting**: Ask questions in natural language and receive context-rich answers with source page citations.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
