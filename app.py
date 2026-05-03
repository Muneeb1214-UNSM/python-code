import os
import subprocess
import sys
import asyncio
import streamlit as st  # Pehle import karna zaroori hai

# --- STEP 1: PLAYWRIGHT INSTALLATION ---
def install_playwright():
    try:
        import playwright
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    
    try:
        # Chromium install karein
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        # Linux dependencies install karein
        subprocess.run([sys.executable, "-m", "playwright", "install-deps"], check=True)
    except Exception as e:
        print(f"Playwright installation warning: {e}")

# Streamlit session state check
if "playwright_installed" not in st.session_state:
    with st.spinner("Setting up browser environment... Please wait."):
        install_playwright()
        st.session_state.playwright_installed = True

from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv

load_dotenv()

# --- UI Setup ---
st.set_page_config(page_title="AI Browser Agent", page_icon="🤖")
st.title("🤖 Vision Web AI Agent")

# Sidebar for Settings
with st.sidebar:
    st.header("Settings")
    # API Key input
    api_key = st.text_input("Enter OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"], index=0)
    st.info("Note: Task complete hone par video niche nazar aayegi.")

# User Command Input
user_task = st.text_area("Aap kya karwana chahte hain?", placeholder="e.g. Go to Wikipedia and search for Space X.")

# --- STEP 2: AGENT LOGIC ---
async def run_agent(task, api_key, model):
    # LLM Setup
    llm = ChatOpenAI(model=model, api_key=api_key)
    
    # Browser configuration (Cloud ke liye headless zaroori hai)
    browser = Browser(
        config=BrowserConfig(headless=True)
    )
    
    # Agent setup
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser
    )

    # Run and get result
    result = await agent.run()
    return result

# --- STEP 3: RUN ---
if st.button("Run Agent 🚀"):
    if not api_key:
        st.error("Sidebar mein OpenAI API Key dalein!")
    elif not user_task:
        st.warning("Kuch likhein to sahi!")
    else:
        try:
            with st.status("AI Agent kaam kar raha hai (Video record ho rahi hai)...", expanded=True) as status:
                # Video folder ensure karein
                if not os.path.exists("./videos"):
                    os.makedirs("./videos")
                
                # Async event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_result = loop.run_until_complete(run_agent(user_task, api_key, model_name))
                
                status.update(label="✅ Task Complete!", state="complete")
                st.success("Agent ne kaam khatam kar liya!")
                
                # Result display
                st.write("### Result:")
                st.write(final_result)

                # Video display logic
                if os.path.exists("./videos"):
                    video_files = [f for f in os.listdir("./videos") if f.endswith(".mp4")]
                    if video_files:
                        # Latest video dhoondna
                        latest_video = max([os.path.join("./videos", f) for f in video_files], key=os.path.getctime)
                        st.write("### Demo Recording:")
                        st.video(latest_video)

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

st.divider()
st.caption("Hackathon Project | Powered by browser-use")
