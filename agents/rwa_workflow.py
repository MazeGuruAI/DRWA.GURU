import os
import sys
from typing import List
from agno.agent import Agent
from agno.workflow.v2 import Workflow, Step, Router
from agno.workflow.v2.types import StepInput, StepOutput
from agno.tools.mcp import MCPTools
from config import get_ai_model
from agents.asset_verification_agent import get_asset_verification_agent
from agents.asset_valuation_agent import get_asset_valuation_agent
from agents.onchain_notarization_agent import get_onchain_notarization_agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETHEREUM_MCP_COMMAND = f"python {os.path.join(current_dir, 'tools', 'web3_mcp_server.py')}"
web3_mcp_tool = MCPTools(
    command=ETHEREUM_MCP_COMMAND,
    env={},
    timeout_seconds=6000,
)

# Dynamically import agents and configuration
try:
    from config import get_ai_model
    from agents.asset_verification_agent import get_asset_verification_agent
    from agents.asset_valuation_agent import get_asset_valuation_agent
    from agents.onchain_notarization_agent import get_onchain_notarization_agent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you run this script from the project root directory")
    sys.exit(1)


# Initialize shared memory and storage
memory_db = SqliteMemoryDb(table_name="rwa_workflow_memory", db_file="storage/rwa_workflow.db")
memory = Memory(db=memory_db)
storage = SqliteStorage(table_name="rwa_workflow_sessions", db_file="storage/rwa_workflow.db")

# Initialize each agent
asset_verification_agent = get_asset_verification_agent()
asset_valuation_agent = get_asset_valuation_agent()
onchain_notarization_agent = get_onchain_notarization_agent(web3_mcp_tool)

# ===== Router function: Identify user intent =====

def intent_router(step_input: StepInput) -> List[Step]:
    """Route to different processing steps based on user intent"""
    user_input = (step_input.message or "").lower()
    
    # Check if files are uploaded (multiple detection methods)
    has_files_in_message = "[Uploaded Files:" in (step_input.message or "")
    has_files_in_additional = False
    if step_input.additional_data:
        has_files_in_additional = step_input.additional_data.get("has_files", False)
    
    # Also check if images parameter is passed
    has_images = hasattr(step_input, 'images') and step_input.images
    
    # Consider files present if detected by any method
    has_any_files = has_files_in_message or has_files_in_additional or has_images
    
    # Check session state (detect from additional_data or message)
    session_state = step_input.additional_data.get("session_state", {}) if step_input.additional_data else {}
    verification_done = session_state.get("verification_done", False)
    valuation_done = session_state.get("valuation_done", False)
    
    # Intent 1: Asset verification
    if any(keyword in user_input for keyword in ["verify", "verification", "upload", "certificate", "proof", "验证", "上传", "房产证", "证明"]):
        if not has_any_files:
            return [Step(
                name="Remind to upload files",
                executor=lambda si: StepOutput(
                    content="Please first upload your asset files (such as property certificates, land certificates, etc.) in the left sidebar, then say 'verify assets'.",
                    success=False
                )
            )]
        else:
            return [Step(
                name="Asset Verification",
                agent=asset_verification_agent,
                description="Verify asset files and generate report"
            )]
    
    # Intent 2: Asset valuation
    elif any(keyword in user_input for keyword in ["valuation", "evaluate", "value", "worth", "price", "估值", "评估", "价值", "多少钱"]):
        if not verification_done:
            return [Step(
                name="Remind to verify first",
                executor=lambda si: StepOutput(
                    content="Please complete asset verification first before proceeding with valuation.",
                    success=False
                )
            )]
        else:
            return [Step(
                name="Asset Valuation",
                agent=asset_valuation_agent,
                description="Conduct market valuation of the asset"
            )]
    
    # Intent 3: Asset tokenization
    elif any(keyword in user_input for keyword in ["token", "tokenize", "tokenization", "deploy", "blockchain", "on-chain", "代币", "上链", "部署"]):
        if not valuation_done:
            return [Step(
                name="Remind to valuate first",
                executor=lambda si: StepOutput(
                    content="Please complete asset valuation first before proceeding with tokenization.",
                    success=False
                )
            )]
        else:
            return [Step(
                name="On-chain Notarization",
                agent=onchain_notarization_agent,
                description="Deploy ERC20 token on Sepolia testnet"
            )]
    
    # Default: Guide user
    else:
        return [Step(
            name="User Guidance",
            executor=lambda si: StepOutput(
                content="""Welcome to RWA Asset Tokenization Service!
                
Please select the service you need:
1. Asset Verification - Upload asset files for verification
2. Asset Valuation - Provide asset information for market evaluation
3. Asset Tokenization - Tokenize assets on-chain and generate tokens

Please tell me which step you would like to proceed with.""",
                success=True
            )
        )]

# ===== Create RWA Workflow =====

rwa_workflow = Workflow(
    name="RWA Asset Tokenization Workflow",
    description="Implement complete process of asset verification, valuation and on-chain tokenization",
    steps=[
        Router(
            name="Intent Recognition Router",
            selector=intent_router,
            choices=[
                Step(name="Asset Verification", agent=asset_verification_agent),
                Step(name="Asset Valuation", agent=asset_valuation_agent),
                Step(name="On-chain Notarization", agent=onchain_notarization_agent),
            ],
            description="Route to corresponding processing flow based on user intent"
        )
    ],
    
    debug_mode=True
)

def run_rwa_workflow(message: str, **kwargs):
    """Convenience function to run RWA workflow (synchronous)"""
    return rwa_workflow.run(message=message, **kwargs)


async def arun_rwa_workflow(message: str, **kwargs):
    """Convenience function to run RWA workflow (asynchronous)"""
    return await rwa_workflow.arun(message=message, **kwargs)


def print_rwa_workflow(message: str, **kwargs):
    """Convenience function to print RWA workflow response (synchronous)"""
    return rwa_workflow.print_response(message=message, **kwargs)


async def aprint_rwa_workflow(message: str, **kwargs):
    """Convenience function to print RWA workflow response (asynchronous)"""
    return await rwa_workflow.aprint_response(message=message, **kwargs)