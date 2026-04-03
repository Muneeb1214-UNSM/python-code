import streamlit as st
import google.generativeai as genai

# Page Setup
st.set_page_config(page_title="Pakistani Student AI Notes Maker", page_icon="🎓")
st.title("🎓 Pak-Student AI Notes Maker")
st.write("Apne mushkil topics ko asaan Roman Urdu aur English mein convert karen.")

# Sidebar for API Key
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Yahan hum model ka naya naam use kar rahe hain
        model = genai.GenerativeModel('gemini-1.5-flash') 

        # Input Box
        user_input = st.text_area("Yahan apna topic ya paragraph paste karen:", placeholder="Example: Newton's second law of motion...")

        if st.button("Generate Notes"):
            if user_input:
                with st.spinner('AI soch raha hai...'):
                    prompt = f"""
                    You are an expert academic tutor for Pakistani university students. 
                    The user has provided this text: {user_input}
                    
                    Please provide:
                    1. Short Summary (Simple English).
                    2. Detailed Explanation in 'Roman Urdu' (Hinglish) so a desi student can easily understand.
                    3. 3-5 Important Exam Questions from this topic.
                    4. Use bullet points and headings.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.success("Tayyar hain aapke notes!")
                    st.markdown("---")
                    st.markdown(response.text)
            else:
                st.warning("Please enter some text first!")
                
    except Exception as e:
        st.error(f"Ek masla aa gaya hai: {e}")
else:
    st.info("Side bar mein apni Gemini API Key enter karen. (Ye key aap aistudio.google.com se le sakte hain)")

# Footer
st.markdown("---")
st.caption("Made for Pakistani Students 🇵🇰")
    
