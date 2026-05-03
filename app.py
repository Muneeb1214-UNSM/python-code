import streamlit as st
import asyncio
import os
from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv

# Load Environment Variables (API Key)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="AI Web Commander", page_icon="🤖", layout="wide")

# Custom CSS for Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .status-box { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar (Configuration) ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    model_choice = st.selectbox("Choose Model", ["gpt-4o", "gpt-4o-mini"])
    st.info("Tip: Demo ke liye 'gpt-4o' behtar hai kyunki ye browsing commands ko ache se samajhta hai.")

# --- Main UI ---
st.title("🌐 AI Browser Commander")
st.subheader("Bataiye mujhe kya karna hai, main browser control karunga!")

# Example Commands
with st.expander("💡 Ideas for commands:"):
    st.write("- Go to YouTube and search for 'Python Tutorial'.")
    st.write("- Open Gmail and check if I have any new emails.")
    st.write("- Go to Amazon, find a gaming mouse under $50 and show me.")
    st.write("- Open Wikipedia and search for 'Artificial Intelligence', then summarize the first paragraph.")

# User Input
user_prompt = st.text_area("Enter your command:", placeholder="e.g., Search for latest AI news on Google and show me the headlines.", height=100)

# Function to run the AI Agent
async def run_browser_agent(prompt, api_key, model):
    if not api_key:
        st.error("❌ Please provide an API Key!")
        return

    # Initialize LLM
    llm = ChatOpenAI(model=model, api_key=api_key)
    
    # Initialize Agent
    # generate_gif=True se aap bad mein video bhi dikha sakte hain (Optional)
    agent = Agent(
        task=prompt,
        llm=llm,
    )

    # Run the agent
    result = await agent.run()
    return result

# --- Execution ---
if st.button("Execute Task 🚀"):
    if user_prompt:
        st.divider()
        with st.status("🤖 Agent is thinking and working...", expanded=True) as status:
            st.write("Initializing Browser...")
            
            # Running the async agent in Streamlit
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_browser_agent(user_prompt, api_key, model_choice))
                
                st.write("Finalizing results...")
                status.update(label="✅ Task Accomplished!", state="complete", expanded=False)
                
                # Success Display
                st.balloons()
                st.success("Task Finished Successfully!")
                st.markdown("### 📝 Agent's Final Report:")
                st.write(result)
                
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter a command first!")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center;'>Built for Hackathon | Powered by browser-use & GPT-4o</p>", unsafe_allow_html=True)
