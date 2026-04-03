import streamlit as st
import google.generativeai as genai

# Setup
st.set_page_config(page_title="Pakistani Student AI Notes Maker")
st.title("🎓 Pak-Student AI Notes Maker")
st.subheader("Apne topics ko asaan Urdu/English mein samjhein")

# API Key input
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # Input Box
    user_input = st.text_area("Yahan apna topic ya notes paste karen:")

    if st.button("Make Notes"):
        if user_input:
            prompt = f"""
            You are an expert tutor for Pakistani University students. 
            Analyze the following text and:
            1. Summarize it in simple points.
            2. Explain the main concept in easy 'Roman Urdu' (Hinglish).
            3. List 3 important exam questions from this topic.
            
            Text: {user_input}
            """
            response = model.generate_content(prompt)
            st.write("### Aapke Notes:")
            st.write(response.text)
        else:
            st.warning("Kuch to likhen!")
else:
    st.info("Side par API Key dalen shuru karne ke liye.")
