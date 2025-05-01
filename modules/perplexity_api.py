import os
from openai import OpenAI
from typing import List, Dict, Any, Optional

class PerplexityAPI:
    """Wrapper for the Perplexity Sonar API."""
    
    def __init__(self):
        """Initialize the Perplexity API client."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is not set.")
        
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        self.model = "sonar-pro"  # Default model
    
    def set_model(self, model_name: str):
        """Change the model being used."""
        self.model = model_name
    
    def search(self, 
              query: str, 
              system_prompt: str = None,
              previous_messages: List[Dict[str, str]] = None, 
              stream: bool = False) -> Any:
        """
        Perform a search query using Perplexity Sonar.
        
        Args:
            query: The search query
            system_prompt: Optional system prompt to guide the response
            previous_messages: Optional list of previous messages for context
            stream: Whether to stream the response
            
        Returns:
            Response from Perplexity Sonar
        """
        # Prepare messages
        messages = previous_messages or []
        
        # Add system message if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Add user query
        messages.append({"role": "user", "content": query})
        
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
            )
            
            # Process response based on streaming option
            if stream:
                return response  # Return stream directly
            else:
                return response.choices[0].message.content
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def search_with_citations(self, query: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Perform a search with structured citation extraction.
        
        Args:
            query: The search query
            system_prompt: Optional system prompt to guide the response
            
        Returns:
            Dictionary with response content and extracted citations
        """
        default_system_prompt = """
        You are a helpful research assistant. Provide accurate, well-researched information
        with proper citations using [1], [2], etc. format. Include a list of all sources at
        the end of your response under a 'Sources:' section.
        """
        
        final_system_prompt = system_prompt or default_system_prompt
        
        raw_response = self.search(query, final_system_prompt)
        
        # Extract content and citations
        content = raw_response
        sources = self._extract_citations(content)
        
        return {
            "content": content,
            "sources": sources,
            "success": True
        }
    
    def _extract_citations(self, text: str) -> List[Dict[str, str]]:
        """Extract citation information from search response."""
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