# Perplexity Ask MCP Integration Implementation Checklist

This document outlines the strategy for integrating Perplexity Ask MCP for real-time web research capabilities into our Claude vs Claude debate system. This enhancement will allow debaters to access up-to-date information during debates, making arguments more factual and evidence-based.

## 1. Technical Prerequisites

- [ ] Set up the Perplexity Sonar API account
  - [ ] Sign up for a Sonar API account at https://docs.perplexity.ai/guides/getting-started
  - [ ] Generate API key from developer dashboard
  - [ ] Set up environment variable `PERPLEXITY_API_KEY`

- [ ] Install MCP server components
  - [ ] Clone ModelContextProtocol repository: `git clone git@github.com:ppl-ai/modelcontextprotocol.git`
  - [ ] Navigate to perplexity-ask directory and install dependencies: `cd modelcontextprotocol/perplexity-ask && npm install`
  - [ ] Build Docker image: `docker build -t mcp/perplexity-ask:latest -f Dockerfile .`

- [ ] Configure system MCP settings
  - [ ] Update Claude desktop configuration file with Perplexity Ask MCP server settings
  - [ ] Test configuration by verifying tools are visible in Claude desktop

## 2. Application Architecture Updates

- [ ] Modify `config/settings.py`
  - [ ] Add flag `ENABLE_RESEARCH_TOOLS` to toggle research capability
  - [ ] Add configuration for research tool timeouts and rate limits
  - [ ] Add system prompts to guide tool usage during debates

- [ ] Update `modules/claude_api.py`
  - [ ] Extend `generate_response` method to support tool use
  - [ ] Create new method `research_with_perplexity` for web searches
  - [ ] Add error handling for API request failures
  - [ ] Implement rate limiting and timeout handling

- [ ] Enhance `modules/debate_engine.py`
  - [ ] Add research capability to debate stages
  - [ ] Create mechanism for tracking citations and sources
  - [ ] Implement research phase before each debate stage (preparation, rebuttals)
  - [ ] Add validation for factual claims based on research

## 3. Integration Points

- [ ] Preparation Phase Enhancement
  - [ ] Allow debaters to research topic before creating debate plans
  - [ ] Include cited sources in the debate plan
  - [ ] Store research results for use in later stages

- [ ] Argument Research
  - [ ] Enable research before generating each debate response
  - [ ] Implement a system to request specific information needed for arguments
  - [ ] Create a format for storing and presenting research findings

- [ ] Rebuttal Enhancement
  - [ ] Allow debaters to fact-check opponent's claims through research
  - [ ] Enable finding counterevidence to opponent's arguments
  - [ ] Implement approach for displaying source credibility

- [ ] Citation System
  - [ ] Create standardized citation format for debate responses
  - [ ] Track and display sources used by each debater
  - [ ] Add UI element to show full citations on demand

## 4. UI Updates (`ui/components.py`)

- [ ] Add research indicators in the debate display
  - [ ] Create loading animations during research phase
  - [ ] Add source citation displays below debate content
  - [ ] Design UI for expanded source information

- [ ] Research Controls
  - [ ] Add toggle for enabling/disabling research tools
  - [ ] Create controls for setting research depth
  - [ ] Implement interface for viewing full research reports

- [ ] Citation Interaction
  - [ ] Make citations clickable to show full source information
  - [ ] Design source credibility visualization
  - [ ] Implement highlighting for statements backed by research

## 5. Perplexity Ask Implementation Details

- [ ] MCP Message Format
  - [ ] Structure messages for optimal research results
  - [ ] Define clear research objectives for each query
  - [ ] Create templates for different research needs (fact-checking, evidence gathering, etc.)

- [ ] Tool Calling Logic
  - [ ] Determine when to trigger research (automatic vs. specific topics)
  - [ ] Create decision logic for using cached vs. new research
  - [ ] Implement context handling for multi-turn research conversations

- [ ] Search Parameter Optimization
  - [ ] Configure search parameters for debate-specific needs
  - [ ] Define timeout and retry logic
  - [ ] Optimize for scholarly and credible sources

## 6. Testing Strategy

- [ ] Unit Tests
  - [ ] Test Perplexity API integration in isolation
  - [ ] Verify proper citation formatting
  - [ ] Test error handling and fallbacks

- [ ] Integration Tests
  - [ ] Verify end-to-end research workflow
  - [ ] Test debate flow with research enabled/disabled
  - [ ] Evaluate source quality and relevance

- [ ] User Experience Testing
  - [ ] Assess debate quality improvement with research
  - [ ] Measure response time impact
  - [ ] Evaluate citation usefulness for judges

## 7. Deployment and Configuration

- [ ] Environment Setup
  - [ ] Document required environment variables
  - [ ] Create setup script for local development
  - [ ] Provide Docker configuration for production

- [ ] Feature Flags
  - [ ] Implement toggle for research capability
  - [ ] Create configuration for research depth and frequency
  - [ ] Add controls for source types and credibility thresholds

- [ ] Monitoring
  - [ ] Track API usage and costs
  - [ ] Monitor research quality and relevance
  - [ ] Implement logging for debugging

## 8. Code Examples

### Example: Perplexity Research Method in claude_api.py

```python
def research_with_perplexity(self, query: str, context: List[Dict] = None) -> Dict:
    """
    Perform research using Perplexity Ask MCP.
    
    Args:
        query: The research question
        context: Optional previous context for multi-turn research
    
    Returns:
        Dictionary with research results and citations
    """
    messages = context or []
    messages.append({"role": "user", "content": query})
    
    try:
        # This assumes the mcp__perplexity_ask tool is available via tool use
        result = self.client.messages.create(
            model=self.model,
            system="You are a research assistant helping with a debate. Find factual, up-to-date information.",
            messages=messages,
            tools=[{"type": "mcp__perplexity_ask"}],
            tool_choice={"type": "mcp__perplexity_ask"},
            max_tokens=1024,
        )
        
        # Process and format the research results
        sources = self._extract_citations(result)
        
        return {
            "content": result.content[0].text,
            "sources": sources,
            "success": True
        }
    except Exception as e:
        return {
            "content": f"Research could not be completed: {str(e)}",
            "sources": [],
            "success": False
        }
```

### Example: Integration in debate_engine.py

```python
def _generate_pro_response_with_research(self, stage: str) -> str:
    """Generate response from pro perspective with research capability."""
    # First, determine research needs based on stage and topic
    research_queries = self._generate_research_queries(stage, "pro/yes")
    
    research_results = {}
    for query in research_queries:
        result = self.claude_api.research_with_perplexity(query)
        if result["success"]:
            research_results[query] = result
    
    # Include research results in the prompt
    research_context = self._format_research_for_prompt(research_results)
    
    # Generate response with research-enhanced prompt
    stage_instructions = self._get_stage_instructions(stage, "pro/yes")
    
    system_prompt = f"""
    You are participating in a structured debate on the topic: "{self.topic}"
    
    Your assigned perspective is: PRO/YES
    
    {stage_instructions}
    
    You have access to the following research:
    {research_context}
    
    Guidelines:
    1. Make strong, logical arguments supporting your assigned perspective
    2. Use evidence and reasoning to back your claims
    3. Cite sources when using factual information from research
    4. Respond to counterarguments raised by your opponent
    5. Be respectful and focused on the topic
    6. Keep responses concise (3-5 paragraphs maximum)
    7. Do not switch sides or argue against your assigned perspective
    {self.pro_personality if self.pro_personality else ""}
    """
    
    return self.claude_api.debate_response(
        scenario=self.topic,
        perspective="pro/yes",
        history=self._get_formatted_history(stage, "pro"),
        research_context=research_context
    )
```

## 9. Advanced Features (Stretch Goals)

- [ ] Adaptive Research Depth
  - [ ] Analyze topic difficulty to determine research needs
  - [ ] Adjust research depth based on debate stage
  - [ ] Implement targeted research for specific claims

- [ ] Opponent Claim Analysis
  - [ ] Automatically identify and fact-check opponent claims
  - [ ] Find counterevidence for refutation
  - [ ] Track claim accuracy throughout debate

- [ ] Source Quality Assessment
  - [ ] Implement credibility scoring for sources
  - [ ] Prioritize academic and authoritative sources
  - [ ] Add visual indicators for source reliability

- [ ] Caching and Persistence
  - [ ] Cache research results for similar queries
  - [ ] Persist research between sessions for the same topic
  - [ ] Implement smart invalidation for outdated information

## 10. Rollout Strategy

1. **Phase 1: Basic Integration**
   - Implement core research capability in preparation phase
   - Add simple citation display
   - Test with limited topics

2. **Phase 2: Enhanced Debate Research**
   - Extend research to all debate stages
   - Implement full citation system
   - Add source credibility features

3. **Phase 3: Advanced Features**
   - Deploy adaptive research depth
   - Add opponent claim analysis
   - Implement cached research persistence

## Conclusion

This implementation checklist provides a comprehensive roadmap for integrating Perplexity Ask MCP into our Claude vs Claude debate system. This integration will significantly enhance the quality of debates by providing factual, up-to-date information to support arguments, enabling more informed and evidence-based discussions.