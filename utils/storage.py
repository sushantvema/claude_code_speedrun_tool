import json
import os
from datetime import datetime
from typing import Dict, List, Any

def save_debate_to_file(debate_data: Dict[str, Any], file_path: str = None) -> str:
    """
    Save debate data to a JSON file.
    
    Args:
        debate_data: Dictionary with debate information
        file_path: Optional custom file path
        
    Returns:
        Path to the saved file
    """
    if not file_path:
        # Create a default filename based on topic and date
        topic_slug = debate_data.get("topic", "debate").replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"debate_{topic_slug}_{timestamp}.json"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
    
    # Save the data
    with open(file_path, 'w') as f:
        json.dump(debate_data, f, indent=2)
    
    return file_path

def load_debate_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load debate data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with debate information
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading debate data: {e}")
        return {}

def export_debate_as_markdown(debate_data: Dict[str, Any], file_path: str = None) -> str:
    """
    Export debate data as a markdown file.
    
    Args:
        debate_data: Dictionary with debate information
        file_path: Optional custom file path
        
    Returns:
        Path to the saved file
    """
    from utils.formatting import format_debate_summary
    
    if not file_path:
        # Create a default filename based on topic and date
        topic_slug = debate_data.get("topic", "debate").replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"debate_{topic_slug}_{timestamp}.md"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
    
    # Format and save the data
    markdown_content = format_debate_summary(debate_data)
    
    with open(file_path, 'w') as f:
        f.write(markdown_content)
    
    return file_path