# Agno Streamlit Project Structure

```
agno_streamlit_project/
├── README.md
├── requirements.txt
├── config.py
├── test_project.py
├── agents/
│   ├── __init__.py
│   ├── main_agent.py
│   └── enhanced_agent.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── knowledge/
│   └── .gitkeep
├── storage/
│   ├── .gitkeep
│   └── agent_sessions.db
```

## Key Components

1. **agents/** - Contains Agno agent definitions
   - `main_agent.py`: Basic agent implementation
   - `enhanced_agent.py`: Agent with storage capabilities

2. **app/** - Streamlit frontend application
   - `main.py`: Main Streamlit application
   - `utils.py`: Utility functions for the frontend

3. **config.py** - Configuration settings

4. **knowledge/** - Directory for knowledge base files

5. **storage/** - Directory for agent session storage

6. **requirements.txt** - Project dependencies

7. **README.md** - Project documentation

8. **test_project.py** - Test script to verify project structure