import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- PROFESSIONAL UI & THEME ---
st.set_page_config(page_title="PakAcademia AI | Custom Notes Maker", page_icon="🇵🇰", layout="centered")

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

# --- BACKEND LOGIC ---
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in available_models: return 'gemini-1.5-flash'
        return 'gemini-pro'
    except: return "gemini-pro"

def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text_content.replace('**', '').replace('#', '').replace('*', '-')
    # Unicode cleaning (Note: Urdu Script PDF requires special fonts, this works best for English/Roman Urdu)
    final_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=final_text)
    return pdf.output()

# --- MAIN INTERFACE ---
st.markdown("<h1>🇵🇰 PakAcademia AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tailor-made Notes for Pakistani University Students</p>", unsafe_allow_html=True)
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # --- STEP 1: TOPIC INPUT ---
    st.subheader("Step 1: Apka Sawal ya Topic")
    user_topic = st.text_area("Yahan apna question ya topic likhen:", placeholder="e.g. Newton's Laws of Motion, 1973 Constitution, or Data Structures...")

    # --- STEP 2: LANGUAGE & LENGTH ---
    st.subheader("Step 2: Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        lang_choice = st.selectbox("Language (Zuban) select karen:", 
                                  ["English Only", "Roman Urdu (Hinglish)", "Urdu Script (اردو)"])
    
    with col2:
        length_choice = st.selectbox("Notes ki length kitni ho?", 
                                    ["Short (1 Page summary)", "Medium (2-3 Pages detailed)", "Comprehensive (Long/Detailed)"])

    # --- GENERATION ---
    if st.button("✨ TAYYAR KAREN (GENERATE NOTES)"):
        if user_topic:
            with st.spinner(f'🧠 {lang_choice} mein notes banaye ja rahe hain...'):
                try:
                    model = genai.GenerativeModel(get_best_model())
                    
                    # Customizing the Prompt based on user choice
                    length_instruction = {
                        "Short (1 Page summary)": "Keep it concise, bullet points, around 300-400 words.",
                        "Medium (2-3 Pages detailed)": "Detailed explanation, sub-headings, around 800-1000 words.",
                        "Comprehensive (Long/Detailed)": "Very in-depth explanation, examples, case studies, 1500+ words."
                    }
                    
                    lang_instruction = {
                        "English Only": "Write everything in formal academic English.",
                        "Roman Urdu (Hinglish)": "Write in Roman Urdu (Urdu words in English alphabets) so it's easy to read.",
                        "Urdu Script (اردو)": "Write everything in proper Urdu script (Nastaliq style content)."
                    }

                    prompt = f"""
                    Role: You are PakAcademia AI, a senior university professor.
                    Topic: {user_topic}
                    Language Requirement: {lang_instruction[lang_choice]}
                    Length Requirement: {length_instruction[length_choice]}
                    
                    Structure:
                    1. Main Heading
                    2. Introduction/Concept
                    3. Detailed Key Points
                    4. Summary/Conclusion
                    5. 3 Important Exam Questions
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state['custom_notes'] = response.text
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Pehle apna topic to likhen!")

    # --- DISPLAY & DOWNLOAD ---
    if 'custom_notes' in st.session_state:
        st.markdown("---")
        st.subheader("📝 Aapke Notes")
        st.markdown(st.session_state['custom_notes'])
        
        # PDF Option (Note: Standard FPDF has limits with Urdu Script, works best for English/Roman)
        pdf_output = create_pdf(st.session_state['custom_notes'])
        st.download_button(
            label="📥 Download as PDF",
            data=bytes(pdf_output),
            file_name="PakAcademia_Notes.pdf",
            mime="application/pdf"
        )
else:
    st.error("API Key Missing! Please add 'GEMINI_API_KEY' in Streamlit Secrets.")

st.markdown("<div class='footer'>PakAcademia AI | Empowering Pakistan's Future 🇵🇰</div>", unsafe_allow_html=True)
