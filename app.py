import streamlit as st
import os
from dotenv import load_dotenv

# Import modules
from modules.claude_api import ClaudeAPI
from modules.debate_engine import DebateEngine
from ui.components import render_debate, render_controls, render_loading_animation
from utils.research import format_research_for_display
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
        
    if 'pro_personality' not in st.session_state:
        st.session_state.pro_personality = ""
    
    if 'con_personality' not in st.session_state:
        st.session_state.con_personality = ""
    
    if 'loading' not in st.session_state:
        st.session_state.loading = False

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
        
        # Research settings
        st.subheader("Research Settings")
        
        enable_research = st.checkbox(
            "Enable Perplexity Research",
            value=st.session_state.debate_engine.enable_research if hasattr(st.session_state, "debate_engine") else True,
            help="Use Perplexity Ask MCP to research facts for the debate"
        )
        
        # Update debate engine with research setting if it exists
        if hasattr(st.session_state, "debate_engine"):
            st.session_state.debate_engine.set_research_enabled(enable_research)
        
        # Personality prompts
        st.subheader("Debater Personalities (Optional)")
        
        st.session_state.pro_personality = st.text_area(
            "Pro/Yes Personality:",
            placeholder="e.g., Speak like a passionate advocate",
            value=st.session_state.pro_personality
        )
        
        st.session_state.con_personality = st.text_area(
            "Con/No Personality:",
            placeholder="e.g., Speak like a skeptical critic",
            value=st.session_state.con_personality
        )
        
        # Start debate button
        if st.button("Start New Debate", key="start_new_debate"):
            # Show loading animation
            with st.spinner("Preparing debate plans..."):
                topic = custom_topic if custom_topic else DEBATE_TOPICS[selected_topic]
                
                # Start debate with personalities if provided
                st.session_state.debate_engine.start_debate(
                    topic, 
                    pro_personality=st.session_state.pro_personality,
                    con_personality=st.session_state.con_personality
                )
                
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
        This app demonstrates a structured debate between two instances of Claude AI, 
        each arguing for opposite sides of a topic.
        
        ## How it works:
        
        1. **Preparation Phase**: Both Claude instances create debate plans
        2. **Opening Statements**: Each side presents their main arguments
        3. **First Rebuttal**: Responses to the opening arguments
        4. **Second Rebuttal**: Further defense and counter-arguments
        5. **Closing Statements**: Final summaries of each position
        
        At the end, you'll be able to vote for the side you found most persuasive!
        """)

if __name__ == "__main__":
    main()
