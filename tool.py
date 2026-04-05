import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- PROFESSIONAL UI ---
st.set_page_config(page_title="PakAcademia AI | Smart Notes", page_icon="🇵🇰", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #006644; color: white; font-weight: 700; }
    h1 { color: #006644; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SMART MODEL DETECTOR ---
def get_model_safe():
    """Ye function khud dhoondega ke kaunsa model available hai"""
    try:
        # Google se available models ki list mangwana
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Agar koi model mil jaye to priority check karein
        target = None
        for m in available_models:
            if 'gemini-1.5-flash' in m: target = m; break
        if not target:
            for m in available_models:
                if 'gemini-1.5-pro' in m: target = m; break
        if not target:
            for m in available_models:
                if 'gemini-pro' in m: target = m; break
        
        # Agar phir bhi na mile to pehla wala utha lo
        final_model = target if target else available_models[0]
        return final_model
    except Exception as e:
        st.error(f"Models list nahi mil rahi: {e}")
        return None

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
st.markdown("<p style='text-align: center;'>Smart Academic Assistant</p>", unsafe_allow_html=True)
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Step 1: Find Model
        active_model_path = get_model_safe()
        
        if active_model_path:
            st.info(f"Connected to: {active_model_path.replace('models/', '')}")
            model = genai.GenerativeModel(active_model_path)
            
            # Step 2: User Input
            user_topic = st.text_area("Enter Topic or Question:", height=150)
            col1, col2 = st.columns(2)
            with col1: lang = st.selectbox("Language:", ["English", "Roman Urdu", "Urdu"])
            with col2: length = st.selectbox("Length:", ["Short", "Medium", "Long"])

            if st.button("🚀 GENERATE NOTES"):
                if user_topic:
                    with st.spinner('PakAcademia AI is synthesizing...'):
                        try:
                            prompt = f"Topic: {user_topic}, Language: {lang}, Length: {length}. Provide professional university notes with headings and 3 exam questions."
                            response = model.generate_content(prompt)
                            st.session_state['notes_data'] = response.text
                        except Exception as e:
                            st.error(f"Generation Error: {e}")
                else:
                    st.warning("Pehle kuch topic to likhen!")
        else:
            st.error("Aapki API key par koi bhi Gemini model nahi mila. Please check if your API key is active in Google AI Studio.")

        # Step 3: Display & Download
        if 'notes_data' in st.session_state:
            st.markdown("---")
            tab1, tab2 = st.tabs(["📝 View Notes", "📥 Download PDF"])
            with tab1: st.markdown(st.session_state['notes_data'])
            with tab2:
                try:
                    pdf_bytes = create_pdf(st.session_state['notes_data'])
                    st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name="PakAcademia_Notes.pdf")
                except: st.error("PDF generation failed.")

    except Exception as e:
        st.error(f"System Error: {e}")
else:
    st.error("API Key missing in Secrets!")

st.markdown("<div style='text-align:center; padding-top:50px;'>PakAcademia AI v2.5 | 🇵🇰</div>", unsafe_allow_html=True)
