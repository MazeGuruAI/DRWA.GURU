# Agno Streamlit Project with Asset Verification Agent

This project demonstrates an AI agent built with Agno and Streamlit that includes asset verification capabilities.

## Features

1. **General AI Assistant**: Answer questions and provide information
2. **Asset Verification Agent**: 
   - Multi-modal data parsing (documents and images)
   - Authenticity verification (format, content, signatures)
   - Compliance checking (legal regulations)
   - Verification report generation
3. **Asset Valuation Agent**: 
   - Asset parameter collection
   - Market data research
   - Economic indicator analysis
   - Industry trend evaluation
   - Traditional valuation method application
   - Comprehensive valuation reporting

## Project Structure

```
agno_streamlit_project/
├── agents/
│   ├── main_agent.py              # Main Agno agent
│   ├── asset_verification_agent.py # Asset verification agent
│   ├── asset_valuation_agent.py   # Asset valuation agent
│   └── enhanced_agent.py          # Combined agent with all capabilities
├── app/
│   ├── main.py                    # Streamlit application
│   └── utils.py                   # Utility functions
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Getting Started

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable:
   
   On Linux/Mac:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   On Windows (Command Prompt):
   ```cmd
   set OPENAI_API_KEY=your_api_key_here
   ```
   
   On Windows (PowerShell):
   ```powershell
   $env:OPENAI_API_KEY="your_api_key_here"
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app/main.py
   ```

## Using the Asset Agents

### Asset Verification
1. Upload asset documents or images using the file uploader in the sidebar
2. Ask the agent to verify the assets by mentioning "verify assets" or similar phrases
3. The agent will analyze the documents for:
   - Authenticity (format, content, signatures)
   - Legal compliance
   - Trading restrictions
4. Receive a detailed verification report

### Asset Valuation
1. Ask the agent to value an asset (property, equipment, etc.)
2. Provide asset parameters when requested (type, location, area, usage years, etc.)
3. The agent will:
   - Collect market data using BaiduSearchTools
   - Analyze economic indicators and industry trends
   - Apply traditional valuation methods
   - Generate a comprehensive valuation report

## Agent Capabilities

### Multi-modal Data Parsing
- Processes both documents and images
- Extracts text, metadata, and visual elements
- Identifies document types and formats
- Analyzes visual elements in asset images for authenticity verification

### Authenticity Verification
- Checks document formatting consistency
- Verifies content integrity
- Validates signatures and official markings
- Analyzes visual elements in images for signs of tampering
- Uses Google Search to cross-reference information

### Compliance Checking
- Researches applicable laws and regulations
- Verifies legal tradability of assets
- Identifies restrictions or limitations
- Checks for required documentation

### Report Generation
- Provides comprehensive verification reports
- Highlights issues and concerns
- Gives clear recommendations
- Formats reports in readable markdown

### Asset Valuation Reporting
- Provides detailed valuation analysis
- Includes data sources and methodology
- Highlights key factors affecting valuation
- Gives clear final valuation estimate with confidence level

## Customization

You can customize the agent behavior by modifying:
- `agents/asset_verification_agent.py` - Verification logic and instructions
- `agents/enhanced_agent.py` - Combined agent capabilities
- `app/main.py` - Streamlit UI components
- `config.py` - Configuration settings

## Dependencies

See `requirements.txt` for the complete list of dependencies.