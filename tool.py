import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- DESIGN & UI ---
st.set_page_config(page_title="UniNotes AI | Pak Student Assistant", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #006644;
        color: white;
        font-weight: bold;
    }
    h1 { color: #006644; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def get_best_model():
    """Ye function khud dhondega ke kaunsa model available hai"""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priority wise check: Flash first, then Pro
        if 'models/gemini-1.5-flash' in available_models:
            return 'gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            return 'gemini-pro'
        else:
            # Agar koi aur mil jaye
            return available_models[0].split('/')[-1] if available_models else "gemini-pro"
    except:
        return "gemini-pro" # Safe fallback

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Remove characters that PDF can't handle
    clean_text = text_content.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP ---
st.title("🎓 UniNotes AI")
st.markdown("<p style='text-align: center;'>Get Professional University Notes in Seconds</p>", unsafe_allow_html=True)

# Secrets se key lena
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    user_input = st.text_area("Yahan apna topic ya lecture paste karen:", height=200)
    
    if st.button("✨ Generate Professional Notes"):
        if user_input:
            with st.spinner('🧠 AI Notes bana raha hai...'):
                try:
                    # Auto detect model
                    model_name = get_best_model()
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    You are a university professor. Task: Create notes for a student.
                    Text: {user_input}
                    
                    Structure:
                    1. CONCEPT CLEARER (Easy Roman Urdu/Hinglish): Explain like a friend.
                    2. FORMAL NOTES (Pure English): High-quality academic bullet points for exams.
                    3. KEY TERMS (English): Define 3 main words.
                    4. EXAM QUESTIONS (English): 3 likely questions.
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['notes'] = response.text
                    st.session_state['model_used'] = model_name
                except Exception as e:
                    st.error(f"Generation Error: {e}")
        else:
            st.warning("Kuch to likhen!")

    # Display & Download
    if 'notes' in st.session_state:
        st.success(f"Notes Generated using {st.session_state['model_used']}!")
        tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
        
        with tab1:
            st.markdown(st.session_state['notes'])
        
        with tab2:
            pdf_bytes = create_pdf(st.session_state['notes'])
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="UniNotes_AI.pdf",
                mime="application/pdf"
            )
else:
    st.error("API Key Missing! Streamlit Settings -> Secrets mein 'GEMINI_API_KEY' add karen.")

st.markdown("---")
st.caption("Made for Pakistani University Students 🇵🇰")
