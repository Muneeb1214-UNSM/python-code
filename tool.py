import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- PROFESSIONAL UI SETUP ---
st.set_page_config(page_title="PakAcademia AI | Smart Notes", page_icon="🇵🇰", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #006644; color: white; font-weight: 700;
    }
    h1 { color: #006644; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND MODEL LOGIC ---
def get_working_model():
    """Ye function khud dhoondega ke kaunsa model available hai"""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority wise check: 1.5-flash, 1.5-pro, phir purana gemini-pro
        if any('gemini-1.5-flash' in m for m in available_models):
            return 'gemini-1.5-flash'
        elif any('gemini-1.5-pro' in m for m in available_models):
            return 'gemini-1.5-pro'
        elif any('gemini-pro' in m for m in available_models):
            return 'gemini-pro'
        else:
            # Agar koi aur mil jaye
            return available_models[0].replace('models/', '') if available_models else "gemini-pro"
    except Exception as e:
        # Fallback to a safe default
        return "gemini-pro"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN APP ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Smart Academic Assistant for Pakistani Students</p>", unsafe_allow_html=True)
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # MODEL AUTO-DETECT
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        
        st.subheader("📝 Customize Your Notes")
        user_topic = st.text_area("Enter your question or topic:", placeholder="e.g. Discuss the 18th Amendment...")
        
        col1, col2 = st.columns(2)
        with col1:
            lang_choice = st.selectbox("Preferred Language:", ["English", "Roman Urdu", "Urdu"])
        with col2:
            length_choice = st.selectbox("Length:", ["Short", "Medium", "Long"])

        if st.button("🚀 GENERATE PROFESSIONAL NOTES"):
            if user_topic:
                with st.spinner(f'🧠 Using {model_name} to generate notes...'):
                    try:
                        prompt = f"""
                        You are PakAcademia AI, a professor.
                        Topic: {user_topic}
                        Language: {lang_choice}
                        Length: {length_choice}
                        
                        Structure: Heading, Concept Overview, Detailed Notes, and 3 Exam Questions.
                        """
                        response = model.generate_content(prompt)
                        st.session_state['notes'] = response.text
                        st.success(f"Generated successfully!")
                    except Exception as e:
                        st.error(f"Generation Error: {e}")
            else:
                st.warning("Pehle kuch likhen!")

        if 'notes' in st.session_state:
            st.markdown("---")
            tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
            with tab1:
                st.markdown(st.session_state['notes'])
            with tab2:
                pdf_data = create_pdf(st.session_state['notes'])
                st.download_button("📥 Download PDF", data=bytes(pdf_data), file_name="PakAcademia_Notes.pdf")

    except Exception as e:
        st.error(f"Configuration Error: {e}")
else:
    st.error("API Key Missing!")

st.markdown("<div style='text-align:center; padding:20px;'>PakAcademia AI | 🇵🇰 Pakistan</div>", unsafe_allow_html=True)
