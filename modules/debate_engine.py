from typing import List, Dict, Tuple, Optional
from config.settings import DEFAULT_ROUNDS, PRO_SYSTEM_PROMPT, CON_SYSTEM_PROMPT

class DebateEngine:
    """
    Engine for managing the Claude vs Claude debate process.
    
    This class handles:
    - Debate state management
    - Turn-taking and rounds
    - Message formatting for Claude API
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
    
    def start_debate(self, topic: str, max_rounds: int = DEFAULT_ROUNDS):
        """
        Start a new debate with the given topic.
        
        Args:
            topic: The debate topic/scenario
            max_rounds: Maximum number of rounds (default: from settings)
        """
        self.topic = topic
        self.max_rounds = max_rounds
        self.current_round = 0
        self.debate_messages = []
        self.debate_active = True
        
        # Generate opening statements
        return self.generate_next_round()
    
    def generate_next_round(self) -> Tuple[str, str]:
        """
        Generate the next round of debate responses.
        
        Returns:
            Tuple of (pro_response, con_response)
        """
        if not self.debate_active:
            return "Debate is not active.", "Debate is not active."
        
        if self.is_debate_complete():
            return "Debate is complete.", "Debate is complete."
        
        self.current_round += 1
        
        # Generate pro side response
        pro_response = self._generate_pro_response()
        
        # Add to message history
        self.debate_messages.append({
            "round": self.current_round,
            "perspective": "pro",
            "content": pro_response,
            "is_assistant": True
        })
        
        # Generate con side response
        con_response = self._generate_con_response()
        
        # Add to message history
        self.debate_messages.append({
            "round": self.current_round,
            "perspective": "con",
            "content": con_response,
            "is_assistant": True
        })
        
        return pro_response, con_response
    
    def _generate_pro_response(self) -> str:
        """Generate response from the pro perspective."""
        return self.claude_api.debate_response(
            scenario=self.topic,
            perspective="pro/yes",
            history=self._get_formatted_history()
        )
    
    def _generate_con_response(self) -> str:
        """Generate response from the con perspective."""
        # Include the pro response from this round
        history = self._get_formatted_history()
        
        return self.claude_api.debate_response(
            scenario=self.topic,
            perspective="con/no",
            history=history
        )
    
    def _get_formatted_history(self) -> List[Dict[str, str]]:
        """
        Format the debate history for API requests.
        
        Returns:
            List of message dictionaries with formatted content
        """
        # For the first round, create an introductory prompt
        if self.current_round == 1:
            return [{
                "role": "user",
                "content": f"Topic for debate: {self.topic}\n\nPlease provide your opening statement."
            }]
        
        # Otherwise, format the existing messages
        formatted_history = [{
            "role": "user",
            "content": f"Topic for debate: {self.topic}\n\nRound {self.current_round}: Please respond to the arguments so far."
        }]
        
        # Add previous rounds to history
        for msg in self.debate_messages:
            formatted_history.append({
                "role": "assistant" if msg.get("is_assistant", False) else "user",
                "content": f"[{msg['perspective'].upper()}]: {msg['content']}"
            })
        
        return formatted_history
    
    def is_debate_complete(self) -> bool:
        """
        Check if the debate is complete.
        
        Returns:
            True if all rounds have been completed, False otherwise
        """
        return self.current_round >= self.max_rounds
    
    def get_debate_summary(self) -> Dict:
        """
        Get a summary of the debate.
        
        Returns:
            Dictionary with debate metadata and messages
        """
        return {
            "topic": self.topic,
            "rounds_completed": self.current_round,
            "max_rounds": self.max_rounds,
            "is_complete": self.is_debate_complete(),
            "messages": self.debate_messages
        }