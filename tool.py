import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- PROFESSIONAL UI & PAKISTANI THEME ---
st.set_page_config(page_title="PakAcademia AI | Pakistan's Smartest Study Tool", page_icon="🇵🇰", layout="centered")

# Custom Styling (Professional Green & Minimalist White)
st.markdown("""
    <style>
    .main { background-color: #f8fbf9; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #006644; /* Pakistani Dark Green */
        color: white;
        font-weight: 700;
        font-size: 1.1em;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #004d33;
        transform: translateY(-2px);
    }
    h1 { color: #006644; font-family: 'Helvetica', sans-serif; text-align: center; font-weight: 800; }
    .stTextArea>div>div>textarea { border: 1px solid #006644; border-radius: 12px; padding: 15px; }
    .footer { text-align: center; color: #666; font-size: 0.9em; margin-top: 60px; padding: 20px; border-top: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in available_models: return 'gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models: return 'gemini-pro'
        return available_models[0].split('/')[-1] if available_models else "gemini-pro"
    except: return "gemini-pro"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Cleaning Markdown for PDF
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN INTERFACE ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: 500; color: #444;'>Empowering the Students of Pakistan with Intelligent Synthesis</p>", unsafe_allow_html=True)
st.markdown("---")

# Backend API Key Check
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Input Section
    st.subheader("Analyze Materials")
    user_input = st.text_area("Yahan apna topic, lecture notes, ya paragraph paste karen:", height=250, 
                             placeholder="Example: Explain the concepts of Macroeconomics or summary of 1947 Independence Act...")
    
    if st.button("✨ GENERATE PROFESSIONAL NOTES"):
        if user_input:
            with st.spinner('⏳ PakAcademia AI is synthesizing your notes...'):
                try:
                    model = genai.GenerativeModel(get_best_model())
                    prompt = f"""
                    You are 'PakAcademia AI', an advanced educational assistant for university students in Pakistan.
                    Analyze this text: {user_input}
                    
                    Please provide:
                    1. CONCEPT CLEARER (Roman Urdu): Explain the topic in simple, friendly Roman Urdu (Hinglish) as a mentor.
                    2. ACADEMIC SUMMARY (English): Detailed, bulleted professional notes for exam preparation.
                    3. KEY TERMINOLOGY (English): Define 3-5 critical academic terms.
                    4. PREDICTED EXAM QUESTIONS (English): 3-5 high-probability university exam questions.
                    """
                    response = model.generate_content(prompt)
                    st.session_state['notes'] = response.text
                except Exception as e:
                    st.error(f"System Alert: {e}")
        else:
            st.warning("Please provide input text to generate notes.")

    # Output Display
    if 'notes' in st.session_state:
        st.markdown("### Analysis Result")
        tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
        
        with tab1:
            st.markdown(st.session_state['notes'])
        
        with tab2:
            try:
                pdf_output = create_pdf(st.session_state['notes'])
                st.download_button(
                    label="📄 Download Official PDF Document",
                    data=bytes(pdf_output),
                    file_name="PakAcademia_AI_Notes.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Export Error: {e}")
else:
    st.error("Configuration Error: GEMINI_API_KEY not found in backend secrets.")

# Footer
st.markdown("<div class='footer'>PakAcademia AI v1.0 | Supporting the Future Leaders of Pakistan 🇵🇰</div>", unsafe_allow_html=True)
