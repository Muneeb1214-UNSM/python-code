import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="UniNotes AI | Pak Student Assistant", page_icon="🎓", layout="centered")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #006644;
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    h1 {
        color: #006644;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND API SETUP ---
# Streamlit Secrets se key uthayega
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Backend mein API Key nahi mili! Please Streamlit Secrets check karen.")

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text_content.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- UI LAYOUT ---
st.title("🎓 UniNotes AI")
st.markdown("<p style='text-align: center; color: gray;'>Pakistan's Smartest AI Note Maker for University Students</p>", unsafe_allow_html=True)

with st.container():
    st.info("💡 **Tip:** Paste your lecture slides or book paragraphs below to get perfect notes.")
    user_input = st.text_area("", height=200, placeholder="Example: Describe the process of Mitosis or explain the 1973 Constitution of Pakistan...")
    
    col1, col2 = st.columns([1, 1])
    generate_btn = st.button("✨ Generate Professional Notes")

# --- LOGIC ---
if generate_btn:
    if user_input:
        with st.spinner('🧠 AI is processing your request...'):
            try:
                # Behtar Model Selection
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                You are a senior professor. Based on this text: {user_input}
                Please provide:
                1. A 'Roman Urdu' (Hinglish) explanation as a 'Concept Clearer' for a student.
                2. Professional 'Academic Notes' in pure English with headings.
                3. 3 Exam-style Short Questions with answers.
                4. A 'Key Takeaway' summary.
                """
                
                response = model.generate_content(prompt)
                st.session_state['notes'] = response.text
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter some text or topic first!")

# --- DISPLAY & DOWNLOAD ---
if 'notes' in st.session_state:
    tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download"])
    
    with tab1:
        st.markdown(st.session_state['notes'])
    
    with tab2:
        st.write("Click below to download your notes in PDF format.")
        pdf_bytes = create_pdf(st.session_state['notes'])
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name="UniNotes_AI_Export.pdf",
            mime="application/pdf"
        )

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>Made with ❤️ for Pakistani Students</p>", unsafe_allow_html=True)
