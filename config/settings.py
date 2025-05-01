# Debate settings

# Number of rounds in a debate
DEFAULT_ROUNDS = 3

# Maximum length of responses (in tokens)
MAX_RESPONSE_LENGTH = 1024

# Default temperature for Claude API calls
DEFAULT_TEMPERATURE = 0.7

# Default model
DEFAULT_MODEL = "claude-3-opus-20240229"

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