import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- 1. CLEAN FRONTEND SETUP ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    /* Pure clean background */
    .stApp { background-color: #ffffff; }
    
    .main-header { font-size: 38px !important; font-weight: 800; color: #004D40; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 15px; color: #666; text-align: center; margin-bottom: 25px; }
    
    /* Input Area - Transparent & Minimal */
    .stTextArea textarea {
        border: 1px solid #006644 !important;
        border-radius: 10px !important;
        background-color: #fcfcfc !important;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: #006644;
        color: white;
        font-weight: 700;
        border: none;
    }

    /* Notes Box - This only appears AFTER generation */
    .final-notes-card {
        border-left: 5px solid #006644;
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 0px 10px 10px 0px;
        margin-top: 20px;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
    }
    
    /* Hiding Streamlit default elements that look like white blocks */
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---
def find_active_model():
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
st.markdown('<div class="main-header">🎓 PakAcademia AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Intelligent Study Partner</div>', unsafe_allow_html=True)

# Transparent Input Section
user_topic = st.text_area("What is your topic today?", height=100, placeholder="Type here...")
c1, c2 = st.columns(2)
with c1: lang = st.selectbox("Language", ["English", "Roman Urdu (Hinglish)", "Urdu (اردو)"])
with c2: length = st.selectbox("Depth", ["Short", "Medium", "Long"])
generate_btn = st.button("✨ Start Generating Notes")

# --- 4. STREAMING ENGINE ---
if generate_btn:
    if user_topic:
        st.write("---")
        # Absolutely NO container or status box here
        notes_placeholder = st.empty() # Totally empty start
        full_text = ""
        
        try:
            # Multi-Key Check
            keys = list(st.secrets["GEMINI_API_KEYS"])
            random.shuffle(keys)
            genai.configure(api_key=keys[0].strip())
            
            model_name = find_active_model()
            model = genai.GenerativeModel(model_name)
            
            prompt = f"Provide university level notes on: {user_topic}. Language: {lang}. Length: {length}. Use headings and bullet points."
            
            # Start Streaming
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                full_text += chunk.text
                # Display plain text during stream (No boxes)
                notes_placeholder.write(full_text)
            
            # When finished, wrap in the final styling
            notes_placeholder.markdown(f'<div class="final-notes-card">{full_text}</div>', unsafe_allow_html=True)
            st.session_state['saved_notes'] = full_text
            st.toast("Notes Completed! 🇵🇰")

        except Exception as e:
            if "429" in str(e): st.warning("Servers are busy. Retrying in 10s...")
            else: st.error(f"Error: {e}")
    else:
        st.error("Please enter a topic first.")

# --- 5. EXPORT OPTIONS ---
if 'saved_notes' in st.session_state:
    st.write("###")
    tab_view, tab_pdf = st.tabs(["📄 Read Mode", "📥 Export PDF"])
    with tab_view:
        st.markdown(st.session_state['saved_notes'])
    with tab_pdf:
        try:
            pdf_data = create_pdf(st.session_state['saved_notes'])
            st.download_button("📥 Download Official PDF", data=bytes(pdf_data), file_name="PakAcademia_AI.pdf")
        except:
            st.info("PDF support for Urdu Script is coming soon. Please copy text directly.")

st.markdown("<div style='text-align:center; margin-top:50px; color:#aaa; font-size:11px;'>Muneeb Haider | PakAcademia AI v2.6</div>", unsafe_allow_html=True)
