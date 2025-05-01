import streamlit as st
from typing import List, Dict

def render_debate(debate_history: List[Dict[str, str]]):
    """
    Render the debate history in the Streamlit interface.
    
    Args:
        debate_history: List of debate messages
    """
    if not debate_history:
        st.info("The debate will appear here once started.")
        return
    
    # Create columns for the two debaters
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pro / Yes Position")
    
    with col2:
        st.subheader("Con / No Position")
    
    # Display debate messages
    for i, message in enumerate(debate_history):
        if message.get("perspective") == "pro":
            with col1:
                st.markdown(f"**Round {message.get('round', i//2 + 1)}**")
                st.markdown(message["content"])
                st.markdown("---")
        else:
            with col2:
                st.markdown(f"**Round {message.get('round', i//2 + 1)}**")
                st.markdown(message["content"])
                st.markdown("---")

def render_controls():
    """Render debate control buttons and voting interface."""
    # Check if debate is complete
    debate_engine = st.session_state.debate_engine
    debate_complete = debate_engine.is_debate_complete()
    
    st.markdown("---")
    
    # Controls based on debate state
    if not debate_complete:
        # Next round button
        if st.button("Continue Debate", key="continue_debate"):
            # Get next round of responses
            pro_response, con_response = debate_engine.generate_next_round()
            
            # Add to debate history
            current_round = len(st.session_state.debate_history) // 2 + 1
            
            st.session_state.debate_history.append({
                "round": current_round,
                "perspective": "pro",
                "content": pro_response,
                "is_assistant": True
            })
            
            st.session_state.debate_history.append({
                "round": current_round,
                "perspective": "con",
                "content": con_response,
                "is_assistant": True
            })
            
            st.rerun()
    else:
        # Debate is complete, show voting interface
        st.header("Vote for the winner")
        
        # Check if user has already voted
        if st.session_state.human_vote is None:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Vote for Pro/Yes"):
                    st.session_state.human_vote = "pro"
                    st.rerun()
            
            with col2:
                if st.button("Vote for Con/No"):
                    st.session_state.human_vote = "con"
                    st.rerun()
        else:
            # Show the voting result
            st.success(f"You voted for the {st.session_state.human_vote.upper()} position!")
            
            # Option to start a new debate
            if st.button("Start New Debate"):
                st.session_state.debate_active = False
                st.session_state.debate_history = []
                st.session_state.human_vote = None
                st.rerun()
    
    # Reset debate button
    st.button("Reset Debate", on_click=reset_debate)

def reset_debate():
    """Reset the debate state."""
    st.session_state.debate_active = False
    st.session_state.debate_history = []
    st.session_state.human_vote = None