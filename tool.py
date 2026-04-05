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
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #006644; text-align: center; font-weight: 800; }
    .stTextArea>div>div>textarea { border: 1px solid #006644; border-radius: 10px; }
    .footer { text-align: center; color: #666; font-size: 0.9em; margin-top: 50px; padding: 20px; border-top: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATION LOGIC ---
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Cleaning Markdown symbols for PDF compatibility
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN INTERFACE ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Custom Notes Generator for Pakistani University Students</p>", unsafe_allow_html=True)
st.markdown("---")

# Secrets check
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')

        # USER INPUTS
        st.subheader("📝 Setup Your Notes")
        user_topic = st.text_area("Enter your question or topic:", height=150, placeholder="e.g. Write a detailed note on the 1973 Constitution of Pakistan...")
        
        col1, col2 = st.columns(2)
        with col1:
            lang_choice = st.selectbox("Preferred Language:", ["English Only", "Roman Urdu (Hinglish)", "Urdu Script (اردو)"])
        with col2:
            length_choice = st.selectbox("Notes Length:", ["Short (Summary)", "Medium (Detailed)", "Long (Comprehensive)"])

        if st.button("🚀 GENERATE PROFESSIONAL NOTES"):
            if user_topic:
                with st.spinner('🧠 PakAcademia AI is synthesizing your notes...'):
                    try:
                        # Professional Prompt Building
                        prompt = f"""
                        You are PakAcademia AI, a senior university professor.
                        Task: Create high-quality academic notes for a student.
                        Topic: {user_topic}
                        Language Choice: {lang_choice}
                        Length Choice: {length_choice}
                        
                        Instructions:
                        1. If language is Roman Urdu, explain the concept like a friendly mentor.
                        2. If English, use formal academic vocabulary.
                        3. Structure the notes with:
                           - Clear Headings
                           - Detailed bullet points
                           - 3 Important Exam-style Questions at the end.
                        """
                        
                        response = model.generate_content(prompt)
                        st.session_state['notes_result'] = response.text
                        st.success("Success! Notes generated.")
                    except Exception as e:
                        if "429" in str(e):
                            st.error("⚠️ **Quota Full:** Google ki free limit khatam ho gayi hai. Please 1 minute baad try karen.")
                        else:
                            st.error(f"Error: {e}")
            else:
                st.warning("Pehle koi topic to likhen!")

        # DISPLAY & DOWNLOAD
        if 'notes_result' in st.session_state:
            st.markdown("---")
            tab1, tab2 = st.tabs(["📄 View Notes", "📥 Download PDF"])
            
            with tab1:
                st.markdown(st.session_state['notes_result'])
            
            with tab2:
                try:
                    pdf_data = create_pdf(st.session_state['notes_result'])
                    st.download_button(
                        label="📥 Download PDF Document",
                        data=bytes(pdf_data),
                        file_name="PakAcademia_Notes.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF Error: {e}")
                    
    except Exception as e:
        st.error(f"Configuration Error: {e}")
else:
    st.error("API Key Missing! Please add 'GEMINI_API_KEY' in Streamlit Secrets.")

# Footer
st.markdown("<div class='footer'>PakAcademia AI | Made with ❤️ for the Students of Pakistan 🇵🇰</div>", unsafe_allow_html=True)
