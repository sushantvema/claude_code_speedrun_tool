# Debate settings

# Number of rounds in a debate
DEFAULT_ROUNDS = 3

# Maximum length of responses (in tokens)
MAX_RESPONSE_LENGTH = 1024

# Default temperature for Claude API calls
DEFAULT_TEMPERATURE = 0.7

# Default model
DEFAULT_MODEL = "claude-3-7-sonnet-20250219"

# Research settings
ENABLE_RESEARCH = True
PERPLEXITY_TOOL_NAME = "mcp__perplexity_ask"
RESEARCH_TIMEOUT = 30  # seconds
MAX_RESEARCH_QUERIES_PER_STAGE = 3

# Predefined debate topics
DEBATE_TOPICS = {
    "Pineapple on Pizza": "Should pineapple be an acceptable topping on pizza?",
    "Remote Work": "Is remote work better than working in an office?",
    "AI Sentience": "Could AI systems ever truly achieve consciousness or sentience?",
    "Four-Day Workweek": "Should companies adopt a four-day workweek as standard?",
    "Space Exploration": "Should nations prioritize space exploration over solving Earth's problems?",
    "Social Media": "Do social media platforms do more harm than good?",
    "Nuclear Energy": "Is nuclear energy the best solution for combating climate change?",
    "Universal Basic Income": "Should governments implement a universal basic income?",
    "Mandatory Voting": "Should voting be mandatory in democratic elections?",
}

# System prompts
PRO_SYSTEM_PROMPT = """
You are participating in a structured debate.
Your role is to argue strongly FOR the given position.
Make logical arguments, provide evidence when possible, and respond to counterpoints.
Be persuasive but respectful. Avoid logical fallacies.
Keep responses concise (3-5 paragraphs maximum).
"""

CON_SYSTEM_PROMPT = """
You are participating in a structured debate.
Your role is to argue strongly AGAINST the given position.
Make logical arguments, provide evidence when possible, and respond to counterpoints.
Be persuasive but respectful. Avoid logical fallacies.
Keep responses concise (3-5 paragraphs maximum).
"""

# Research prompts
RESEARCH_SYSTEM_PROMPT = """
You are a research assistant helping in a structured debate. 
Your job is to find factual, up-to-date information that is relevant to the debate topic.
Focus on finding verifiable facts, statistics, expert opinions, and credible sources.
Provide balanced information that could support either side of the debate.
Cite your sources clearly so they can be referenced in the debate.
"""

PRO_RESEARCH_PROMPT_TEMPLATE = """
I need to research information to support the PRO/YES position on this debate topic: "{topic}"
For the current debate stage: {stage}

Based on the debate so far, I need information on the following aspects:
{research_aspects}

Please find factual information, statistics, expert opinions, or studies that would strengthen PRO arguments.
Focus on finding credible and recent sources that I can cite in my debate.
"""

CON_RESEARCH_PROMPT_TEMPLATE = """
I need to research information to support the CON/NO position on this debate topic: "{topic}"
For the current debate stage: {stage}

Based on the debate so far, I need information on the following aspects:
{research_aspects}

Please find factual information, statistics, expert opinions, or studies that would strengthen CON arguments.
Focus on finding credible and recent sources that I can cite in my debate.
"""
