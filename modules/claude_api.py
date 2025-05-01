import os
import anthropic
from typing import List, Dict, Any

class ClaudeAPI:
    """Wrapper for the Anthropic Claude API."""
    
    def __init__(self):
        """Initialize the Claude API client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-opus-20240229"  # Default model
    
    def set_model(self, model_name: str):
        """Change the model being used."""
        self.model = model_name
    
    def generate_response(self, 
                         system_prompt: str, 
                         messages: List[Dict[str, str]]) -> str:
        """
        Generate a response from Claude using the provided system prompt and messages.
        
        Args:
            system_prompt: The system prompt to guide Claude's behavior
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            The generated response text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def debate_response(self, 
                      scenario: str, 
                      perspective: str, 
                      history: List[Dict[str, str]]) -> str:
        """
        Generate a debate response from Claude.
        
        Args:
            scenario: The debate scenario/topic
            perspective: The debater's assigned perspective (yes/no, pro/con)
            history: Previous messages in the debate
            
        Returns:
            Claude's response as a debater
        """
        system_prompt = f"""
        You are participating in a structured debate on the topic: "{scenario}"
        
        Your assigned perspective is: {perspective}
        
        Guidelines:
        1. Make strong, logical arguments supporting your assigned perspective
        2. Use evidence and reasoning to back your claims
        3. Respond to counterarguments raised by your opponent
        4. Be respectful and focused on the topic
        5. Keep responses concise (3-5 paragraphs maximum)
        6. Do not switch sides or argue against your assigned perspective
        """
        
        # Format the message history for API request
        formatted_messages = []
        for msg in history:
            formatted_messages.append({
                "role": "assistant" if msg.get("is_assistant", False) else "user",
                "content": msg["content"]
            })
        
        return self.generate_response(system_prompt, formatted_messages)