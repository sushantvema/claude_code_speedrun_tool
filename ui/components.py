import streamlit as st
from typing import List, Dict
import time

def render_debate(debate_history: List[Dict[str, str]]):
    """
    Render the debate history in the Streamlit interface.
    
    Args:
        debate_history: List of debate messages
    """
    if not st.session_state.debate_active:
        st.info("The debate will appear here once started.")
        return
    
    debate_engine = st.session_state.debate_engine
    current_stage = debate_engine.get_current_stage()
    
    # Render preparation phase if we're at that stage
    if current_stage == "preparation":
        render_preparation_phase()
        return
    
    # Create columns for the two debaters
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pro / Yes Position")
    
    with col2:
        st.subheader("Con / No Position")
    
    # Group messages by stage
    stages = ["opening", "first_rebuttal", "second_rebuttal", "closing"]
    current_stage_index = stages.index(current_stage) if current_stage in stages else len(stages)
    
    # Only show stages up to the current one
    visible_stages = stages[:current_stage_index]
    if current_stage in stages:
        visible_stages.append(current_stage)
        
    # Display messages stage by stage
    for stage in visible_stages:
        # Get messages for this stage
        stage_messages = [msg for msg in debate_history if msg.get("stage") == stage]
        
        if not stage_messages:
            continue
        
        # Stage header
        st.markdown(f"## {stage.replace('_', ' ').title()} Stage")
        
        pro_message = next((msg for msg in stage_messages if msg.get("perspective") == "pro"), None)
        con_message = next((msg for msg in stage_messages if msg.get("perspective") == "con"), None)
        
        # Display stage content in columns
        stage_col1, stage_col2 = st.columns(2)
        
        with stage_col1:
            if pro_message:
                st.markdown(pro_message["content"])
        
        with stage_col2:
            if con_message:
                st.markdown(con_message["content"])
                
        st.markdown("---")

def render_preparation_phase():
    """Render the preparation phase UI."""
    debate_engine = st.session_state.debate_engine
    
    st.header("Debate Preparation Phase")
    st.markdown("""
    Before the debate begins, both sides have prepared their debate plans. 
    Review these plans and decide if you want to proceed with the debate.
    """)
    
    # Display pro plan
    st.subheader("Pro/Yes Plan")
    st.markdown(debate_engine.pro_plan)
    
    # Display con plan
    st.subheader("Con/No Plan")
    st.markdown(debate_engine.con_plan)
    
    # Button to approve plans and start debate
    if st.button("Approve Plans and Start Debate", key="approve_plans"):
        with st.spinner("Generating opening statements..."):
            debate_engine.approve_plans_and_continue()
            next_content = debate_engine.generate_next_debate_content()
            st.session_state.debate_history = []
            
            # Add opening statements to debate history
            if "pro" in next_content and "con" in next_content:
                st.session_state.debate_history.append({
                    "perspective": "pro",
                    "content": next_content["pro"],
                    "stage": "opening",
                    "is_assistant": True
                })
                
                st.session_state.debate_history.append({
                    "perspective": "con", 
                    "content": next_content["con"],
                    "stage": "opening",
                    "is_assistant": True
                })
        
        st.rerun()

def render_controls():
    """Render debate control buttons and voting interface."""
    # Check debate state
    debate_engine = st.session_state.debate_engine
    current_stage = debate_engine.get_current_stage()
    debate_complete = debate_engine.is_debate_complete()
    
    st.markdown("---")
    
    # Controls based on debate state
    if current_stage == "preparation":
        # Preparation phase controls are in render_preparation_phase
        pass
        
    elif not debate_complete:
        # Next stage button - use a unique key for each stage
        stage_button_key = f"continue_debate_{current_stage}"
        if st.button("Continue to Next Stage", key=stage_button_key):
            with st.spinner("Generating next debate stage..."):
                next_content = debate_engine.generate_next_debate_content()
                
                # Add new content to debate history
                if "pro" in next_content and "con" in next_content:
                    st.session_state.debate_history.append({
                        "perspective": "pro",
                        "content": next_content["pro"],
                        "stage": next_content["stage"],
                        "is_assistant": True
                    })
                    
                    st.session_state.debate_history.append({
                        "perspective": "con", 
                        "content": next_content["con"],
                        "stage": next_content["stage"],
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
                if st.button("Vote for Pro/Yes", key="vote_pro"):
                    st.session_state.human_vote = "pro"
                    st.rerun()
            
            with col2:
                if st.button("Vote for Con/No", key="vote_con"):
                    st.session_state.human_vote = "con"
                    st.rerun()
        else:
            # Show the voting result
            st.success(f"You voted for the {st.session_state.human_vote.upper()} position!")
            
            # Option to start a new debate
            if st.button("Start New Debate", key="new_debate_after_vote"):
                st.session_state.debate_active = False
                st.session_state.debate_history = []
                st.session_state.human_vote = None
                st.rerun()
    
    # Reset debate button - use a unique key
    if st.button("Reset Debate", key="reset_debate_button", on_click=reset_debate):
        pass

def reset_debate():
    """Reset the debate state."""
    st.session_state.debate_active = False
    st.session_state.debate_history = []
    st.session_state.human_vote = None
    
def render_loading_animation():
    """Render a loading animation."""
    with st.spinner("Claude is thinking..."):
        # Simulate loading
        time.sleep(0.5)