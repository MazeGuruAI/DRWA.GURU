from typing import Optional
import asyncio
import os
import sys
from pathlib import Path
import contextlib
import threading
from concurrent.futures import ThreadPoolExecutor
from textwrap import dedent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage

from agno.agent import Agent
from agno.tools.mcp import MCPTools

from config import get_ai_model

# 以太坊MCP服务器配置
ETHEREUM_MCP_COMMAND = "python tools/web3_mcp_server.py"
ETHEREUM_FASTMCP_URL = "http://127.0.0.1:8000/mcp"


async def run_agent(message: str) -> None:
    """运行Web3 Agent并处理用户查询"""
    # Initialize the MCP server
    async with (
        MCPTools(ETHEREUM_MCP_COMMAND) as mcp_tools,  # Supply the command to run the MCP server
    ):
        agent = get_onchain_notarization_agent(
            prefix_name="interactive",
            mcp_tools=mcp_tools  # 传递MCP工具实例
        )
        await agent.aprint_response(message, stream=True)
'''
async def run_agent(message: str) -> None:
    """运行Web3 Agent并处理用户查询"""
    try:
        # Initialize the MCP server with timeout
        async with MCPTools(
            transport="streamable-http", 
            url=ETHEREUM_FASTMCP_URL,
            timeout_seconds=30
        ) as mcp_tools:
            agent = get_web3_agent(
                prefix_name="interactive",
                mcp_tools=mcp_tools  # 传递MCP工具实例
            )
            await agent.aprint_response(message, stream=True)
    except Exception as e:
        print(f"❌ 执行失败: {e}", file=sys.stderr)
        raise

'''

def get_onchain_notarization_agent(
    mcp_tools: MCPTools = None,
) -> Agent:
    """创建链上存证Agent实例"""
    # 初始化共享的内存和存储（与RWA团队保持一致）
    # memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    # memory = Memory(db=memory_db)
    # storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")
    # 使用传入的MCP工具或创建新的
    ethereum_mcp_tool = mcp_tools or MCPTools(command=ETHEREUM_MCP_COMMAND)

    return Agent(
        model=get_ai_model(model_type="azure"),
        tools=[ethereum_mcp_tool],

        instructions=dedent("""\
You are an expert on-chain notarization agent. Your role is to handle the process of asset tokenization and blockchain deployment.
            
Notarization Process:    
1. Tokenization Scheme Determination:
- Collect token parameters from the user:
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
- `deploy_erc20_contract`: 部署新的ERC20合约
- `transfer_erc20_tokens`: 使用ERC20合约转账代币
- `check_erc20_balance`: 查询ERC20代币余额
- `get_network_status`: 获取网络状态和钱包信息
- `get_eth_balance`: 查询地址ETH/原生代币余额
- `get_transaction_count`: 查询地址交易计数（nonce）
- `get_gas_price`: 获取当前Gas价格
- `get_block_number`: 查询最新区块号
- `get_transaction`: 查询交易详情
- `get_network_info`: 获取网络配置和状态信息
﻿
Important Guidelines:
- Always validate asset valuations before proceeding with tokenization
- Ensure all user-provided token parameters are complete and valid
- Use web3 MCP tools for blockchain interactions
- Monitor transaction status and handle errors appropriately
- Generate detailed reports with all relevant information
- Be thorough but concise in your analysis
- Clearly distinguish between facts and recommendations
- If you're unsure about something, state your uncertainty rather than making assumptions
        """),
        add_state_in_messages=True,
        # 历史与会话
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,

        # 其它
        markdown=True,
        add_datetime_to_instructions=True,
        debug_mode=True,
        stream_intermediate_steps=True
    )



'''
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行Web3区块链数据查询Agent")
    parser.add_argument("--prompt", type=str, required=True, help="用户查询或任务描述")
    parser.add_argument("--prefix", type=str, default="cli", help="Agent前缀名")
    parser.add_argument("--model_id", type=str, default=None, help="模型ID")
    parser.add_argument("--model_type", type=str, default=None, help="模型类型（如azure、deepseek）")
    parser.add_argument("--user_id", type=str, default="cli_user", help="用户ID")
    parser.add_argument("--session_id", type=str, default=None, help="会话ID")
    parser.add_argument("--debug", action="store_true", help="开启调试模式")

    args = parser.parse_args()

    try:
        print(f"🚀 启动Web3 Agent，查询：{args.prompt}")
        asyncio.run(run_agent(args.prompt))
    except KeyboardInterrupt:
        print("\n👋 用户中断，Web3 Agent已停止")
    except Exception as exc:
        print(f"❌ 执行失败: {exc}", file=sys.stderr)
        sys.exit(1)
'''
