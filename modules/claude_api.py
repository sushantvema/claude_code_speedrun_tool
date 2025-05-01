import os
import anthropic
import json
from typing import List, Dict, Any, Optional
from config.settings import DEFAULT_MODEL, ENABLE_RESEARCH, PERPLEXITY_TOOL_NAME, RESEARCH_TIMEOUT, RESEARCH_SYSTEM_PROMPT
from modules.perplexity_api import PerplexityAPI

class ClaudeAPI:
    """Wrapper for the Anthropic Claude API."""
    
    def __init__(self):
        """Initialize the Claude API client."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        
        # Initialize with just the API key, without any additional parameters
        # that might cause compatibility issues across different versions
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = DEFAULT_MODEL
        
        # Initialize research cache
        self.research_cache = {}
        
        # Initialize Perplexity API client if environment variable is set
        try:
            self.perplexity_client = PerplexityAPI()
            self.perplexity_available = True
        except ValueError:
            self.perplexity_available = False
    
    def set_model(self, model_name: str):
        """Change the model being used."""
        self.model = model_name
    
    def generate_response(self, 
                         system_prompt: str, 
                         messages: List[Dict[str, str]],
                         use_tools: bool = False) -> str:
        """
        Generate a response from Claude using the provided system prompt and messages.
        
        Args:
            system_prompt: The system prompt to guide Claude's behavior
            messages: List of message dictionaries with 'role' and 'content'
            use_tools: Whether to enable tool use for this request
            
        Returns:
            The generated response text
        """
        try:
            params = {
                "model": self.model,
                "system": system_prompt,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
            }
            
            # Add tools if enabled
            if use_tools and ENABLE_RESEARCH:
                params["tools"] = [{
                    "name": PERPLEXITY_TOOL_NAME,
                    "description": "Search the web for real-time information"
                }]
                params["tool_choice"] = "auto"
            
            response = self.client.messages.create(**params)
            
            # Handle tool calls in the response if present
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Process tool calls and their results
                for tool_call in response.tool_calls:
                    # Currently we only handle Perplexity Ask MCP
                    if tool_call.name == PERPLEXITY_TOOL_NAME:
                        # Tool calls are handled by the MCP server automatically
                        # We just need to extract the content from the response
                        pass
            
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def debate_response(self, 
                      scenario: str, 
                      perspective: str, 
                      history: List[Dict[str, str]],
                      research_results: Optional[Dict] = None) -> str:
        """
        Generate a debate response from Claude.
        
        Args:
            scenario: The debate scenario/topic
            perspective: The debater's assigned perspective (yes/no, pro/con)
            history: Previous messages in the debate
            research_results: Optional research results to incorporate
            
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
        
        # Add research results if available
        if research_results:
            research_context = self._format_research_for_prompt(research_results)
            if research_context:
                system_prompt += f"\n\nYou have access to the following research that may support your arguments:\n{research_context}\n\nWhen using this research, cite the sources appropriately."
        
        return self.generate_response(system_prompt, formatted_messages)
    
    def research_with_perplexity(self, query: str, context: List[Dict] = None) -> Dict:
        """
        Perform research using Perplexity API.
        
        Args:
            query: The research question
            context: Optional previous context for multi-turn research
        
        Returns:
            Dictionary with research results and citations
        """
        # Check cache first
        cache_key = query.strip().lower()
        if cache_key in self.research_cache:
            return self.research_cache[cache_key]
        
        # Method 1: Use Perplexity API client directly if available
        if self.perplexity_available:
            try:
                result = self.perplexity_client.search_with_citations(
                    query=query,
                    system_prompt=RESEARCH_SYSTEM_PROMPT
                )
                
                # Cache the result
                self.research_cache[cache_key] = result
                
                return result
            except Exception as e:
                # If direct API fails, fall back to MCP method
                print(f"Direct Perplexity API failed, falling back to MCP: {str(e)}")
                pass
        
        # Method 2: Use Perplexity Ask MCP tool as fallback
        try:
            messages = context or []
            messages.append({"role": "user", "content": query})
            
            # Use Perplexity Ask MCP tool
            response = self.client.messages.create(
                model=self.model,
                system=RESEARCH_SYSTEM_PROMPT,
                messages=messages,
                tools=[{
                    "name": PERPLEXITY_TOOL_NAME,
                    "description": "Search the web for real-time information"
                }],
                tool_choice={"type": "function", "function": {"name": PERPLEXITY_TOOL_NAME}},
                max_tokens=1024,
                temperature=0.3,
                timeout=RESEARCH_TIMEOUT
            )
            
            # Extract content and sources
            content = response.content[0].text
            sources = self._extract_citations(content)
            
            result = {
                "content": content,
                "sources": sources,
                "success": True
            }
            
            # Cache the result
            self.research_cache[cache_key] = result
            
            return result
        except Exception as e:
            result = {
                "content": f"Research could not be completed: {str(e)}",
                "sources": [],
                "success": False
            }
            return result
    
    def _extract_citations(self, text: str) -> List[Dict]:
        """Extract citation information from research response."""
        sources = []
        
        # Try to find citations in format [1], [2], etc.
        import re
        citations = re.findall(r'\[([\d]+)\]', text)
        
        # Extract full citation information from the end of the text
        citation_section = re.search(r'Sources:|References:|Citations:(.*?)$', text, re.DOTALL | re.IGNORECASE)
        
        if citation_section:
            citation_text = citation_section.group(1)
            # Parse individual citations
            citation_matches = re.finditer(r'\[([\d]+)\](.*?)(?=\[[\d]+\]|\Z)', citation_text, re.DOTALL)
            
            for match in citation_matches:
                num = match.group(1)
                citation = match.group(2).strip()
                # Extract URL if present
                url_match = re.search(r'https?://[^\s\)]+', citation)
                url = url_match.group(0) if url_match else ""
                
                sources.append({
                    "id": num,
                    "text": citation,
                    "url": url
                })
        
        return sources
    
    def _format_research_for_prompt(self, research_results: Dict) -> str:
        """Format research results for inclusion in prompts."""
        if not research_results or not research_results.get("success", False):
            return ""
        
        content = research_results.get("content", "")
        sources = research_results.get("sources", [])
        
        # Format only the key information and sources
        research_text = "RESEARCH FINDINGS:\n\n"
        
        # Extract key points from content, removing any "I'll research" or similar meta-text
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
        
        research_text += "\n".join(content_lines).strip() + "\n\n"
        
        # Add formatted sources
        if sources:
            research_text += "SOURCES:\n"
            for source in sources:
                research_text += f"[{source['id']}] {source['text']}\n"
        
        return research_text