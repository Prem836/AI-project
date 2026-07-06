import streamlit as st
import os

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
    
    # Progress status indicators
    st.markdown("""
    * **Day 1: Base UI Setup** <span class='status-badge status-completed'>Completed</span>
    * **Day 2: Doc Loading & Text Extraction** <span class='status-badge status-pending'>In Progress</span>
    * **Day 3: Text Chunking** <span class='status-badge status-upcoming'>Upcoming</span>
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
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Display uploaded file names and sizes
        for f in uploaded_files:
            file_details = {"FileName": f.name, "FileType": f.type, "FileSize": f.size}
            st.code(f"📄 Name: {f.name}\n⚖️ Size: {f.size / 1024:.2f} KB")
            
        st.info("ℹ️ Next step: Processing text extraction (Day 2 task!)")
    else:
        st.warning("⚠️ No documents uploaded yet. Please upload files to get started.")
        
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("💬 Interactive Assistant")
    
    # Placeholder layout for Day 1
    if not uploaded_files:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
            <p style="font-size: 4rem; margin-bottom: 1rem;">📚</p>
            <h3>Knowledge Database Empty</h3>
            <p>Upload documents in the left panel to allow the assistant to read and answer questions from them.</p>
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
