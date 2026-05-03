
import os
import subprocess
import sys
import asyncio

# --- STEP 1: PLAYWRIGHT INSTALLATION (Streamlit Cloud ke liye zaroori hai) ---
def install_playwright():
    try:
        # Check if playwright is already installed
        import playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    
    # Browser install karne ke liye command
    subprocess.run(["playwright", "install", "chromium"])
    # System dependencies install karne ke liye (Linux servers par)
    subprocess.run(["playwright", "install-deps"])

# App start hote hi installation check karein
if "playwright_installed" not in os.environ:
    install_playwright()
    os.environ["playwright_installed"] = "true"

import streamlit as st
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv

load_dotenv()

# --- UI Setup ---
st.set_page_config(page_title="AI Browser Agent", page_icon="🤖")

st.title("🤖 Vision Web AI Agent")
st.markdown("Yeh agent aapke liye browser control karega. Aap command dein, baki kaam AI karega.")

# Sidebar for Settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"], index=0)
    st.info("Note: Task ki video recording automatically generate hogi.")

# User Command Input
user_task = st.text_area("Aap kya karwana chahte hain?", placeholder="e.g. Open YouTube and search for Coke Studio Pakistani songs.")

# --- STEP 2: AGENT LOGIC ---
async def run_agent(task, api_key, model):
    # LLM Setup
    llm = ChatOpenAI(model=model, api_key=api_key)
    
    # Browser Config: Streamlit Cloud par 'headless=True' hona chahiye
    # Hum video save karne ke liye folder path bhi de rahe hain
    browser = Browser(
        config=BrowserConfig(
            headless=True,  # Cloud compatibility
        )
    )
    
    # Agent Initialization
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        generate_gif=False, # Hum video use karenge
    )

    # Run Agent
    result = await agent.run()
    
    # Recording ka path (browser-use automatically videos/ folder mein save karta hai)
    # Humein latest video dhoondni hogi
    return result

# --- STEP 3: BUTTON & EXECUTION ---
if st.button("Run Agent 🚀"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar!")
    elif not user_task:
        st.warning("Please enter a command for the agent.")
    else:
        try:
            with st.status("AI Agent kaam kar raha hai... Ismein 1-2 minute lag sakte hain.", expanded=True) as status:
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_result = loop.run_until_complete(run_agent(user_task, api_key, model_name))
                
                status.update(label="✅ Task Mukammal!", state="complete")
                
                st.success("Agent ne apna kaam khatam kar liya hai!")
                st.write("### Result Summary:")
                st.write(final_result)
                
                # Agar koi video save hui hai to usay dikhayein
                video_folder = "./videos" # Default folder for browser-use recordings
                if os.path.exists(video_folder):
                    files = os.listdir(video_folder)
                    if files:
                        latest_video = max([os.path.join(video_folder, f) for f in files], key=os.path.getctime)
                        st.write("### Execution Recording:")
                        st.video(latest_video)

        except Exception as e:
            st.error(f"Ek error aaya hai: {str(e)}")

st.divider()
st.caption("Hackathon Project | Powered by browser-use & OpenAI")
