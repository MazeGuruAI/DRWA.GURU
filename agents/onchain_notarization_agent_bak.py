"""On-Chain Notarization Agent for Agno"""

from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from textwrap import dedent
from typing import Optional
import sys
import os
import asyncio
from config import get_ai_model
from agno.tools.mcp import MCPTools

# 以太坎MCP服务器配置
# 获取当前文件的绝对路径，然后构建正确的相对路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETHEREUM_MCP_COMMAND = f"python {os.path.join(current_dir, 'tools', 'web3_mcp_server.py')}"
ETHEREUM_FASTMCP_URL = "http://127.0.0.1:8000/mcp"


async def run_agent(message: str) -> None:
    """运行Web3 Agent并处理用户查询"""   
    # Initialize the MCP server with stable configuration
    try:
        print("📋 初始化MCP工具...")
        
        # 使用绝对路径配置（避免相对路径问题）
        mcp_command = "python C:\\Users\\zlf\\Documents\\rwaguru\\agno_streamlit_project\\tools\\web3_mcp_server.py"
        
        mcp_tools = MCPTools(
            command=mcp_command,
            env={},
            timeout_seconds=30,
        )
        
        print("📋 创建onchain_notarization_agent...")
        agent = get_onchain_notarization_agent(
            web3_mcp_tool=mcp_tools  # 传递MCP工具实例
        )
        
        print("📋 发送查询请求...")
        print("-" * 40)
        await agent.aprint_response(message, stream=True)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ 启动MCP工具时出错: {e}")
        import traceback
        traceback.print_exc()



def get_onchain_notarization_agent(web3_mcp_tool: MCPTools) -> Agent:
    """Create and return the on-chain notarization agent."""
    
    # 初始化共享的内存和存储（与RWA团队保持一致）
    memory_db = SqliteMemoryDb(table_name="rwa_memory", db_file="storage/rwa_memory.db")
    memory = Memory(db=memory_db)
    storage = SqliteStorage(table_name="rwa_sessions", db_file="storage/rwa_storage.db")

    tools = [ReasoningTools(), web3_mcp_tool]

    agent = Agent(
        name="On-Chain Notarization Agent",
        model=get_ai_model(model_type="azure"),
        tools=tools,
        description="You are an expert on-chain notarization agent that handles asset tokenization and blockchain deployment.",
        # 内存和存储配置
        memory=memory,
        storage=storage,
        instructions=dedent("""
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
        show_tool_calls=True,
        add_state_in_messages=True,
        # 历史与会话
        add_history_to_messages=True,
        num_history_runs=3,
        read_chat_history=True,

        # 其它
        markdown=True,
        add_datetime_to_instructions=True,
        stream_intermediate_steps=True
    )
    
    return agent


if __name__ == "__main__":
    # 测试run_agent方法
    try:
        print("🚀 启动Web3 Agent测试...")
        print("🎯 测试目标: 验证run_agent方法能否调用web3 MCP工具")
        print("🔧 测试查询: 获取以太坊Sepolia测试网gas费用")
        print("=" * 60)
        
        test_message = "请使用get_gas_price工具查询以太坊Sepolia测试网的当前gas费用，并返回具体的价格信息。"
        
        asyncio.run(run_agent(test_message))
        
        print("\n" + "=" * 60)
        print("✅ run_agent方法测试完成")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，Web3 Agent已停止")
    except Exception as exc:
        print(f"❌ 执行失败: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
