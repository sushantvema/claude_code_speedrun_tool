## P0 Problems

- The preparation phase as outlined in debate.md is not being shown to the user.
- The user needs to see each generation for each stage ONE AT A TIME with a nice and simple UI
  transition. Having the two columns is nice.
- The user voting button at the very end is causing an error (something about
duplicate ID's for streamlit buttons)

## Stretch Goals

- Implement two text boxes in the sidebar for the user to add "personality
prompts" to the two agents
- Add a funny loading or generating symbol or animation when stages are
inferencing or waiting for claude to return.

## Implementation Checklist

### P0 Fixes
- [ ] Implement preparation phase UI showing debate plans from both sides
  - [ ] Update debate_engine.py to generate preparation plans
  - [ ] Update app.py to show preparation plans in the UI
  - [ ] Add ability to approve or edit plans before debate
- [ ] Modify UI to show debate stages sequentially
  - [ ] Update components.py to display one stage at a time
  - [ ] Add "Next Stage" buttons between debate phases
  - [ ] Preserve the two-column layout for clarity
- [ ] Fix voting button duplicate ID error
  - [ ] Update components.py to use unique IDs for buttons
  - [ ] Ensure proper state management for voting

### Stretch Goals
- [ ] Add personality prompts in sidebar
  - [ ] Update UI with text input fields
  - [ ] Modify the debate_engine.py to incorporate personality traits
- [ ] Add loading animation
  - [ ] Implement loading spinner/animation
  - [ ] Display during API calls to Claude
