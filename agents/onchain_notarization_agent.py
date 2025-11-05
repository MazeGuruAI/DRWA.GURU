import warnings
from typing import Optional
import asyncio
import os
import sys
from pathlib import Path
import contextlib
import threading
from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent

# Add parent directory to system path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage

from agno.agent import Agent
from agno.tools.mcp import MCPTools

from config import get_ai_model

# Suppress RuntimeWarning and specific async cleanup warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*async.*generator.*')

# Ethereum MCP server configuration
ETHEREUM_MCP_COMMAND = "python tools/web3_mcp_server.py"
ETHEREUM_FASTMCP_URL = "http://127.0.0.1:8000/mcp"

'''
async def run_agent(message: str) -> None:
    """Run Web3 Agent and process user queries"""
    mcp_tools = None
    agent_completed = False
    
    try:
        # Initialize the MCP server with longer timeout for startup
        mcp_tools_config = MCPTools(
            command=ETHEREUM_MCP_COMMAND,
            timeout_seconds=30  # Increase timeout for MCP server startup
        )
        async with mcp_tools_config as mcp_tools:
            agent = get_onchain_notarization_agent(
                prefix_name="interactive",
                mcp_tools=mcp_tools  # Pass MCP tool instance
            )
            await agent.aprint_response(message, stream=True)
            agent_completed = True
            # Give a brief moment for any pending operations
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        # Suppress cleanup errors after successful completion
        if agent_completed and ("TaskGroup" in str(e) or "cancel scope" in str(e)):
            # This is likely a cleanup error after successful execution, ignore it
            pass
        else:
            print(f"❌ Execution failed: {e}", file=sys.stderr)
            raise

async def run_agent(message: str) -> None:
    """Run Web3 Agent and process user queries"""
    try:
        # Initialize the MCP server with timeout
        async with MCPTools(
            transport="streamable-http", 
            url=ETHEREUM_FASTMCP_URL,
            timeout_seconds=30
        ) as mcp_tools:
            agent = get_web3_agent(
                prefix_name="interactive",
                mcp_tools=mcp_tools  # Pass MCP tool instance
            )
            await agent.aprint_response(message, stream=True)
    except Exception as e:
        print(f"❌ Execution failed: {e}", file=sys.stderr)
        raise

'''

def get_onchain_notarization_agent() -> Agent:
    """Create on-chain notarization Agent instance"""
    # Initialize shared memory and storage (consistent with RWA team)
    memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")
    
    # Use passed MCP tools or create new ones
    ethereum_mcp_tool = MCPTools(
        command=ETHEREUM_MCP_COMMAND,
        timeout_seconds=60  # Increase timeout for server startup
    )

    return Agent(
        name="Onchain Notarization Agent",
        model=get_ai_model(model_type="azure"),
        tools=[ethereum_mcp_tool],

        instructions=dedent("""\
You are an expert on-chain notarization agent. Your role is to handle the process of asset tokenization and blockchain deployment.
            
Notarization Process:    
1. Tokenization Scheme Determination:
* Token name
* Token symbol
* Total supply
            
3. Blockchain Deployment:
- Use web3 MCP tools(deploy_erc20_contract) to deploy smart contracts
- Execute deployment transactions
- Monitor transaction status and confirm successful deployment
- Verify contract addresses and deployment details
- Generate a comprehensive notarization report
            
Available Tools:
- ReasoningTools: For logical analysis and decision making
- `deploy_erc20_contract`: Deploy new ERC20 contract
- `transfer_erc20_tokens`: Transfer tokens using ERC20 contract
- `check_erc20_balance`: Query ERC20 token balance
- `get_network_status`: Get network status and wallet information
- `get_eth_balance`: Query address ETH/native token balance
- `get_transaction_count`: Query address transaction count (nonce)
- `get_gas_price`: Get current Gas price
- `get_block_number`: Query latest block number
- `get_transaction`: Query transaction details
- `get_network_info`: Get network configuration and status information
﻿
Important Guidelines:
- Use web3 MCP tools for blockchain interactions
- Monitor transaction status and handle errors appropriately
- Generate detailed reports with all relevant information
- Be thorough but concise in your analysis
- Clearly distinguish between facts and recommendations
- All output content is in English
- If you're unsure about something, state your uncertainty rather than making assumptions
        """),
        add_state_in_messages=True,
        # History and session
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,

        # Other
        markdown=True,
        add_datetime_to_instructions=True,
        debug_mode=True,
        stream_intermediate_steps=True
    )



'''
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Web3 blockchain data query Agent")
    parser.add_argument("--prompt", type=str, required=True, help="User query or task description")
    parser.add_argument("--prefix", type=str, default="cli", help="Agent prefix name")
    parser.add_argument("--model_id", type=str, default=None, help="Model ID")
    parser.add_argument("--model_type", type=str, default=None, help="Model type (e.g., azure, deepseek)")
    parser.add_argument("--user_id", type=str, default="cli_user", help="User ID")
    parser.add_argument("--session_id", type=str, default=None, help="Session ID")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    try:
        print(f"🚀 Starting Web3 Agent, query: {args.prompt}")
        asyncio.run(run_agent(args.prompt))
        print("\n✅ Agent execution completed")
    except KeyboardInterrupt:
        print("\n👋 User interrupted, Web3 Agent stopped")
    except Exception as exc:
        # Check if it's just a cleanup error
        if "TaskGroup" in str(exc) or "cancel scope" in str(exc):
            print("\n✅ Agent execution completed (cleanup warning ignored)")
        else:
            print(f"❌ Execution failed: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

'''





