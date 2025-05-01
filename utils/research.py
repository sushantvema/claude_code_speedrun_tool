from typing import List, Dict, Any, Optional
from config.settings import MAX_RESEARCH_QUERIES_PER_STAGE, PRO_RESEARCH_PROMPT_TEMPLATE, CON_RESEARCH_PROMPT_TEMPLATE

def generate_research_queries(topic: str, stage: str, perspective: str, debate_history: List[Dict] = None) -> List[str]:
    """
    Generate research queries based on the debate topic, stage, and perspective.
    
    Args:
        topic: The debate topic
        stage: Current stage of the debate
        perspective: Pro/Con perspective
        debate_history: Optional history of previous debate messages
        
    Returns:
        List of research queries
    """
    # Stage-specific research aspects
    stage_aspects = {
        "preparation": [
            "Key statistics and facts related to this topic",
            "Major arguments for and against this position",
            "Expert opinions or recent studies on this topic",
            "Historical context of this debate topic"
        ],
        "opening": [
            "Key statistics supporting my position",
            "Expert opinions aligned with my perspective",
            "Recent developments or studies related to this topic",
            "Examples that demonstrate the validity of my position"
        ],
        "first_rebuttal": [
            "Counter-evidence to opponent's main points",
            "Logical weaknesses in opposing arguments",
            "Additional evidence supporting my main arguments",
            "Expert opinions that refute opponent's claims"
        ],
        "second_rebuttal": [
            "Deeper evidence to strengthen my position against critiques",
            "Additional facts that address opponent's rebuttals",
            "Studies or expert opinions that directly counter opponent's evidence",
            "Real-world examples that reinforce my arguments"
        ],
        "closing": [
            "Most compelling evidence supporting my position",
            "Strongest expert opinions aligned with my stance",
            "Clear statistics that demonstrate my position's validity",
            "Final facts that address remaining counterarguments"
        ]
    }
    
    # Get research aspects based on stage
    aspects = stage_aspects.get(stage, stage_aspects["preparation"])
    
    # Limit to a smaller set of aspect to avoid rate limiting
    selected_aspects = aspects[:min(MAX_RESEARCH_QUERIES_PER_STAGE, len(aspects))]
    aspects_text = "\n".join(f"- {aspect}" for aspect in selected_aspects)
    
    # Create queries using the appropriate template
    template = PRO_RESEARCH_PROMPT_TEMPLATE if perspective.lower() == "pro" or perspective.lower() == "pro/yes" else CON_RESEARCH_PROMPT_TEMPLATE
    
    query = template.format(
        topic=topic,
        stage=stage,
        research_aspects=aspects_text
    )
    
    # For now, we just return a single comprehensive query
    # In a more advanced system, you could generate multiple specific queries
    return [query]

def extract_debate_claims(debate_history: List[Dict]) -> List[str]:
    """
    Extract claims from debate history that might need fact-checking.
    
    Args:
        debate_history: List of debate message dictionaries
        
    Returns:
        List of claims that could be researched
    """
    claims = []
    
    if not debate_history:
        return claims
    
    # Look for claims in opponent's messages
    for msg in debate_history:
        if not msg.get("content"):
            continue
        
        content = msg["content"]
        lines = content.split("\n")
        
        # Simple heuristic: sentences that might contain factual claims often
        # have numbers, percentages, or phrases like "studies show", "according to"
        for line in lines:
            if any(marker in line.lower() for marker in 
                   ["study", "research", "statistics", "data", "report", "according to", 
                    "evidence", "shows that", "found that", "%", "percent"]):
                claims.append(line.strip())
    
    return claims[:MAX_RESEARCH_QUERIES_PER_STAGE]  # Limit claims to avoid too many queries

def format_research_for_display(research_results: Dict) -> str:
    """
    Format research results for UI display.
    
    Args:
        research_results: Research results dictionary
        
    Returns:
        Formatted HTML-compatible string for display
    """
    if not research_results or not research_results.get("success", False):
        return "<p><em>No research results available.</em></p>"
    
    content = research_results.get("content", "")
    sources = research_results.get("sources", [])
    
    # Format content, preserving paragraphs
    formatted_content = ""
    
    # Remove initial meta-text and ending citations for display
    lines = content.split("\n")
    content_lines = []
    in_content = False
    
    for line in lines:
        # Skip initial "I'll search" lines
        if not in_content and ('I will' in line or 'I\'ll' in line or 'searching' in line.lower()):
            continue
        in_content = True
        # Stop at sources section
        if 'sources:' in line.lower() or 'references:' in line.lower():
            break
        content_lines.append(line)
    
    content_text = "\n".join(content_lines).strip()
    
    # Convert to HTML paragraphs
    formatted_content = "<p>" + content_text.replace("\n\n", "</p><p>") + "</p>"
    
    # Format citations with superscripts and tooltips
    for source in sources:
        citation_id = source.get("id", "")
        citation_text = source.get("text", "").replace('"', '&quot;')
        
        # Replace [n] with a superscript that has a tooltip
        formatted_content = formatted_content.replace(
            f"[{citation_id}]", 
            f'<sup class="citation" title="{citation_text}">[{citation_id}]</sup>'
        )
    
    # Add sources section
    if sources:
        formatted_content += "<div class='sources'><h5>Sources</h5><ol>"
        for source in sources:
            source_text = source.get("text", "")
            source_url = source.get("url", "")
            
            if source_url:
                formatted_content += f'<li><a href="{source_url}" target="_blank">{source_text}</a></li>'
            else:
                formatted_content += f'<li>{source_text}</li>'
        
        formatted_content += "</ol></div>"
    
    return formatted_content