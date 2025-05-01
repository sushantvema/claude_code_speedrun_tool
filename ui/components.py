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
        st.write("**Pro / Yes**")
    
    with col2:
        st.write("**Con / No**")
    
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
        
        pro_message = next((msg for msg in stage_messages if msg.get("perspective") == "pro"), None)
        con_message = next((msg for msg in stage_messages if msg.get("perspective") == "con"), None)
        
        # Display stage content in columns without stage headers
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
    
    st.write("**Debate Preparation**")
    st.markdown("""
    Both sides have prepared debate plans. Review and edit them as desired before starting.
    """)
    
    # Display loading message while plans are being generated
    if not debate_engine.pro_plan or not debate_engine.con_plan:
        with st.spinner("Claude is preparing debate plans..."):
            st.info("Generating debate plans... Please wait.")
            # Add a small delay to ensure the UI updates before continuing
            import time
            time.sleep(0.5)
        return
        
    # Initialize session state for edited plans if not exists
    if 'pro_plan_edited' not in st.session_state or not st.session_state.pro_plan_edited:
        st.session_state.pro_plan_edited = debate_engine.pro_plan
    
    if 'con_plan_edited' not in st.session_state or not st.session_state.con_plan_edited:
        st.session_state.con_plan_edited = debate_engine.con_plan
    
    # Create columns for the two plans
    col1, col2 = st.columns(2)
    
    with col1:
        # Display pro plan
        st.write("**Pro/Yes Plan**")
        # Show the pro plan and allow editing
        pro_plan_value = st.session_state.pro_plan_edited if st.session_state.pro_plan_edited else debate_engine.pro_plan
        
        edited_pro_plan = st.text_area(
            "Edit Pro Plan if needed:",
            value=pro_plan_value,
            height=400,
            key="pro_plan_edit_area"
        )
        
        # Update the session state with the edited plan
        st.session_state.pro_plan_edited = edited_pro_plan
    
    with col2:
        # Display con plan
        st.write("**Con/No Plan**")
        # Show the con plan and allow editing
        con_plan_value = st.session_state.con_plan_edited if st.session_state.con_plan_edited else debate_engine.con_plan
        
        edited_con_plan = st.text_area(
            "Edit Con Plan if needed:",
            value=con_plan_value,
            height=400,
            key="con_plan_edit_area"
        )
        
        # Update the session state with the edited plan
        st.session_state.con_plan_edited = edited_con_plan
    
    # Add a hint about editing plans
    st.info("You can completely rewrite the debate plans if desired. The debaters will follow your edited plans precisely without questioning them or acknowledging the edits. Your instructions override all other guidelines.")
    
    # Button to approve plans and start debate
    # Only show the button if we have plans to approve
    if debate_engine.pro_plan and debate_engine.con_plan:
        if st.button("Approve Plans and Start Debate", key="approve_plans"):
            with st.spinner("Generating opening statements..."):
                # Pass the edited plans to the debate engine
                debate_engine.approve_plans_and_continue(
                    pro_plan_edited=st.session_state.pro_plan_edited,
                    con_plan_edited=st.session_state.con_plan_edited
                )
                
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
        st.write("**Vote for the winner**")
        
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
            # Show the voting result with minimal styling
            st.info(f"You voted for the {st.session_state.human_vote.upper()} position")
            
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
    st.session_state.pro_plan_edited = None
    st.session_state.con_plan_edited = None
    
def render_loading_animation():
    """Render a loading animation."""
    with st.spinner("Claude is thinking..."):
        # Simulate loading
