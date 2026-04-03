import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Notes Maker", page_icon="🎓")
st.title("🎓 Pak-Student AI Notes Maker")

# Sidebar
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- YE HISSA MODEL DHONDNE KE LIYE HAI ---
        # Hum check kar rahe hain ke aapke pas kaunse models available hain
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Pehle check karen 1.5-flash, phir 1.5-pro, phir gemini-pro
        selected_model_name = ""
        if 'models/gemini-1.5-flash' in available_models:
            selected_model_name = 'gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            selected_model_name = 'gemini-pro'
        else:
            selected_model_name = available_models[0].replace('models/', '') if available_models else ""

        if selected_model_name:
            model = genai.GenerativeModel(selected_model_name)
            st.sidebar.success(f"Connected to: {selected_model_name}")
            
            user_input = st.text_area("Yahan apna topic paste karen (e.g. Data Structures, Photosynthesis):", height=200)

            if st.button("Notes Banayein"):
                if user_input:
                    with st.spinner('AI Notes bana raha hai...'):
                        prompt = f"""
                        You are a teacher for Pakistani students.
                        Topic: {user_input}
                        
                        1. Explain the main concept in very easy Roman Urdu (Hinglish).
                        2. Give 5 main summary points in English.
                        3. List 3 questions that can come in exams.
                        """
                        response = model.generate_content(prompt)
                        st.markdown("### Aapke Notes:")
                        st.write(response.text)
                else:
                    st.warning("Kuch likhen ge to notes banenge na!")
        else:
            st.error("Aapke account mein koi model nahi mila. API key check karen.")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Mashwara: Google AI Studio mein jayen aur check karen ke API key active hai.")
else:
    st.info("Side bar mein API Key dalen.")
