import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- 1. FULL DARK MODE PREMIUM UI ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 45px !important;
        font-weight: 800;
        background: linear-gradient(90deg, #00C853, #B2FF59);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 16px;
        color: #888;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Professional Dark Input Card */
    .stTextArea textarea {
        background-color: #1a1c23 !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
    }
    
    /* Neon Green Button - Professional & Glowing */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(135deg, #00C853 0%, #00897B 100%);
        color: white;
        font-weight: 700;
        font-size: 18px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.2);
        transition: 0.3s all ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 200, 83, 0.4);
        color: #ffffff;
    }

    /* Final Notes Box - Professional Neon Border */
    .final-notes-card {
        background-color: #161b22;
        border-left: 4px solid #00C853;
        padding: 25px;
        border-radius: 10px;
        margin-top: 25px;
        line-height: 1.7;
        color: #e6edf3;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* Tabs Styling for Dark Mode */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #1a1c23;
        border-radius: 8px;
        color: #888;
        padding: 5px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00C853 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---
def find_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if preferred in available_models: return preferred
        return available_models[0]
    except: return "models/gemini-pro"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- 3. UI LAYOUT ---
st.markdown('<div class="main-header">🖋️ PakAcademia AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Premium Academic Assistant for Pakistani Students</div>', unsafe_allow_html=True)

# Main Input Section
with st.container():
    user_topic = st.text_area("What topic should I summarize for you?", height=130, placeholder="Describe the topic or paste lecture points here...")
    
    col1, col2 = st.columns(2)
    with col1:
        lang = st.selectbox("Output Language", ["English", "Roman Urdu (Hinglish)", "Urdu (اردو)"])
    with col2:
        length = st.selectbox("Note Depth", ["Short", "Medium", "Long"])
    
    generate_btn = st.button("✨ Generate Professional Notes")

# --- 4. STREAMING ENGINE ---
if generate_btn:
    if user_topic:
        st.write("---")
        # Empty space for clean streaming - No boxes here
        notes_placeholder = st.empty()
        full_text = ""
        
        try:
            # Multi-Key Rotation
            keys = list(st.secrets["GEMINI_API_KEYS"])
            random.shuffle(keys)
            genai.configure(api_key=keys[0].strip())
            
            model_path = find_best_model()
            model = genai.GenerativeModel(model_path)
            
            prompt = f"As a Senior Professor, provide high-quality university notes on: {user_topic}. Language: {lang}. Depth: {length}. Use clear headings and 3 exam questions."
            
            # Start Streaming
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                full_text += chunk.text
                # Streaming plain text for ChatGPT feel
                notes_placeholder.write(full_text)
            
            # Final Styling Applied after streaming
            notes_placeholder.markdown(f'<div class="final-notes-card">{full_text}</div>', unsafe_allow_html=True)
            st.session_state['saved_notes'] = full_text
            st.toast("Notes Synthesis Complete!", icon="✅")

        except Exception as e:
            if "429" in str(e): st.error("⚠️ All API Keys busy. Please wait 60 seconds.")
            else: st.error(f"Error: {e}")
    else:
        st.warning("Please enter a topic first.")

# --- 5. TABS & EXPORT ---
if 'saved_notes' in st.session_state:
    st.write("###")
    t1, t2 = st.tabs(["📝 Full View", "📥 Download PDF"])
    with t1:
        st.markdown(st.session_state['saved_notes'])
    with t2:
        try:
            pdf_data = create_pdf(st.session_state['saved_notes'])
            st.download_button("📥 Download Official PDF", data=bytes(pdf_data), file_name="PakAcademia_Notes.pdf")
        except:
            st.info("Note: PDF export is currently optimized for English/Roman Urdu text.")

# Footer
st.markdown(f"<div style='text-align:center; margin-top:60px; color:#444; font-size:12px;'>Muneeb Haider | PakAcademia AI v2.7 🇵🇰</div>", unsafe_allow_html=True)
