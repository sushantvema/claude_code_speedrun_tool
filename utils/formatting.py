from typing import Dict, List
import re

def format_debate_message(message: Dict) -> str:
    """
    Format a debate message for display.
    
    Args:
        message: Message dictionary with content and metadata
        
    Returns:
        Formatted message string
    """
    content = message.get("content", "")
    
    # Clean up any markdown formatting issues
    content = clean_markdown(content)
    
    return content

def clean_markdown(text: str) -> str:
    """
    Clean up markdown formatting issues.
    
    Args:
        text: The markdown text to clean
        
    Returns:
        Cleaned markdown text
    """
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Ensure proper spacing for headers
    text = re.sub(r'(^|\n)#([^#])', r'\1# \2', text)
    
    return text

def format_debate_summary(debate_data: Dict) -> str:
    """
    Format a debate summary for export.
    
    Args:
        debate_data: Dictionary with debate information
        
    Returns:
        Formatted summary string
    """
    topic = debate_data.get("topic", "Unknown Topic")
    messages = debate_data.get("messages", [])
    
    summary = f"# Debate Summary: {topic}\n\n"
    
    # Group messages by round
    current_round = 0
    for msg in messages:
        msg_round = msg.get("round", 0)
        
        if msg_round > current_round:
            current_round = msg_round
            summary += f"\n## Round {current_round}\n\n"
        
        perspective = msg.get("perspective", "").upper()
        content = msg.get("content", "")
        
        summary += f"### {perspective} Position\n\n{content}\n\n"
    
    return summary