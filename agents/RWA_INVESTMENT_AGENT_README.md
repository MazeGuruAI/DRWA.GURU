# RWA Investment Agent - Comprehensive Investment Advisory System

## 🎯 Overview

The RWA Investment Agent is a sophisticated AI-powered investment advisor designed to help investors make informed decisions about Real World Asset (RWA) tokenized investments. It provides end-to-end investment analysis from market research to portfolio construction and risk management.

## 🚀 Features

### 1. **RWA Asset Collection & Discovery**
- Automatically collects comprehensive RWA project data from https://rwa.xyz/
- Tracks market capitalization, trading volumes, and liquidity metrics
- Monitors new token launches and project updates
- Gathers fundamental data: teams, backers, technology, legal structures

### 2. **Intelligent Asset Classification**
Categorizes RWA assets by:
- **Asset Type**: Real Estate, Commodities, Bonds, Credit, Equity, Art, Infrastructure
- **Risk Profile**: Low, Medium, High risk categories
- **Liquidity**: High, Medium, Low liquidity classifications
- **Yield Type**: Fixed, Variable, or Hybrid returns

### 3. **Comprehensive Asset Comparison**
- Side-by-side comparison of similar RWA products
- Risk-adjusted return analysis (Sharpe Ratio, Sortino Ratio)
- Liquidity metrics and fee structure comparison
- Regulatory compliance assessment
- Tier-based ranking system (S-tier to C-tier)

### 4. **Personalized Investment Strategy**
Generates custom portfolio strategies based on:
- Investment amount and capital available
- Risk tolerance (Conservative, Moderate, Aggressive)
- Investment horizon (Short, Medium, Long-term)
- Liquidity needs and income preferences
- Geographic and asset class preferences

**Example Portfolio Strategies:**

| Portfolio Type | Allocation | Expected Return | Volatility |
|---------------|------------|-----------------|------------|
| Conservative | 60% Treasuries, 25% Bonds, 10% Real Estate, 5% Gold | 4-6% APY | Low |
| Moderate | 30% Treasuries, 30% Real Estate, 20% Credit, 15% Commodities, 5% Infrastructure | 8-12% APY | Medium |
| Aggressive | 25% EM Credit, 25% RE Development, 20% Commodities, 20% PE, 10% Art | 15-25% APY | High |

### 5. **Historical Performance Backtesting**
- Analyzes historical returns and performance metrics
- Calculates risk-adjusted returns and drawdown analysis
- Scenario testing (bull markets, bear markets, inflation, interest rate changes)
- Benchmark comparisons with traditional assets

### 6. **Comprehensive Risk Assessment**
Evaluates multiple risk dimensions:
- **Market Risk**: Volatility, liquidity, correlation analysis
- **Credit Risk**: Default probability, collateral quality
- **Regulatory Risk**: Compliance status, jurisdictional issues
- **Operational Risk**: Smart contract security, custody arrangements
- **Liquidity Risk**: Exit scenarios, lock-up periods

Risk scoring system (1-10 scale) with mitigation strategies

### 7. **Professional Investment Reports**
Generates structured reports including:
- Executive Summary with key recommendations
- Market Overview and trends
- Detailed asset analysis
- Portfolio recommendations with rationale
- Historical performance insights
- Risk assessment and mitigation
- Implementation guide with step-by-step instructions

## 📋 Usage

### Basic Usage

```python
from agents.rwa_investment_agent import get_rwa_investment_agent

# Initialize the agent
agent = get_rwa_investment_agent()

# Request investment analysis
response = agent.run("""
    I have $50,000 to invest in RWA assets.
    My risk tolerance is moderate, and I prefer a balanced approach.
    Investment horizon is 2 years.
    Please recommend a portfolio strategy.
""")

print(response.content)
```

### Running Standalone

```bash
python -m agents.rwa_investment_agent
```

This launches an interactive mode where you can ask investment questions.

## 🎯 Use Cases

### 1. Portfolio Construction
```
"I want to invest $100,000 in RWA with low risk tolerance. 
Recommend a portfolio with 60% US treasuries and 40% other stable RWA assets."
```

### 2. Asset Comparison
```
"Compare the top 3 US Treasury-backed RWA tokens. 
Which one has the best yield-to-liquidity ratio?"
```

### 3. Market Research
```
"What are the current trends in RWA tokenization? 
Which asset classes are seeing the most growth?"
```

### 4. Risk Analysis
```
"Analyze the risks of investing in real estate RWA tokens 
in the current market environment."
```

### 5. Performance Review
```
"Show me the historical performance of commodity-backed RWA tokens 
over the past 12 months."
```

## 🔧 Configuration

The agent uses the same configuration as other RWA agents:

- **Model**: Azure OpenAI or DeepSeek (configurable in `config.py`)
- **Memory**: SQLite-based persistent memory
- **Storage**: Session storage for conversation history
- **Tools**: 
  - BaiduSearchTools (for market research)
  - WebsiteTools (for data collection from rwa.xyz)
  - ReasoningTools (for complex analysis)

## 📊 Data Sources

**Primary Source**: https://www.rwa.xyz/
- Comprehensive RWA project database
- Real-time market data and metrics
- Project fundamentals and documentation

**Secondary Sources** (via web search):
- RWA project websites and whitepapers
- Market analysis reports
- Regulatory updates
- News and announcements

## 🛡️ Risk Disclaimer

**IMPORTANT**: This agent provides **informational analysis only** and does NOT constitute:
- Professional financial advice
- Investment recommendations as absolute certainty
- Guarantees of returns or performance

**Users should:**
- Conduct their own due diligence
- Consult licensed financial advisors
- Understand that past performance does not guarantee future results
- Be aware of risks including loss of capital
- Comply with applicable laws and regulations

## 🔄 Integration with RWA Team

The Investment Agent can work standalone or as part of the RWA Team workflow:

```python
from agents.rwa_team import rwa_team

# The investment agent can be consulted after valuation
response = rwa_team.run("""
    I have completed asset valuation for my property.
    Now I want to understand how to invest in other RWA assets 
    to diversify my portfolio.
""")
```

## 📈 Performance Metrics

The agent analyzes investments using industry-standard metrics:

- **Returns**: TWR, MWR, Cumulative, Annualized
- **Risk**: Volatility, VaR, CVaR, Beta
- **Risk-Adjusted**: Sharpe Ratio, Sortino Ratio, Calmar Ratio
- **Drawdown**: Maximum Drawdown, Recovery Time
- **Correlation**: With other asset classes and indices

## 🆕 Future Enhancements

Planned features:
- [ ] Real-time portfolio tracking and monitoring
- [ ] Automated rebalancing alerts
- [ ] Integration with DeFi protocols for direct investment
- [ ] Advanced ML-based return prediction models
- [ ] Multi-language support for global investors
- [ ] Mobile-friendly report generation
- [ ] API access for programmatic integration

## 📞 Support

For questions or issues:
1. Check the main [PROJECT STRUCTURE](../PROJECT_STRUCTURE.md)
2. Review [RWA Workflow README](./RWA_WORKFLOW_README.md)
3. Examine the agent source code for detailed instructions

## 📄 License

Part of the DRWA.GURU project. See main repository for license information.

---

**Last Updated**: 2025-10-27  
**Version**: 1.0.0  
**Status**: Production Ready
