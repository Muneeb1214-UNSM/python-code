import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import time

# --- DESIGN ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🇵🇰")

# --- API SETUP (Cached) ---
# Is se har baar list_models call nahi hoga, quota bachega
@st.cache_resource
def setup_genai(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN APP ---
st.title("🇵🇰 PakAcademia AI")

if "GEMINI_API_KEY" in st.secrets:
    model = setup_genai(st.secrets["GEMINI_API_KEY"])
    
    user_topic = st.text_area("Apna topic enter karen:")
    col1, col2 = st.columns(2)
    with col1: lang = st.selectbox("Zuban:", ["English", "Roman Urdu", "Urdu"])
    with col2: length = st.selectbox("Length:", ["Short", "Medium", "Long"])

    if st.button("🚀 GENERATE NOTES"):
        if user_topic:
            try:
                with st.spinner('Synthesizing...'):
                    prompt = f"Topic: {user_topic}, Language: {lang}, Length: {length}. Give professional notes."
                    response = model.generate_content(prompt)
                    st.session_state['notes'] = response.text
            
            # YAHAN ERROR HANDLE HOGA
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ **Server Busy hai!** Bohat saare students ek saath use kar rahe hain. Please 30-60 seconds baad dubara button dabayein.")
                else:
                    st.error(f"Kuch masla aa gaya hai: {e}")
        else:
            st.warning("Pehle kuch likhen!")

    if 'notes' in st.session_state:
        st.markdown(st.session_state['notes'])
        pdf_out = create_pdf(st.session_state['notes'])
        st.download_button("📥 Download PDF", data=bytes(pdf_out), file_name="Notes.pdf")

else:
    st.error("API Key missing!")
