import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- PROFESSIONAL UI ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🇵🇰", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #006644; color: white; font-weight: 700;
    }
    h1 { color: #006644; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC (FIXED) ---
def get_best_model():
    """Ye function list mangwaye ga aur jo model milega wahi use karega"""
    try:
        # Google se available models ki list mangwana
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority wise model select karna
        if 'models/gemini-1.5-flash' in models:
            return 'gemini-1.5-flash'
        elif 'models/gemini-1.5-pro' in models:
            return 'gemini-1.5-pro'
        elif 'models/gemini-pro' in models:
            return 'gemini-pro'
        else:
            # Agar koi aur model mil jaye (e.g. naya version)
            return models[0].replace('models/', '')
    except Exception as e:
        # Agar list bhi na mile to default naya model try karein
        return "gemini-1.5-flash"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Cleaning symbols for PDF
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN APP ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Customized University Notes Generator</p>", unsafe_allow_html=True)
st.markdown("---")

# Secrets check
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # User Inputs
    st.subheader("📝 Customize Your Notes")
    user_topic = st.text_area("Enter your question or topic:", placeholder="e.g. Explain 18th Amendment of Pakistan...")
    
    col1, col2 = st.columns(2)
    with col1:
        lang_choice = st.selectbox("Preferred Language:", ["English", "Roman Urdu (Hinglish)", "Urdu Script (اردو)"])
    with col2:
        length_choice = st.selectbox("Page Length:", ["Short (1 Page)", "Medium (2-3 Pages)", "Comprehensive (Long)"])

    if st.button("🚀 GENERATE NOTES"):
        if user_topic:
            with st.spinner('Checking models and generating notes...'):
                try:
                    # Best model select karna
                    target_model = get_best_model()
                    model = genai.GenerativeModel(target_model)
                    
                    # Custom Prompt logic
                    prompt = f"""
                    You are PakAcademia AI, a senior professor.
                    Topic: {user_topic}
                    Language: {lang_choice}
                    Length: {length_choice}
                    
                    Requirements:
                    1. If language is Roman Urdu, explain like a friendly mentor.
                    2. If English, keep it academic and formal.
                    3. Structure: Heading, Detailed Notes, Key Terms, and 3 Exam Questions.
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['final_notes'] = response.text
                    st.session_state['used_model'] = target_model
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Topic enter karein!")

    # Show Output
    if 'final_notes' in st.session_state:
        st.info(f"Model used: {st.session_state['used_model']}")
        st.markdown("---")
        st.markdown(st.session_state['final_notes'])
        
        pdf_out = create_pdf(st.session_state['final_notes'])
        st.download_button(
            label="📥 Download PDF Document",
            data=bytes(pdf_out),
            file_name="PakAcademia_Notes.pdf",
            mime="application/pdf"
        )
else:
    st.error("API Key missing in Secrets!")

st.markdown("---")
st.caption("PakAcademia AI | 🇵🇰 Pakistan's Future Leaders")
