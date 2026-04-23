import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- 1. PREMIUM FRONTEND (CSS) ---
st.set_page_config(page_title="PakAcademia AI | Pro Assistant", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-header { font-size: 45px !important; font-weight: 800; color: #004D40; text-align: center; margin-bottom: 10px; }
    .sub-header { font-size: 18px; color: #555; text-align: center; margin-bottom: 40px; }
    .input-card { background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eee; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background: linear-gradient(135deg, #006644 0%, #004D40 100%); color: white; font-weight: 700; font-size: 18px; border: none; }
    .notes-box { background-color: #ffffff; border-left: 5px solid #006644; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); font-size: 16px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---

def find_best_model():
    """Ye function khud dhoondega ke kaunsa model available hai taake 404 na aaye"""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priority wise selection
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if preferred in available_models:
                return preferred
        return available_models[0] if available_models else "models/gemini-pro"
    except:
        return "models/gemini-pro" # Fallback

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
        return None, "API Keys Missing", None
    
    keys = list(st.secrets["GEMINI_API_KEYS"])
    random.shuffle(keys)
    
    for key in keys:
        try:
            genai.configure(api_key=key.strip())
            # Find the best model dynamically
            model_path = find_best_model()
            model = genai.GenerativeModel(model_path)
            response = model.generate_content(prompt, stream=True)
            return response, "Success", model_path
        except Exception as e:
            if "429" in str(e): continue
            else: return None, str(e), None
    return None, "QUOTA_FULL", None

# --- 3. UI LAYOUT ---
st.markdown('<div class="main-header">🎓 PakAcademia AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced AI-powered academic assistant for Pakistani Students</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    user_topic = st.text_area("What would you like to learn today?", height=150, placeholder="Example: Briefly explain the structure of an Atom...")
    
    c1, c2 = st.columns(2)
    with c1: lang = st.selectbox("Language", ["English", "Roman Urdu (Hinglish)", "Urdu (اردو)"])
    with c2: length = st.selectbox("Select Depth", ["Short Summary", "Medium Detail", "Comprehensive"])
    
    generate_btn = st.button("✨ Generate Intelligent Notes")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. PROCESSING ---
if generate_btn:
    if user_topic:
        st.markdown("---")
        notes_placeholder = st.empty()
        full_response = ""
        
        prompt = f"Role: Senior Professor. Topic: {user_topic}. Language: {lang}. Depth: {length}. Provide high-quality academic notes with headings and 3 exam questions."
        
        stream, status, connected_model = generate_streaming_notes(prompt)
        
        if status == "Success":
            st.caption(f"⚡ Connected via {connected_model.split('/')[-1]}")
            for chunk in stream:
                full_response += chunk.text
                notes_placeholder.markdown(f'<div class="notes-box">{full_response}▌</div>', unsafe_allow_html=True)
            notes_placeholder.markdown(f'<div class="notes-box">{full_response}</div>', unsafe_allow_html=True)
            st.session_state['final_notes'] = full_response
        elif status == "QUOTA_FULL":
            st.error("⚠️ All keys busy. Retry in 60s.")
        else:
            st.error(f"Error: {status}")
    else:
        st.warning("Please enter a topic.")

# --- 5. EXPORT ---
if 'final_notes' in st.session_state:
    st.write("###")
    t1, t2 = st.tabs(["📝 Read Notes", "📥 Export & Save"])
    with t1: st.markdown(st.session_state['final_notes'])
    with t2:
        try:
            pdf_bytes = create_pdf(st.session_state['final_notes'])
            st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name="PakAcademia_Notes.pdf")
        except:
            st.error("PDF Export limited for special characters. Please copy text.")

st.markdown("<div style='text-align:center; padding:30px; color:gray;'>PakAcademia AI | 🇵🇰 Pakistan</div>", unsafe_allow_html=True)
