import streamlit as st
import os
from utils.loader import load_document
from utils.helpers import get_document_metrics, time_it

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
    
    /* Card design with glassmorphism */
    .card {
        background: rgba(30, 41, 59, 0.4);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.1);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 1rem 0;'><h2 style='color:#a78bfa; font-weight:700;'>🎓 DocSensei</h2><p style='color:#64748b; font-size:0.9rem;'>AI PDF & DOCX QA System</p></div>", unsafe_allow_html=True)
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
    * **Day 3: Text Chunking** <span class='status-badge status-pending'>In Progress</span>
    * **Day 4: Embeddings & Vector Store** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 5: Gemini LLM Integration** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 6: Chat History Interface** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 7: Document Summarization** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 8: Styling & Custom CSS** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 9: End-to-End Verification** <span class='status-badge status-upcoming'>Upcoming</span>
    * **Day 10: Final Prep, Report & PPT** <span class='status-badge status-upcoming'>Upcoming</span>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #475569; font-size:0.8rem;'>DocSensei v1.0.0 &copy; 2026</div>", unsafe_allow_html=True)


# --- MAIN AREA DESIGN ---
st.markdown("""
<div class="header-container">
    <div class="main-title">DocSensei</div>
    <div class="subtitle">Interact with your PDFs & Word documents using the power of local Embeddings & Google Gemini</div>
</div>
""", unsafe_allow_html=True)

# Layout: Upload on the left, instructions/chat on the right
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📤 Document Upload")
    st.write("Upload your documents to build the knowledge database.")
    
    # File uploader widget accepting PDF and DOCX files
    uploaded_files = st.file_uploader(
        "Choose PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="doc_uploader"
    )
    
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}

    if uploaded_files:
        # Identify removed files
        current_uploaded_names = [f.name for f in uploaded_files]
        for name in list(st.session_state.processed_files.keys()):
            if name not in current_uploaded_names:
                del st.session_state.processed_files[name]
                
        # Identify files that need to be processed
        new_files_to_process = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
        
        if new_files_to_process:
            os.makedirs("uploads", exist_ok=True)
            with st.spinner("🔍 Extracting text from documents..."):
                for f in new_files_to_process:
                    file_path = os.path.join("uploads", f.name)
                    try:
                        # Write file content
                        with open(file_path, "wb") as temp_file:
                            temp_file.write(f.getbuffer())
                        # Load and extract text
                        with time_it() as timer:
                            docs = load_document(file_path)
                        st.session_state.processed_files[f.name] = {
                            "docs": docs,
                            "time_taken": timer.elapsed,
                            "size": f.size
                        }
                    except Exception as e:
                        st.error(f"❌ Error processing {f.name}: {str(e)}")

        # Collect all successfully loaded documents
        all_documents = []
        for name, data in st.session_state.processed_files.items():
            all_documents.extend(data["docs"])
            
        if all_documents:
            st.success(f"📁 {len(uploaded_files)} file(s) loaded and processed successfully!")
        else:
            st.warning("⚠️ No documents could be successfully processed.")
    else:
        if not st.session_state.processed_files:
            st.warning("⚠️ No documents uploaded yet. Please upload files to get started.")
        else:
            st.success(f"📁 {len(st.session_state.processed_files)} file(s) loaded successfully!")

    # Developer Quick-Load / Reset buttons at the bottom of the Upload card
    if os.path.exists("test_files"):
        test_files = [f for f in os.listdir("test_files") if f.endswith((".pdf", ".docx"))]
        if test_files:
            st.markdown("---")
            st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;'>💡 Developer Quick-Load</p>", unsafe_allow_html=True)
            col_dev1, col_dev2 = st.columns(2)
            with col_dev1:
                if st.button("📁 Load Test Files", use_container_width=True):
                    for fname in test_files:
                        file_path = os.path.join("test_files", fname)
                        if fname not in st.session_state.processed_files:
                            try:
                                with time_it() as timer:
                                    docs = load_document(file_path)
                                # Copy to uploads directory to mimic standard upload behavior
                                os.makedirs("uploads", exist_ok=True)
                                dest_path = os.path.join("uploads", fname)
                                import shutil
                                shutil.copy2(file_path, dest_path)
                                
                                st.session_state.processed_files[fname] = {
                                    "docs": docs,
                                    "time_taken": timer.elapsed,
                                    "size": os.path.getsize(file_path)
                                }
                            except Exception as e:
                                st.error(f"❌ Error loading test file {fname}: {str(e)}")
                    st.rerun()
            with col_dev2:
                if st.button("🗑️ Clear Cache", use_container_width=True):
                    st.session_state.processed_files.clear()
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show stats and previewer as separate cards outside the Upload card but within col1
    if st.session_state.processed_files:
        # Collect all loaded docs
        all_documents = []
        for name, data in st.session_state.processed_files.items():
            all_documents.extend(data["docs"])
            
        if all_documents:
            # Metrics Card
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📊 Extraction Metrics")
            metrics = get_document_metrics(all_documents)
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
                    <div class="stat-number">{metrics['total_chars']:,}</div>
                    <div class="stat-label">Characters</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # File list detail
            for name, data in st.session_state.processed_files.items():
                st.markdown(f"<div style='margin-bottom: 0.5rem;'><span style='color: #a78bfa; font-weight: 500;'>📄 {name}</span> <span style='color: #64748b; font-size: 0.85rem;'>({data['size'] / 1024:.1f} KB) &bull; Extracted in {data['time_taken']:.2f}s</span></div>", unsafe_allow_html=True)
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


with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💬 Interactive Assistant")
    
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
        st.write("Ask a question about your uploaded document(s):")
        user_query = st.text_input("Ask a question...", placeholder="e.g. What is the main thesis of this document?", disabled=True)
        st.button("Send Query", disabled=True)
        st.info("💡 Note: Question answering will be fully functional on Day 5 after integrating Google Gemini!")
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
