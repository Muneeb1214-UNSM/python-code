import os
import subprocess
import sys
import asyncio

# --- STEP 1: PLAYWRIGHT INSTALLATION ---
def install_playwright():
    try:
        import playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    
    # Chromium aur uski dependencies install karne ka sabse sahi tareeka
    try:
        # Install chromium
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        # Install system dependencies (Linux ke liye)
        subprocess.run([sys.executable, "-m", "playwright", "install-deps"], check=True)
    except Exception as e:
        print(f"Playwright installation warning: {e}")

# App start hote hi ek baar installation run karein
if "playwright_installed" not in st.session_state:
    with st.spinner("Setting up browser environment... Please wait."):
        install_playwright()
        st.session_state.playwright_installed = True

import streamlit as st
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv

load_dotenv()

# --- UI Setup ---
st.set_page_config(page_title="AI Browser Agent", page_icon="🤖")
st.title("🤖 Vision Web AI Agent")

# Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"], index=0)

user_task = st.text_area("Aap kya karwana chahte hain?", placeholder="e.g. Open YouTube and search for Coke Studio.")

# --- STEP 2: AGENT LOGIC ---
async def run_agent(task, api_key, model):
    llm = ChatOpenAI(model=model, api_key=api_key)
    
    # Browser ko 'headless' mode mein chalana cloud ke liye lazmi hai
    browser = Browser(
        config=BrowserConfig(headless=True)
    )
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser
    )

    result = await agent.run()
    return result

# --- STEP 3: RUN ---
if st.button("Run Agent 🚀"):
    if not api_key:
        st.error("Sidebar mein OpenAI API Key dalein!")
    elif not user_task:
        st.warning("Command to likhein!")
    else:
        try:
            with st.status("AI Agent kaam kar raha hai...", expanded=True) as status:
                # Video recording directory create karna
                if not os.path.exists("./videos"):
                    os.makedirs("./videos")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_result = loop.run_until_complete(run_agent(user_task, api_key, model_name))
                
                status.update(label="✅ Task Complete!", state="complete")
                st.success("Agent ne kaam khatam kar liya!")
                st.write(final_result)

                # Video check
                if os.path.exists("./videos"):
                    videos = [f for f in os.listdir("./videos") if f.endswith(".mp4")]
                    if videos:
                        latest_video = os.path.join("./videos", videos[-1])
                        st.video(latest_video)

        except Exception as e:
            st.error(f"Error: {str(e)}")
