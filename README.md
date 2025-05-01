# Claude vs Claude Debate System

A minimal Streamlit application that hosts a debate between two instances of Claude, arguing opposite sides of a topic with human judge evaluation.

> *This project was conceived and implemented in two hours at the [First Ever
> Claude Speedrun Hackathon @ Berkeley](https://lu.ma/4zxa9ash?tk=N05F0U)*

## DEMO LINKS

- [YouTube 7 Minutes](https://youtu.be/avVqaOqdVIo)
- [DevPost Submission](https://devpost.com/software/claude-vs-claude-ultimate-debate-system)

## Features

- Select from predefined debate topics or create your own
- Watch two Claude instances debate opposite sides of an issue
- Control debate progression with a turn-based system
- Vote for the debater you thought presented better arguments
- Simple and intuitive UI built with Streamlit
- Real-time research capabilities using Perplexity Sonar API
- Citation support for factual claims in debates

## System Architecture

```mermaid
graph TD
    %% Main Components
    User[User/Judge] --> |Selects Topic & Settings| App[Streamlit App]
    App --> |Renders UI| UI[UI Components]
    App --> |Manages Debate| DE[Debate Engine]
    DE --> |API Calls| CAPI[Claude API]
    DE --> |Research Queries| RC[Research Component]
    
    %% Research Flow
    RC --> |Direct API| PAPI[Perplexity API Client]
    RC --> |MCP Fallback| PMCP[Perplexity MCP Integration]
    PAPI --> |Web Search| Web((Internet))
    PMCP --> |Web Search| Web

    %% Debate Flow
    subgraph Debate Flow
        DE --> |Preparation| Stage1[Preparation Phase]
        Stage1 --> |Plans Approved| Stage2[Opening Statements]
        Stage2 --> Stage3[First Rebuttal]
        Stage3 --> Stage4[Second Rebuttal]
        Stage4 --> Stage5[Closing Statements]
        Stage5 --> |Complete| Vote[User Voting]
    end

    %% Two Claude Instances
    CAPI --> |Pro Arguments| Claude1[Claude Instance 1\nPRO Position]
    CAPI --> |Con Arguments| Claude2[Claude Instance 2\nCON Position]
    
    %% Research Integration
    subgraph Research Integration
        RC --> |Pro Research| ProResearch[Pro Side Research]
        RC --> |Con Research| ConResearch[Con Side Research]
        ProResearch --> |Citations| Claude1
        ConResearch --> |Citations| Claude2
    end

    %% Data Storage
    Config[Configuration\nSettings.py] --> DE
    Config --> CAPI
    Config --> RC
    
    %% UI Components
    UI --> |Displays| DebateUI[Debate Content]
    UI --> |Shows| ResearchUI[Research Data]
    UI --> |Controls| ProgressUI[Debate Progress]
    
    %% Styling
    classDef core fill:#f9f,stroke:#333,stroke-width:2px
    classDef api fill:#bbf,stroke:#333,stroke-width:2px
    classDef ui fill:#bfb,stroke:#333,stroke-width:2px
    classDef flow fill:#fbb,stroke:#333,stroke-width:2px
    
    class App,DE,RC core
    class CAPI,PAPI,PMCP,Claude1,Claude2 api
    class UI,DebateUI,ResearchUI,ProgressUI ui
    class Stage1,Stage2,Stage3,Stage4,Stage5 flow
```

## Getting Started

### Prerequisites

- Python 3.8+
- Anthropic API key
- Perplexity Sonar API key (optional, for research capabilities)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/claude-debate.git
cd claude-debate
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up your environment variables

```bash
cp .env.example .env
```

Then edit `.env` to add your Anthropic API key and Perplexity API key (if using research features).

### Running the App

```bash
streamlit run app.py
```

The app will be available at <http://localhost:8501>

## Project Structure

```
/claude-debate/
├── app.py                   # Main Streamlit entry point
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── modules/
│   ├── claude_api.py        # Claude API wrapper
│   └── debate_engine.py     # Core debate logic
├── ui/
│   └── components.py        # UI components
└── config/
    └── settings.py          # App settings and configurations
```

## Branching Strategy

The project uses the following branching strategy for collaborative development:

- `main`: Production-ready code
- `develop`: Integration branch for features
- Feature branches: Individual components (branched from `develop`)

## Contributing

1. Create a feature branch from `develop`
2. Implement your changes
3. Submit a pull request to merge back into `develop`
4. After testing and review, changes will be merged into `main`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

