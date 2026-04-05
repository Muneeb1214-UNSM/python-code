import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- PROFESSIONAL UI SETUP ---
st.set_page_config(page_title="PakAcademia AI | Smart Notes", page_icon="🇵🇰", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #006644; color: white; font-weight: 700;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #006644; text-align: center; font-weight: 800; }
    .footer { text-align: center; color: #666; font-size: 0.9em; margin-top: 50px; padding: 20px; border-top: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATION LOGIC ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MULTI-KEY AI GENERATION LOGIC ---
def generate_notes_with_retry(prompt):
    keys = st.secrets["GEMINI_API_KEYS"]
    # Keys ko random order mein shuffle karna taake load divide ho
    random.shuffle(keys)
    
    last_error = ""
    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Success"
        except Exception as e:
            last_error = str(e)
            if "429" in last_error:
                continue # Doosri key try karo
            else:
                return None, last_error
    
    return None, "QUOTA_EXCEEDED"

# --- MAIN APP INTERFACE ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Advanced Academic Synthesis Tool for Pakistani Students</p>", unsafe_allow_html=True)
st.markdown("---")

if "GEMINI_API_KEYS" in st.secrets:
    # INPUT SECTION
    st.subheader("📝 Customize Your Notes")
    user_topic = st.text_area("Apna Sawal ya Topic enter karen:", height=150, placeholder="e.g. Discuss the role of Allama Iqbal in Pakistan Movement...")
    
    col1, col2 = st.columns(2)
    with col1:
        lang_choice = st.selectbox("Preferred Language:", ["English", "Roman Urdu (Hinglish)", "Urdu Script (اردو)"])
    with col2:
        length_choice = st.selectbox("Note Length:", ["Short (Summary)", "Medium (Detailed)", "Long (Comprehensive)"])

    if st.button("🚀 GENERATE PROFESSIONAL NOTES"):
        if user_topic:
            with st.spinner('🧠 PakAcademia AI is processing (Checking multiple servers)...'):
                
                # Custom prompt building
                prompt = f"""
                You are PakAcademia AI, a senior professor. 
                Task: Create notes for a university student.
                Topic: {user_topic}
                Language: {lang_choice}
                Length: {length_choice}
                
                Structure:
                1. Concept Overview (Easy to understand)
                2. Academic Detailed Notes (Formal)
                3. Key Definitions
                4. 3 Potential Exam Questions
                """
                
                notes, status = generate_notes_with_retry(prompt)
                
                if notes:
                    st.session_state['generated_notes'] = notes
                elif status == "QUOTA_EXCEEDED":
                    st.error("⚠️ **Server Full:** Sabhi keys ka quota khatam ho gaya hai. Please 1 minute baad try karen.")
                else:
                    st.error(f"Error: {status}")
        else:
            st.warning("Pehle koi topic to likhen!")

    # DISPLAY SECTION
    if 'generated_notes' in st.session_state:
        st.markdown("---")
        tab1, tab2 = st.tabs(["📄 View Notes", "📥 Download"])
        
        with tab1:
            st.markdown(st.session_state['generated_notes'])
        
        with tab2:
            pdf_data = create_pdf(st.session_state['generated_notes'])
            st.download_button(
                label="📥 Download as PDF",
                data=bytes(pdf_data),
                file_name="PakAcademia_Notes.pdf",
                mime="application/pdf"
            )
else:
    st.error("Secrets mein GEMINI_API_KEYS (list) add karna lazmi hai!")

st.markdown("<div class='footer'>PakAcademia AI v2.1 | Empowering Future Leaders 🇵🇰</div>", unsafe_allow_html=True)
