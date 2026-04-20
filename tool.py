import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- 1. PREMIUM FRONTEND (CSS) ---
st.set_page_config(page_title="PakAcademia AI | Pro Assistant", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    /* Global Styles */
    .main { background-color: #f8f9fa; }
    
    /* Header Styling */
    .main-header {
        font-size: 45px !important;
        font-weight: 800;
        color: #004D40;
        text-align: center;
        margin-bottom: 10px;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-header {
        font-size: 18px;
        color: #555;
        text-align: center;
        margin-bottom: 40px;
    }

    /* Card Styling for Input */
    .input-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(135deg, #006644 0%, #004D40 100%);
        color: white;
        font-weight: 700;
        font-size: 18px;
        border: none;
        transition: 0.3s all;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 68, 0.3);
        color: #f1f1f1;
    }

    /* Note Content Styling */
    .notes-box {
        background-color: #ffffff;
        border-left: 5px solid #006644;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* Customizing Text Area */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid #ddd !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f1f1;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #006644 !important; color: white !important; }

    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND FUNCTIONS ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

def generate_streaming_notes(prompt):
    if "GEMINI_API_KEYS" not in st.secrets:
        return None, "API Keys Missing"
    
    keys = list(st.secrets["GEMINI_API_KEYS"])
    random.shuffle(keys)
    
    for key in keys:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt, stream=True)
            return response, "Success"
        except Exception as e:
            if "429" in str(e): continue
            else: return None, str(e)
    return None, "QUOTA_FULL"

# --- 3. UI LAYOUT ---

st.markdown('<div class="main-header">🎓 PakAcademia AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Pakistan’s most advanced AI-powered academic assistant</div>', unsafe_allow_html=True)

# Input Section in a nice layout
with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    user_topic = st.text_area("What would you like to learn today?", height=150, placeholder="Example: Briefly explain the 1973 Constitution or the laws of Thermodynamics...")
    
    c1, c2 = st.columns(2)
    with c1:
        lang = st.selectbox("Output Language", ["English", "Roman Urdu (Hinglish)", "Urdu (اردو)"])
    with c2:
        length = st.selectbox("Select Depth", ["Short Summary", "Medium Detail", "Comprehensive"])
    
    generate_btn = st.button("✨ Generate Intelligent Notes")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. PROCESSING & OUTPUT ---
if generate_btn:
    if user_topic:
        st.markdown("---")
        notes_placeholder = st.empty()
        full_response = ""
        
        prompt = f"Role: Senior Professor. Topic: {user_topic}. Language: {lang}. Depth: {length}. Instruction: Provide high-quality academic notes with headings and 3 exam questions."
        
        stream, status = generate_streaming_notes(prompt)
        
        if status == "Success":
            with st.status("🧠 Synthesizing Academic Content...", expanded=True) as status_box:
                for chunk in stream:
                    full_response += chunk.text
                    notes_placeholder.markdown(f'<div class="notes-box">{full_response}▌</div>', unsafe_allow_html=True)
                notes_placeholder.markdown(f'<div class="notes-box">{full_response}</div>', unsafe_allow_html=True)
                st.session_state['final_notes'] = full_response
                status_box.update(label="✅ Notes Completed!", state="complete", expanded=False)
        elif status == "QUOTA_FULL":
            st.error("⚠️ All servers are currently busy. Please retry in 60 seconds.")
        else:
            st.error(f"Error: {status}")
    else:
        st.warning("Please enter a topic or question to begin.")

# --- 5. TABS FOR VIEWING & EXPORT ---
if 'final_notes' in st.session_state:
    st.write("###")
    t1, t2 = st.tabs(["📝 Read Notes", "📥 Export & Save"])
    
    with t1:
        st.markdown(st.session_state['final_notes'])
    
    with t2:
        st.info("Download your notes in PDF format for offline study.")
        try:
            pdf_bytes = create_pdf(st.session_state['final_notes'])
            st.download_button(
                label="📥 Download PDF Document",
                data=bytes(pdf_bytes),
                file_name="PakAcademia_Notes.pdf",
                mime="application/pdf"
            )
        except:
            st.error("PDF Export is currently limited for Urdu script. Please copy the text directly.")

# Footer
st.markdown("""
    <div class="footer">
        <br><br>
        <p>Made with ❤️ by <b>Muneeb Haider</b> for Pakistani Students</p>
        <p style="font-size: 12px; color: #999;">PakAcademia AI v2.5 | Powering Education through GenAI</p>
    </div>
    """, unsafe_allow_html=True)
