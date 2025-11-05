"""Main Agno Agent for the Streamlit Application"""

from agno.agent import Agent
from agno.team import Team
from config import get_ai_model
from agents.asset_verification_agent import get_asset_verification_agent
from agents.asset_valuation_agent import get_asset_valuation_agent
from agents.onchain_notarization_agent import get_onchain_notarization_agent
from agents.rwa_compliance_agent import get_rwa_compliance_agent
from agents.rwa_investment_agent import get_rwa_investment_agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools

# Initialize memory and storage
memory_db = SqliteMemoryDb(table_name="rwa_team_memory", db_file="storage/rwa_memory.db")
memory = Memory(db=memory_db)
sessions = SqliteStorage(table_name="rwa_team_sessions", db_file="storage/rwa_sessions.db")

asset_valuation_agent = get_asset_valuation_agent()
asset_verification_agent = get_asset_verification_agent()
onchain_notarization_agent = get_onchain_notarization_agent()
compliance_agent = get_rwa_compliance_agent()
investment_agent = get_rwa_investment_agent()

rwa_team = Team(
    name="RWA Team",
    members=[asset_valuation_agent, asset_verification_agent, onchain_notarization_agent, compliance_agent,investment_agent],
    model=get_ai_model(model_type="azure"),
    mode="route",
    tools=[ReasoningTools()],

    # ==================== 团队协作配置 ====================
    show_members_responses=True,  # 显示成员响应
    
    # ==================== 会话管理 ====================
    memory=memory,
    storage=sessions,
    
    # ==================== 调试和监控 ====================
    debug_mode=True,

    instructions="""
    You are a professional RWA (Real World Asset) asset tokenization team, responsible for helping users complete the full process of asset verification, valuation and tokenization and help user to invest RWA assets.

    ### Team Members and Responsibilities:
    - **asset_verification_agent**: Verify asset (property certificates, land certificates, etc.), verify their authenticity, validity and legality, generate verification reports and record key asset information
    - **asset_valuation_agent**: Based on asset verification information and detailed information provided by users (asset type, region, area, years of use, etc.), conduct professional valuation of assets through market data queries
    - **onchain_notarization_agent**: According to valuation results ,generate token parameters (token name, symbol, supply, etc.), deploy ERC20 token contracts on Ethereum Sepolia testnet
    - **compliance_agent**: Provide regulatory and compliance guidance for RWA tokenization across multiple jurisdictions, including securities laws, licensing requirements, KYC/AML obligations, and latest regulatory news
    - **investment_agent**: Provide comprehensive RWA investment analysis, portfolio recommendations, asset comparisons, risk assessments, and market research based on data from RWA platforms
    
    ### Core Workflow - Smart Routing Based on User Intent:
    
    **Step 1: Identify User Intent**
    - call ReasoningTools to carefully analyze user requests to determine the operation the user wants to perform:
      * Asset verification
      * Asset valuation
      * Asset tokenization (Token)
      * Compliance and regulatory consultation
      * RWA investment analysis and portfolio recommendations
      * General consultation or unrelated questions
    
    If **User wants asset verification**
    1. First check if the user want to verification ,then check if the user has uploaded files or images
    2. If **not uploaded**:
       - Kindly remind users that they need to upload asset-related files (such as photos or scans of property certificates, land certificates)
       - Explain the importance and requirements of uploading files
       - Wait for user to upload before continuing
    3. If **uploaded**:
       - Immediately call asset_verification_agent for asset verification
       - Generate verification report and output to user
       - Store verification results in memory
       - If verification finds asset information is fake or there are serious problems, immediately abort the process and inform the user
    
    If **User wants asset valuation**
    1. First check if the asset has been verified(from session or memory)
    2. If **not verified**:
       - Inform the user that asset verification must be completed first
       - Guide the user through the asset verification process
    3. If **verification passed**:
       - Call asset_valuation_agent for asset valuation
       - Output valuation report (including market analysis, value assessment, risk warnings, etc.)
       - Store valuation results in memory
    
    If **User wants asset tokenization**
    1. First check if asset valuation has been completed
    2. If **not valuated**:
       - Inform the user that asset valuation must be completed first
       - Guide the user through verification and valuation process in order
    3. If **valuation completed**:
       - Retrieve user specified token information, if not specified, generate complete Token metadata(name, symbol, supply, etc.) based on valuation report 
       - Call onchain_notarization_agent to deploy ERC20 contract on Ethereum Sepolia testnet
       - If deployment succeeds:
         * Return contract address
         * Return transaction hash
         * Return deployer address
         * Provide blockchain explorer link
         * Explain how to use it
       - If deployment fails:
         * Explain the reason for failure in detail
         * Provide possible solutions
         * Ask if you need to retry
       - Store results in memory
    
    If **User wants compliance and regulatory guidance**
    1. Identify the specific jurisdiction(s) or regulatory topic
    2. Call compliance_agent to provide regulatory guidance:
       - Securities law requirements
       - Licensing and registration obligations
       - KYC/AML compliance requirements
       - Cross-border regulatory considerations
       - Latest regulatory news and updates
    3. If user is planning tokenization:
       - Integrate compliance guidance with verification/valuation results
       - Ensure tokenization plan meets regulatory requirements
       - Warn about potential compliance risks
    4. Provide references to specific regulations and official sources

    If **User wants RWA investment analysis**
    1. Identify user's investment requirements:
       - Investment amount and budget
       - Risk tolerance (conservative, moderate, aggressive)
       - Investment horizon and liquidity needs
       - Preferred asset types or sectors
    2. Call investment_agent to provide analysis:
       - Collect latest RWA market data from platforms like https://app.rwa.xyz/
       - Classify and compare available RWA assets
       - Analyze historical performance and risk metrics
       - Generate customized portfolio recommendations
       - Provide comprehensive investment report with actionable insights
    3. Integrate with other agents if needed:
       - Coordinate with compliance_agent for regulatory considerations
       - Reference verification/valuation results if user has own assets
    4. Deliver clear, data-driven recommendations with risk disclosures
    
    If **Unrelated questions or general consultation**
    - Answer user questions directly using AI capabilities
    - Can introduce RWA service content and process

    ### Core Principles:
    1. Prioritize judging user intent rather than whether to upload files, even when uploading files, call different agents based on user intent
    2. **Status check first**: Check if prerequisites are met before each step
    3. **Smart intent recognition**: Accurately determine the operation the user currently wants to perform
    4. **Friendly guidance**: Actively ask when information is missing instead of directly refusing
    5. **Memory management**: Store results from each stage in time for subsequent calls
    6. **Exception handling**: Immediately abort and give clear explanation when problems are found
    7. **User experience**: Maintain professional, friendly, and efficient interaction

    ### Output Quality Standards:
    - **Accuracy**: Ensure all information is accurate and reliable, with clear data sources
    - **Completeness**: Provide comprehensive and detailed analysis reports without missing key information
    - **Structured**: Clear and easy-to-read output using titles, lists, tables and other formats
    - **Practicality**: Provide actionable suggestions and clear next steps
    - **Professionalism**: Use professional terminology to demonstrate professional standards in finance and blockchain

    ### Best Practices:
    - Always start from user intent and provide personalized service
    - Make full use of each team member's professional capabilities
    - Keep the process transparent and let users know the progress of each step
    - When errors or exceptions occur, provide clear explanations and solutions
    - Regularly confirm whether the user understands and needs further explanation
    
    """,
)

'''
def main():
    """Test the RWA team with a sample asset verification and valuation workflow."""
    print("=" * 60)
    print("🏢 启动RWA团队测试")
    print("=" * 60)
    
    try:
        # 测试RWA团队的基本功能
        print("\n📋 团队成员信息:")
        print("- {}: Asset Verification Agent".format(asset_verification_agent.name))
        print("- {}: Asset Valuation Agent".format(asset_valuation_agent.name))
        print("- {}: Blockchain Notarization Agent".format(onchain_notarization_agent.name))
        print("- {}: Compliance and Regulation Agent".format(compliance_agent.name))
        
        print("\n🚀 Starting RWA process test...")
        
        # Simulate user request
        user_request = """
        Hello, I would like to tokenize my property. I have a residential property located in Chaoyang District, Beijing,
        with a building area of 120 square meters and a property age of 5 years. I would like to have the asset verified, valued and issue tokens.
        Please guide me through the entire process.
        """
        
        print(f"\n📝 User request: {user_request.strip()}")
        print("\n" + "="*60)
        print("🔄 RWA team processing...")
        print("="*60)
        
        # Call RWA team to handle user request
        response = rwa_team.run(
            message=user_request
        )
        
        print("\n" + "="*60)
        print("✅ RWA team processing completed")
        print("="*60)
        print("\n📊 Processing result:")
        print(response.content if hasattr(response, 'content') else str(response))
        
        # Display session state
        if hasattr(rwa_team, 'session_state') and rwa_team.session_state:
            print("\n📈 Session state:")
            for key, value in rwa_team.session_state.items():
                print(f"  {key}: {value}")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error occurred during execution: {str(e)}")
        print("\n💡 Possible solutions:")
        print("1. Check environment variable configuration (AZURE_OPENAI_API_KEY, etc.)")
        print("2. Confirm network connection is normal")
        print("3. Verify all agent components are correctly initialized")
        
        # Try simple team information test
        print("\n🔍 Attempting basic team information test...")
        try:
            simple_response = rwa_team.run(
                message="Please introduce the functions and services of the RWA team"
            )
            print("✅ Basic function test succeeded")
            print(f"Response: {simple_response.content if hasattr(simple_response, 'content') else str(simple_response)}")
        except Exception as simple_e:
            print(f"❌ Basic function test also failed: {str(simple_e)}")
        
        return None




if __name__ == "__main__":
    main()

'''






