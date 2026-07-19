import streamlit as st
import fitz  # PyMuPDF
import os
import io
import hashlib
import json
from datetime import datetime

# ─── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Premium Look ────────────────────────────────
st.markdown("""
<style>
    /* Global */
    .stApp { background: linear-gradient(135deg, #0E1117 0%, #1A1F2E 100%); }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #4F8BF9 0%, #764BA2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(79,139,249,0.25);
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p { color: rgba(255,255,255,0.85); margin: 0.5rem 0 0; }
    
    /* Cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-card h3 { color: #4F8BF9; font-size: 2rem; margin: 0; }
    .metric-card p { color: rgba(255,255,255,0.7); margin: 0.25rem 0 0; font-size: 0.85rem; }
    
    /* Chat Bubbles */
    .user-msg {
        background: linear-gradient(135deg, #4F8BF9, #764BA2);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .ai-msg {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        color: #FAFAFA;
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    /* Disclaimer */
    .disclaimer {
        background: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #FFC107;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
        margin-bottom: 1rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141824 0%, #0E1117 100%);
    }
    
    /* Upload area */
    .upload-zone {
        border: 2px dashed rgba(79,139,249,0.4);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: rgba(79,139,249,0.05);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_reports" not in st.session_state:
    st.session_state.uploaded_reports = []
if "extracted_texts" not in st.session_state:
    st.session_state.extracted_texts = []
if "rag_initialized" not in st.session_state:
    st.session_state.rag_initialized = False
if "users_db" not in st.session_state:
    st.session_state.users_db = {}  # Simple in-memory user store


# ─── Helper Functions ────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text.strip()

def get_ai_response(query: str, context: str, history: list) -> str:
    """Get AI response using OpenAI API with RAG context."""
    try:
        from openai import OpenAI
        
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY", "")
            except Exception:
                pass
        
        if not api_key:
            return "⚠️ **OpenAI API Key not configured.** Please add your `OPENAI_API_KEY` in the Streamlit Cloud Secrets settings (Settings → Secrets) to enable AI responses."
        
        client = OpenAI(api_key=api_key)
        
        system_prompt = f"""You are an AI Medical Assistant designed to help users understand their health information.
You MUST clearly state that you are for Educational Purposes Only and are not a substitute for professional medical advice.

Use the following retrieved context from the user's uploaded medical reports to answer their query. 
If the answer is not in the context, clearly state that you do not have enough specific medical information and advise consulting a doctor.

Retrieved Medical Report Context:
{context if context else "No medical reports uploaded yet. Answer based on general medical knowledge with appropriate disclaimers."}"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in history[-6:]:  # Last 6 messages for context window
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": query})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error communicating with AI: {str(e)}"


def generate_pdf_report(email: str, chat_history: list, reports: list) -> bytes:
    """Generate a downloadable PDF health summary."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(f"Health Summary Report for {email}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "DISCLAIMER: This report is for educational purposes only and is not professional medical advice.",
        styles['Italic']
    ))
    story.append(Spacer(1, 24))
    
    # Reports section
    story.append(Paragraph("Uploaded Medical Reports", styles['Heading2']))
    if not reports:
        story.append(Paragraph("No reports uploaded.", styles['Normal']))
    for r in reports:
        story.append(Paragraph(f"• {r['filename']} (Uploaded: {r['uploaded_at']})", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Chat summary
    story.append(Paragraph("Recent AI Interactions", styles['Heading2']))
    if not chat_history:
        story.append(Paragraph("No interactions found.", styles['Normal']))
    for msg in chat_history[-10:]:
        role = "Q" if msg["role"] == "user" else "A"
        content = msg["content"][:300]
        story.append(Paragraph(f"<b>{role}:</b> {content}", styles['Normal']))
        story.append(Spacer(1, 4))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ─── AUTH PAGES ──────────────────────────────────────────────────
def show_auth_page():
    """Display Login / Register page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0 2rem;">
            <h1 style="font-size: 3rem; margin: 0;">🏥</h1>
            <h2 style="background: linear-gradient(135deg, #4F8BF9, #764BA2); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-size: 2rem; margin: 0.5rem 0;">AI Medical Assistant</h2>
            <p style="color: rgba(255,255,255,0.6);">Your intelligent health companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
                if submit:
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    elif email in st.session_state.users_db:
                        if st.session_state.users_db[email] == hash_password(password):
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.rerun()
                        else:
                            st.error("❌ Incorrect password.")
                    else:
                        st.error("❌ User not found. Please register first.")
        
        with tab2:
            with st.form("register_form"):
                reg_email = st.text_input("Email Address", placeholder="you@example.com", key="reg_email")
                reg_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
                register = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if register:
                    if not reg_email or not reg_password:
                        st.error("Please fill in all fields.")
                    elif reg_password != reg_confirm:
                        st.error("❌ Passwords do not match.")
                    elif reg_email in st.session_state.users_db:
                        st.error("❌ This email is already registered.")
                    else:
                        st.session_state.users_db[reg_email] = hash_password(reg_password)
                        st.success("✅ Account created successfully! Please sign in.")
        
        st.markdown("""
        <div class="disclaimer">
            ⚠️ <b>Educational Project</b> — This application is for learning purposes only. 
            It does not provide real medical advice.
        </div>
        """, unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0;">🏥</h2>
            <h3 style="background: linear-gradient(135deg, #4F8BF9, #764BA2);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       margin: 0.25rem 0;">AI Medical Assistant</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📤 Upload Reports", "💬 AI Chat", "📥 Download Report"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # User info
        st.markdown(f"**Logged in as:** {st.session_state.user_email}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.chat_history = []
            st.session_state.uploaded_reports = []
            st.session_state.extracted_texts = []
            st.session_state.rag_initialized = False
            st.rerun()
        
        st.divider()
        st.caption("v1.0.0 • Educational Use Only")
        
    return page


# ─── DASHBOARD PAGE ─────────────────────────────────────────────
def show_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Overview of your medical data and AI interactions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(st.session_state.uploaded_reports)}</h3>
            <p>📄 Reports Uploaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        user_msgs = len([m for m in st.session_state.chat_history if m["role"] == "user"])
        st.markdown(f"""
        <div class="metric-card">
            <h3>{user_msgs}</h3>
            <p>💬 Questions Asked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_pages = sum(r.get("pages", 0) for r in st.session_state.uploaded_reports)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_pages}</h3>
            <p>📃 Pages Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_chars = sum(len(t) for t in st.session_state.extracted_texts)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_chars:,}</h3>
            <p>🔤 Characters Extracted</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Activity
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📄 Recent Reports")
        if not st.session_state.uploaded_reports:
            st.info("No reports uploaded yet. Go to **Upload Reports** to get started!")
        else:
            for report in st.session_state.uploaded_reports[-5:]:
                with st.container(border=True):
                    st.markdown(f"**{report['filename']}**")
                    st.caption(f"Pages: {report['pages']} • Uploaded: {report['uploaded_at']}")
    
    with col_right:
        st.subheader("💬 Recent Conversations")
        if not st.session_state.chat_history:
            st.info("No conversations yet. Go to **AI Chat** to ask questions!")
        else:
            for msg in st.session_state.chat_history[-6:]:
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                with st.container(border=True):
                    st.markdown(f"{role_icon} **{msg['role'].capitalize()}**")
                    st.caption(msg["content"][:150] + "..." if len(msg["content"]) > 150 else msg["content"])


# ─── UPLOAD PAGE ─────────────────────────────────────────────────
def show_upload():
    st.markdown("""
    <div class="main-header">
        <h1>📤 Upload Medical Reports</h1>
        <p>Upload PDF reports to extract text and feed the AI knowledge base</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer">
        ⚠️ Your files are processed in-memory and are <b>never stored on any server</b>. 
        All data is cleared when your session ends.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload PDF Medical Reports",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files for text extraction."
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Skip if already processed
            existing_names = [r["filename"] for r in st.session_state.uploaded_reports]
            if uploaded_file.name in existing_names:
                st.warning(f"⚠️ `{uploaded_file.name}` already uploaded. Skipping.")
                continue
            
            with st.spinner(f"🔍 Processing `{uploaded_file.name}`..."):
                file_bytes = uploaded_file.read()
                extracted_text = extract_text_from_pdf(file_bytes)
                
                # Count pages
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                page_count = len(doc)
                doc.close()
                
                if extracted_text:
                    st.session_state.extracted_texts.append(extracted_text)
                    st.session_state.uploaded_reports.append({
                        "filename": uploaded_file.name,
                        "pages": page_count,
                        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "char_count": len(extracted_text),
                    })
                    
                    st.success(f"✅ **{uploaded_file.name}** — {page_count} pages, {len(extracted_text):,} characters extracted.")
                    
                    with st.expander(f"📖 Preview extracted text from `{uploaded_file.name}`"):
                        st.text(extracted_text[:2000] + ("..." if len(extracted_text) > 2000 else ""))
                else:
                    st.error(f"❌ Could not extract text from `{uploaded_file.name}`. It may be a scanned image PDF.")
    
    # Show previously uploaded reports
    if st.session_state.uploaded_reports:
        st.divider()
        st.subheader("📚 Uploaded Reports Library")
        for i, report in enumerate(st.session_state.uploaded_reports):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{report['filename']}**")
            with col2:
                st.caption(f"{report['pages']} pages")
            with col3:
                st.caption(report['uploaded_at'])


# ─── CHAT PAGE ───────────────────────────────────────────────────
def show_chat():
    st.markdown("""
    <div class="main-header">
        <h1>💬 AI Medical Chat</h1>
        <p>Ask questions about your health reports — powered by GPT-4</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer">
        ⚠️ <b>For Educational Purposes Only.</b> This AI is not a substitute for professional medical advice, 
        diagnosis, or treatment. Always consult a qualified healthcare provider.
    </div>
    """, unsafe_allow_html=True)
    
    # Build context from all extracted texts
    context = "\n\n---\n\n".join(st.session_state.extracted_texts) if st.session_state.extracted_texts else ""
    
    if not st.session_state.extracted_texts:
        st.info("💡 **Tip:** Upload medical reports first to get AI-powered analysis based on your documents!")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    query = st.chat_input("Ask about your medical reports...")
    
    if query:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query})
        st.markdown(f'<div class="user-msg">{query}</div>', unsafe_allow_html=True)
        
        # Get AI response
        with st.spinner("🧠 AI is thinking..."):
            response = get_ai_response(query, context, st.session_state.chat_history)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.markdown(f'<div class="ai-msg">{response}</div>', unsafe_allow_html=True)
        st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


# ─── DOWNLOAD PAGE ──────────────────────────────────────────────
def show_download():
    st.markdown("""
    <div class="main-header">
        <h1>📥 Download Health Summary</h1>
        <p>Generate and download a comprehensive PDF report of your AI interactions</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Reports Uploaded", len(st.session_state.uploaded_reports))
    with col2:
        st.metric("Chat Messages", len(st.session_state.chat_history))
    
    st.divider()
    
    if not st.session_state.chat_history and not st.session_state.uploaded_reports:
        st.warning("📭 No data available yet. Upload reports and chat with the AI first!")
    else:
        st.info("Click below to generate a PDF health summary containing your uploaded reports and recent AI conversations.")
        
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating your health summary PDF..."):
                pdf_bytes = generate_pdf_report(
                    st.session_state.user_email,
                    st.session_state.chat_history,
                    st.session_state.uploaded_reports,
                )
            
            st.success("✅ Report generated successfully!")
            st.download_button(
                label="⬇️ Download Health Summary PDF",
                data=pdf_bytes,
                file_name=f"health_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ─── MAIN APP ROUTER ────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        page = show_sidebar()
        
        if page == "📊 Dashboard":
            show_dashboard()
        elif page == "📤 Upload Reports":
            show_upload()
        elif page == "💬 AI Chat":
            show_chat()
        elif page == "📥 Download Report":
            show_download()


if __name__ == "__main__":
    main()
