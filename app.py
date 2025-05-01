import streamlit as st
import os
from dotenv import load_dotenv

# Import modules
from modules.claude_api import ClaudeAPI
from modules.debate_engine import DebateEngine
from ui.components import render_debate, render_controls
from config.settings import DEBATE_TOPICS

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Claude vs Claude Debate",
    page_icon="🤖",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'debate_engine' not in st.session_state:
        # Initialize Claude API
        api = ClaudeAPI()
        
        # Initialize debate engine
        st.session_state.debate_engine = DebateEngine(api)
    
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = []
    
    if 'debate_active' not in st.session_state:
        st.session_state.debate_active = False
    
    if 'human_vote' not in st.session_state:
        st.session_state.human_vote = None

def main():
    st.title("Claude vs Claude Debate System")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for debate configuration
    with st.sidebar:
        st.header("Debate Configuration")
        
        # Topic selection
        selected_topic = st.selectbox(
            "Select a debate topic:",
            options=list(DEBATE_TOPICS.keys())
        )
        
        # Custom topic
        custom_topic = st.text_area(
            "Or enter a custom topic:",
            placeholder="Should cats be allowed to vote?"
        )
        
        # Start debate button
        if st.button("Start New Debate"):
            topic = custom_topic if custom_topic else DEBATE_TOPICS[selected_topic]
            st.session_state.debate_engine.start_debate(topic)
            st.session_state.debate_active = True
            st.session_state.debate_history = []
            st.session_state.human_vote = None
            st.rerun()
    
    # Main content area - debate display
    if st.session_state.debate_active:
        render_debate(st.session_state.debate_history)
        render_controls()
    else:
        st.info("Select a topic and click 'Start New Debate' to begin.")
        
        # About section
        st.markdown("---")
        st.subheader("About this app")
        st.markdown("""
        This app demonstrates a debate between two instances of Claude AI, 
        each arguing for opposite sides of a topic. You can select from 
        predefined topics or create your own custom debate scenario.
        
        At the end of the debate, you'll be able to vote for the winner!
        """)

if __name__ == "__main__":
    main()
