import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- 1. PREMIUM FRONTEND (CSS) ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-header { font-size: 42px !important; font-weight: 800; color: #004D40; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 16px; color: #666; text-align: center; margin-bottom: 30px; }
    
    /* Input Section Styling */
    .input-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #eee;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    /* Professional Button */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(135deg, #006644 0%, #004D40 100%);
        color: white;
        font-weight: 700;
        border: none;
    }
    
    /* Result Box - Only shows when notes are ready */
    .final-notes {
        background-color: #ffffff;
        border-left: 5px solid #006644;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---
def find_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
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
st.markdown('<div class="sub-header">Advanced Academic Assistant for Pakistani Students</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_topic = st.text_area("What is your topic today?", height=120, placeholder="e.g. Explain the importance of the 1940 Resolution...")
    
    c1, c2 = st.columns(2)
    with c1: lang = st.selectbox("Language", ["English", "Roman Urdu (Hinglish)", "Urdu (اردو)"])
    with c2: length = st.selectbox("Notes Length", ["Short", "Medium", "Long"])
    
    generate_btn = st.button("✨ Generate Notes")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. STREAMING & DISPLAY ---
if generate_btn:
    if user_topic:
        st.write("---")
        # Khali placeholder - Is mein koi dabba nahi hai abhi
        notes_placeholder = st.empty()
        full_response = ""
        
        try:
            # Keys Rotation
            keys = list(st.secrets["GEMINI_API_KEYS"])
            random.shuffle(keys)
            genai.configure(api_key=keys[0].strip())
            
            model_path = find_best_model()
            model = genai.GenerativeModel(model_path)
            
            prompt = f"Role: University Professor. Topic: {user_topic}. Language: {lang}. Depth: {length}. Instruction: Provide high-quality academic notes with headings and questions."
            
            # Streaming Start
            response = model.generate_content(prompt, stream=True)
            
            # Words display ho rahe hain baghair kisi "white box" ke
            for chunk in response:
                full_response += chunk.text
                notes_placeholder.markdown(full_response + "▌")
            
            # Jab poora ho jaye, tab khubsurat box mein dalo
            notes_placeholder.markdown(f'<div class="final-notes">{full_response}</div>', unsafe_allow_html=True)
            st.session_state['final_notes'] = full_response
            st.balloons() # Success animation

        except Exception as e:
            if "429" in str(e): st.error("Server busy! Please try again in a few seconds.")
            else: st.error(f"Error: {e}")
    else:
        st.warning("Please enter a topic.")

# --- 5. TABS & EXPORT ---
if 'final_notes' in st.session_state:
    st.write("###")
    t1, t2 = st.tabs(["📝 View Full Notes", "📥 Download PDF"])
    with t1: st.markdown(st.session_state['final_notes'])
    with t2:
        try:
            pdf_bytes = create_pdf(st.session_state['final_notes'])
            st.download_button("📥 Download Official PDF", data=bytes(pdf_bytes), file_name="PakAcademia_Notes.pdf")
        except: st.error("PDF download issues? Copy the text directly.")

st.markdown("<div style='text-align:center; padding:40px; color:#888; font-size:12px;'>PakAcademia AI | 🇵🇰 Pakistan</div>", unsafe_allow_html=True)
