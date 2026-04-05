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

# --- BACKEND LOGIC (MULTI-KEY & MODEL CHECK) ---
def generate_content_with_retry(prompt):
    if "GEMINI_API_KEYS" not in st.secrets:
        return None, "Secrets mein keys missing hain!"
    
    keys = list(st.secrets["GEMINI_API_KEYS"])
    random.shuffle(keys) 
    
    errors = []
    for key in keys:
        try:
            # 1. Configure the API Key
            genai.configure(api_key=key.strip())
            
            # 2. Try to find the best model name available on THIS key
            # Google sometimes needs 'models/gemini-1.5-flash' instead of just 'gemini-1.5-flash'
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Priority List
            target_model = None
            if 'models/gemini-1.5-flash' in available_models:
                target_model = 'models/gemini-1.5-flash'
            elif 'models/gemini-1.5-pro' in available_models:
                target_model = 'models/gemini-1.5-pro'
            elif 'models/gemini-pro' in available_models:
                target_model = 'models/gemini-pro'
            else:
                target_model = available_models[0] # Jo bhi mil jaye
            
            # 3. Generate Content
            model = genai.GenerativeModel(target_model)
            response = model.generate_content(prompt)
            return response.text, "Success"
            
        except Exception as e:
            err_msg = str(e)
            errors.append(err_msg)
            # Agar quota (429) ya invalid key (400) hai to agli key try karo
            if "429" in err_msg or "400" in err_msg or "404" in err_msg:
                continue 
            else:
                return None, err_msg
    
    return None, f"All keys failed. Last error: {errors[-1] if errors else 'Unknown'}"

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
        with st.spinner('Checking Servers & Finding Best Model...'):
            prompt = f"Topic: {user_topic}, Language: {lang}, Length: {length}. Provide professional university notes with headings and 3 exam questions."
            
            notes, status = generate_content_with_retry(prompt)
            
            if notes:
                st.session_state['notes'] = notes
                st.success("Notes Generated Successfully!")
            else:
                st.error(f"Error Details: {status}")
                st.info("Mashwara: 1 minute baad dobara try karen ya API Keys check karen.")
    else:
        st.warning("Please enter a topic!")

if 'notes' in st.session_state:
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
    with tab1: st.markdown(st.session_state['notes'])
    with tab2:
        try:
            pdf_bytes = create_pdf(st.session_state['notes'])
            st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name="PakAcademia_Notes.pdf")
        except:
            st.error("PDF generation failed due to special characters.")

st.markdown("<div style='text-align:center; padding-top:50px;'>PakAcademia AI | 🇵🇰 Pakistan</div>", unsafe_allow_html=True)
