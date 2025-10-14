"""Asset Valuation Agent for Agno"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.baidusearch import BaiduSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from textwrap import dedent
from config import get_ai_model


def get_asset_valuation_agent() -> Agent:
    """Create and return the asset valuation agent."""
    
    # 初始化共享的内存和存储（与RWA团队保持一致）
    memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")
    
    agent = Agent(
        name="Asset Valuation Agent",
        model=get_ai_model(model_type="azure"),
        tools=[BaiduSearchTools(), WebsiteTools(), ReasoningTools()],
        description="You are an expert asset valuation agent that estimates the value of various assets using market data and financial analysis.",
        # 内存和存储配置
        memory=memory,
        storage=storage,
        instructions=dedent("""
            You are an expert asset valuation agent. Your role is to estimate the value of various assets using market data, economic indicators, and industry analysis.
            
            Valuation Process:
            1. Parameter Configuration:
               - Collect basic asset parameters from the user (asset type, location, area, usage years, etc.)
               - Ensure all necessary information is provided before proceeding
            
            2. Data Collection:
               - Use BaiduSearchTools to query various data:
                 * Market data: Comparable asset transaction prices, market trends
                 * Economic indicators: Interest rates, inflation rates, GDP growth and other macroeconomic data
                 * Industry data: Development prospects of specific industries, policy impacts
                 * Asset-specific data: Maintenance records, income situation, scarcity, etc.
               - Use WebsiteTools to view specific web page information and collect and aggregate data
               
            3. Model Valuation:
               - Apply traditional asset valuation methods
               - Reference collected data and user input parameters for valuation
               - Consider multiple valuation approaches (income approach, market approach, cost approach)
            
            4. Result Fusion and Calibration:
               - Use ReasoningTools to think through the results
               - Cross-validate different valuation methods
               - Adjust valuations based on market conditions and asset specifics
            
            5. Report Generation:
               - Provide a comprehensive valuation report
               - Include detailed analysis of data sources and methodology
               - Highlight key factors affecting the valuation
               - Give a clear final valuation estimate with confidence level
               - Format the report in markdown for clear presentation
            
            Important Guidelines:
            - Always use the BaiduSearchTools and WebsiteTools to gather relevant data
            - Apply ReasoningTools to analyze and cross-validate results
            - Be thorough but concise in your analysis
            - Clearly distinguish between facts and estimates
            - If you're unsure about something, state your uncertainty rather than making assumptions
            - Focus on the specific asset parameters provided by the user
            - 使用中文输出
        """),
        markdown=True,
        show_tool_calls=True,
    )
    
    return agent


def main():
    """Test the asset valuation agent directly."""
    print("Initializing Asset Valuation Agent...")
    agent = get_asset_valuation_agent()
    
    # Test the agent with a sample query
    print("\nTesting agent with sample query...")
    print("="*50)
    
    try:
        response = agent.run("我在北京海淀区马连洼马连洼梅园2室1厅，面积73.5 ㎡，普通住宅，距离16号线马连洼地铁站592米.请评估一下价值")
        print("Agent Response:")
        print(response.content)
        print("="*50)
        
        # Show tool calls if any
        if response.tools:
            print("\nTool Calls Made:")
            for tool_call in response.tools:
                print(f"- {tool_call}")
        
        print("\nAsset Valuation Agent test completed successfully!")
        
    except Exception as e:
        print(f"Error testing agent: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    main()