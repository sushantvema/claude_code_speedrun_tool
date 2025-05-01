from typing import List, Dict, Tuple, Optional
from config.settings import DEFAULT_ROUNDS, PRO_SYSTEM_PROMPT, CON_SYSTEM_PROMPT, ENABLE_RESEARCH
from enum import Enum
import utils.research as research_utils

class DebateStage(Enum):
    """Enum representing the current stage of the debate."""
    PREPARATION = "preparation"
    OPENING = "opening"
    FIRST_REBUTTAL = "first_rebuttal"
    SECOND_REBUTTAL = "second_rebuttal"
    CLOSING = "closing"
    COMPLETE = "complete"

class DebateEngine:
    """
    Engine for managing the Claude vs Claude debate process.
    
    This class handles:
    - Debate state management
    - Turn-taking and rounds
    - Message formatting for Claude API
    - Sequential stage progression
    - Research integration
    """
    
    def __init__(self, claude_api):
        """
        Initialize the debate engine.
        
        Args:
            claude_api: Instance of ClaudeAPI for making API calls
        """
        self.claude_api = claude_api
        self.topic = None
        self.max_rounds = DEFAULT_ROUNDS
        self.current_round = 0
        self.debate_messages = []
        self.debate_active = False
        self.current_stage = None
        self.pro_personality = ""
        self.con_personality = ""
        
        # Preparation phase plans
        self.pro_plan = None
        self.con_plan = None
        
        # Research data
        self.enable_research = ENABLE_RESEARCH
        self.pro_research = {}  # Stores research per stage for pro side
        self.con_research = {}  # Stores research per stage for con side
    
    def start_debate(self, topic: str, max_rounds: int = DEFAULT_ROUNDS, 
                    pro_personality: str = "", con_personality: str = ""):
        """
        Start a new debate with the given topic.
        
        Args:
            topic: The debate topic/scenario
            max_rounds: Maximum number of rounds (default: from settings)
            pro_personality: Additional personality traits for pro debater
            con_personality: Additional personality traits for con debater
        """
        self.topic = topic
        self.max_rounds = max_rounds
        self.current_round = 0
        self.debate_messages = []
        self.debate_active = True
        self.current_stage = DebateStage.PREPARATION
        self.pro_personality = pro_personality
        self.con_personality = con_personality
        
        # Generate preparation plans
        return self.generate_preparation_plans()
    
    def generate_preparation_plans(self) -> Tuple[str, str]:
        """
        Generate debate preparation plans for both sides.
        
        Returns:
            Tuple of (pro_plan, con_plan)
        """
        if not self.debate_active:
            return "Debate is not active.", "Debate is not active."
        
        # Conduct research if enabled
        if self.enable_research:
            self._conduct_research("preparation")
        
        # Generate pro side plan with research integration
        pro_plan_prompt = f"""
        You are preparing for a structured debate on the topic: "{self.topic}"
        
        Your assigned perspective is: PRO/YES
        
        Create a brief debate plan outlining:
        1. Your 2-3 main arguments supporting the position
        2. Potential counterarguments you expect from the opposing side
        3. How you will respond to those counterarguments
        4. Your overall strategy for making a persuasive case
        
        Keep your plan concise (maximum 300 words).
        {self.pro_personality if self.pro_personality else ""}
        """
        
        # Add research to pro prompt if available
        pro_research = self.pro_research.get("preparation")
        if pro_research and pro_research.get("success", False):
            research_text = self.claude_api._format_research_for_prompt(pro_research)
            if research_text:
                pro_plan_prompt += f"\n\nYou have access to the following research that may be useful:\n{research_text}\n\nIncorporate this research into your debate plan where relevant."
        
        con_plan_prompt = f"""
        You are preparing for a structured debate on the topic: "{self.topic}"
        
        Your assigned perspective is: CON/NO
        
        Create a brief debate plan outlining:
        1. Your 2-3 main arguments opposing the position
        2. Potential counterarguments you expect from the supporting side
        3. How you will respond to those counterarguments
        4. Your overall strategy for making a persuasive case
        
        Keep your plan concise (maximum 300 words).
        {self.con_personality if self.con_personality else ""}
        """
        
        # Add research to con prompt if available
        con_research = self.con_research.get("preparation")
        if con_research and con_research.get("success", False):
            research_text = self.claude_api._format_research_for_prompt(con_research)
            if research_text:
                con_plan_prompt += f"\n\nYou have access to the following research that may be useful:\n{research_text}\n\nIncorporate this research into your debate plan where relevant."
        
        pro_plan = self.claude_api.generate_response(
            system_prompt="You are a debate coach helping prepare a structured argument.",
            messages=[{"role": "user", "content": pro_plan_prompt}]
        )
        
        con_plan = self.claude_api.generate_response(
            system_prompt="You are a debate coach helping prepare a structured argument.",
            messages=[{"role": "user", "content": con_plan_prompt}]
        )
        
        self.pro_plan = pro_plan
        self.con_plan = con_plan
        
        return pro_plan, con_plan
    
    def approve_plans_and_continue(self) -> None:
        """
        Move from preparation stage to the first debate stage.
        """
        self.current_stage = DebateStage.OPENING
        
    def generate_next_debate_content(self) -> Dict[str, str]:
        """
        Generate the next content based on the current debate stage.
        
        Returns:
            Dictionary with the generated content for the current stage
        """
        if not self.debate_active:
            return {"error": "Debate is not active."}
        
        if self.current_stage == DebateStage.PREPARATION:
            return {"pro_plan": self.pro_plan, "con_plan": self.con_plan}
        
        elif self.current_stage == DebateStage.OPENING:
            pro_response = self._generate_pro_response("opening")
            self._add_to_history("pro", pro_response, stage="opening")
            
            con_response = self._generate_con_response("opening")
            self._add_to_history("con", con_response, stage="opening")
            
            self.current_stage = DebateStage.FIRST_REBUTTAL
            return {"pro": pro_response, "con": con_response, "stage": "opening"}
            
        elif self.current_stage == DebateStage.FIRST_REBUTTAL:
            pro_response = self._generate_pro_response("first_rebuttal")
            self._add_to_history("pro", pro_response, stage="first_rebuttal")
            
            con_response = self._generate_con_response("first_rebuttal")
            self._add_to_history("con", con_response, stage="first_rebuttal")
            
            self.current_stage = DebateStage.SECOND_REBUTTAL
            return {"pro": pro_response, "con": con_response, "stage": "first_rebuttal"}
            
        elif self.current_stage == DebateStage.SECOND_REBUTTAL:
            pro_response = self._generate_pro_response("second_rebuttal")
            self._add_to_history("pro", pro_response, stage="second_rebuttal")
            
            con_response = self._generate_con_response("second_rebuttal")
            self._add_to_history("con", con_response, stage="second_rebuttal")
            
            self.current_stage = DebateStage.CLOSING
            return {"pro": pro_response, "con": con_response, "stage": "second_rebuttal"}
            
        elif self.current_stage == DebateStage.CLOSING:
            pro_response = self._generate_pro_response("closing")
            self._add_to_history("pro", pro_response, stage="closing")
            
            con_response = self._generate_con_response("closing")
            self._add_to_history("con", con_response, stage="closing")
            
            self.current_stage = DebateStage.COMPLETE
            return {"pro": pro_response, "con": con_response, "stage": "closing"}
            
        elif self.current_stage == DebateStage.COMPLETE:
            return {"stage": "complete", "message": "Debate is complete"}
            
        return {"error": "Unknown debate stage"}
    
    def _add_to_history(self, perspective: str, content: str, stage: str) -> None:
        """Add a message to the debate history."""
        self.debate_messages.append({
            "round": self.current_round,
            "perspective": perspective,
            "content": content,
            "stage": stage,
            "is_assistant": True
        })
    
    def _generate_pro_response(self, stage: str) -> str:
        """
        Generate response from the pro perspective for the current stage.
        
        Args:
            stage: The current debate stage
            
        Returns:
            Pro side's response for the current stage
        """
        # Conduct research for this stage if enabled
        if self.enable_research and stage != "preparation":
            self._conduct_research(stage)
        
        stage_instructions = self._get_stage_instructions(stage, "pro/yes")
        
        system_prompt = f"""
        You are participating in a structured debate on the topic: "{self.topic}"
        
        Your assigned perspective is: PRO/YES
        
        {stage_instructions}
        
        Guidelines:
        1. Make strong, logical arguments supporting your assigned perspective
        2. Use evidence and reasoning to back your claims
        3. Respond to counterarguments raised by your opponent
        4. Be respectful and focused on the topic
        5. Keep responses concise (3-5 paragraphs maximum)
        6. Do not switch sides or argue against your assigned perspective
        {self.pro_personality if self.pro_personality else ""}
        """
        
        # Get research for this stage if available
        research_results = self.pro_research.get(stage)
        
        return self.claude_api.debate_response(
            scenario=self.topic,
            perspective="pro/yes",
            history=self._get_formatted_history(stage, "pro"),
            research_results=research_results
        )
    
    def _generate_con_response(self, stage: str) -> str:
        """
        Generate response from the con perspective for the current stage.
        
        Args:
            stage: The current debate stage
            
        Returns:
            Con side's response for the current stage
        """
        stage_instructions = self._get_stage_instructions(stage, "con/no")
        
        system_prompt = f"""
        You are participating in a structured debate on the topic: "{self.topic}"
        
        Your assigned perspective is: CON/NO
        
        {stage_instructions}
        
        Guidelines:
        1. Make strong, logical arguments opposing the given position
        2. Use evidence and reasoning to back your claims
        3. Respond to arguments raised by your opponent
        4. Be respectful and focused on the topic
        5. Keep responses concise (3-5 paragraphs maximum)
        6. Do not switch sides or argue for the position
        {self.con_personality if self.con_personality else ""}
        """
        
        # Get research for this stage if available
        research_results = self.con_research.get(stage)
        
        return self.claude_api.debate_response(
            scenario=self.topic,
            perspective="con/no",
            history=self._get_formatted_history(stage, "con"),
            research_results=research_results
        )
        
    def _conduct_research(self, stage: str) -> None:
        """
        Conduct research for both pro and con perspectives for the current stage.
        
        Args:
            stage: Current debate stage
        """
        if not self.enable_research:
            return
            
        # Generate research queries
        pro_queries = research_utils.generate_research_queries(
            topic=self.topic, 
            stage=stage, 
            perspective="pro",
            debate_history=self.debate_messages
        )
        
        con_queries = research_utils.generate_research_queries(
            topic=self.topic, 
            stage=stage, 
            perspective="con",
            debate_history=self.debate_messages
        )
        
        # Execute research queries
        pro_research_results = None
        con_research_results = None
        
        if pro_queries:
            pro_research_results = self.claude_api.research_with_perplexity(pro_queries[0])
            self.pro_research[stage] = pro_research_results
            
        if con_queries:
            con_research_results = self.claude_api.research_with_perplexity(con_queries[0])
            self.con_research[stage] = con_research_results
    
    def _get_stage_instructions(self, stage: str, perspective: str) -> str:
        """Get stage-specific instructions for the debater."""
        if stage == "opening":
            return "This is your OPENING STATEMENT. Present your main arguments supporting your position. Aim for 3-5 paragraphs."
            
        elif stage == "first_rebuttal":
            return "This is your FIRST REBUTTAL. Address the key points made by your opponent in their opening statement. Defend your position against their critiques."
            
        elif stage == "second_rebuttal":
            return "This is your SECOND REBUTTAL. Strengthen your arguments based on the debate so far. Address any new points raised in the first rebuttal."
            
        elif stage == "closing":
            return "This is your CLOSING STATEMENT. Summarize your strongest arguments and why you believe your position is correct. No new arguments at this stage."
            
        return ""
    
    def _get_formatted_history(self, stage: str, perspective: str) -> List[Dict[str, str]]:
        """
        Format the debate history for API requests based on the current stage.
        
        Args:
            stage: Current debate stage
            perspective: Current perspective (pro/con)
            
        Returns:
            List of message dictionaries with formatted content
        """
        # For the opening statements, include the debate plan
        if stage == "opening":
            plan = self.pro_plan if perspective == "pro" else self.con_plan
            return [{
                "role": "user",
                "content": f"""Topic for debate: {self.topic}

Your debate plan:
{plan}

Now please provide your opening statement based on this plan.
"""
            }]
        
        # For subsequent stages, include relevant history
        formatted_history = [{
            "role": "user",
            "content": f"Topic for debate: {self.topic}\n\nPlease provide your {stage.replace('_', ' ')} for this debate."
        }]
        
        # Add all previous messages that are relevant to the current stage
        relevant_messages = [msg for msg in self.debate_messages 
                            if msg["stage"] in self._get_relevant_previous_stages(stage)]
        
        for msg in relevant_messages:
            formatted_history.append({
                "role": "assistant" if msg.get("is_assistant", False) else "user",
                "content": f"[{msg['perspective'].upper()}]: {msg['content']}"
            })
        
        return formatted_history
    
    def _get_relevant_previous_stages(self, current_stage: str) -> List[str]:
        """Get the stages that should be included in the history for the current stage."""
        stages = ["opening", "first_rebuttal", "second_rebuttal", "closing"]
        current_index = stages.index(current_stage) if current_stage in stages else -1
        
        if current_index <= 0:
            return []
        
        return stages[:current_index]
    
    def is_debate_complete(self) -> bool:
        """
        Check if the debate is complete.
        
        Returns:
            True if the debate has reached the COMPLETE stage
        """
        return self.current_stage == DebateStage.COMPLETE
    
    def get_debate_summary(self) -> Dict:
        """
        Get a summary of the debate.
        
        Returns:
            Dictionary with debate metadata and messages
        """
        return {
            "topic": self.topic,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "is_complete": self.is_debate_complete(),
            "messages": self.debate_messages,
            "pro_plan": self.pro_plan,
            "con_plan": self.con_plan,
            "pro_research": self.pro_research,
            "con_research": self.con_research,
            "enable_research": self.enable_research
        }
        
    def set_research_enabled(self, enabled: bool) -> None:
        """
        Enable or disable research capabilities.
        
        Args:
            enabled: Boolean to enable/disable research
        """
        self.enable_research = enabled
        
    def get_current_stage(self) -> str:
        """Get the current debate stage."""
        return self.current_stage.value if self.current_stage else None