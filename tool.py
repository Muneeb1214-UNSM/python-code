import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AI Notes Maker", page_icon="🎓")

st.title("🎓 Pak-Student AI Notes Maker")
st.write("Apne concepts asaan Urdu/English mein samjhein.")

# Sidebar
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Try to find the best available model
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Test if model exists
            test_response = model.generate_content("test")
        except:
            model = genai.GenerativeModel('gemini-pro')

        # User Input
        user_input = st.text_area("Yahan topic paste karen:", height=200)

        if st.button("Generate Notes"):
            if user_input:
                with st.spinner('AI Notes bana raha hai, sabar karen...'):
                    prompt = f"""
                    You are a helpful tutor for Pakistani university students.
                    Topic/Text: {user_input}
                    
                    Please provide:
                    1. Summary in 5 simple bullet points.
                    2. Explanation in 'Roman Urdu' (Mix of Urdu and English) so it sounds like a teacher explaining to a student.
                    3. 3 potential exam questions.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("### Aapke Notes:")
                    st.write(response.text)
            else:
                st.warning("Pehle kuch likh to dein!")

    except Exception as e:
        st.error(f"Ek masla aa gaya hai: {e}")
        st.info("Mashwara: Check karen ke aapki API Key sahi hai ya nahi.")
else:
    st.info("Side bar mein API Key enter karen.")
