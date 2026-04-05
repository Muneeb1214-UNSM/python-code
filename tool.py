import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import random

# --- UI SETUP ---
st.set_page_config(page_title="PakAcademia AI", page_icon="🇵🇰", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #006644; color: white; font-weight: 700; }
    h1 { color: #006644; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SMART GENERATION LOGIC (MULTI-KEY) ---
def generate_content_with_retry(prompt):
    """Sari keys bari bari check karta hai jab tak result na mil jaye"""
    if "GEMINI_API_KEYS" not in st.secrets:
        return None, "Secrets mein keys missing hain!"
    
    keys = list(st.secrets["GEMINI_API_KEYS"])
    random.shuffle(keys) # Keys ko mix karna taake load divide ho
    
    for key in keys:
        try:
            genai.configure(api_key=key.strip())
            # Hum sirf 'gemini-1.5-flash' use karenge kyunke iska quota sab se zyada hai
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Success"
        except Exception as e:
            if "429" in str(e):
                continue # Agli key check karo
            else:
                return None, str(e)
    
    return None, "QUOTA_FULL"

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
st.markdown("<p style='text-align: center;'>Smart Academic Assistant for Students</p>", unsafe_allow_html=True)

user_topic = st.text_area("Enter Topic or Question:", height=150)
col1, col2 = st.columns(2)
with col1: lang = st.selectbox("Language:", ["English", "Roman Urdu", "Urdu"])
with col2: length = st.selectbox("Length:", ["Short", "Medium", "Long"])

if st.button("🚀 GENERATE NOTES"):
    if user_topic:
        with st.spinner('Checking Servers & Generating Notes...'):
            prompt = f"Topic: {user_topic}, Language: {lang}, Length: {length}. Provide professional university notes with headings and 3 exam questions."
            
            notes, status = generate_content_with_retry(prompt)
            
            if notes:
                st.session_state['notes'] = notes
                st.success("Notes Generated Successfully!")
            elif status == "QUOTA_FULL":
                st.error("⚠️ **Limit Exhausted:** Sabhi API keys ka quota khatam ho gaya hai. Please 1 minute baad try karen ya developer ko batayen ke mazeed keys add kare.")
            else:
                st.error(f"Error: {status}")
    else:
        st.warning("Please enter a topic!")

if 'notes' in st.session_state:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
    with tab1: st.markdown(st.session_state['notes'])
    with tab2:
        pdf_bytes = create_pdf(st.session_state['notes'])
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name="PakAcademia_Notes.pdf")

st.markdown("<div style='text-align:center; padding-top:50px;'>PakAcademia AI | 🇵🇰 Pakistan's Future Leaders</div>", unsafe_allow_html=True)
