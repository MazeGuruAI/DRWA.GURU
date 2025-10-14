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

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETHEREUM_MCP_COMMAND = f"python {os.path.join(current_dir, 'tools', 'web3_mcp_server.py')}"
web3_mcp_tool = MCPTools(
    command=ETHEREUM_MCP_COMMAND,
    env={},
    timeout_seconds=6000,
)

# 动态导入代理和配置
try:
    from config import get_ai_model
    from agents.asset_verification_agent import get_asset_verification_agent
    from agents.asset_valuation_agent import get_asset_valuation_agent
    from agents.onchain_notarization_agent import get_onchain_notarization_agent
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


# 初始化共享的内存和存储
memory_db = SqliteMemoryDb(table_name="rwa_workflow_memory", db_file="storage/rwa_workflow.db")
memory = Memory(db=memory_db)
storage = SqliteStorage(table_name="rwa_workflow_sessions", db_file="storage/rwa_workflow.db")

# 初始化各个代理
asset_verification_agent = get_asset_verification_agent()
asset_valuation_agent = get_asset_valuation_agent()
onchain_notarization_agent = get_onchain_notarization_agent(web3_mcp_tool)

# ===== 路由函数：识别用户意图 =====

def intent_router(step_input: StepInput) -> List[Step]:
    """根据用户意图路由到不同的处理步骤"""
    user_input = (step_input.message or "").lower()
    
    # 检查是否有文件上传（多种检测方式）
    has_files_in_message = "[已上传文件:" in (step_input.message or "")
    has_files_in_additional = False
    if step_input.additional_data:
        has_files_in_additional = step_input.additional_data.get("has_files", False)
    
    # 也检查是否传递了images参数
    has_images = hasattr(step_input, 'images') and step_input.images
    
    # 只要一种方式检测到文件就认为有文件
    has_any_files = has_files_in_message or has_files_in_additional or has_images
    
    # 检查会话状态（从 additional_data 或消息中检测）
    session_state = step_input.additional_data.get("session_state", {}) if step_input.additional_data else {}
    verification_done = session_state.get("verification_done", False)
    valuation_done = session_state.get("valuation_done", False)
    
    # 意图1：资产验证
    if any(keyword in user_input for keyword in ["验证", "上传", "房产证", "证明"]):
        if not has_any_files:
            return [Step(
                name="提醒上传文件",
                executor=lambda si: StepOutput(
                    content="请先在左侧边栏上传您的资产文件（如房产证、土地证等），然后再说'验证资产'。",
                    success=False
                )
            )]
        else:
            return [Step(
                name="资产验证",
                agent=asset_verification_agent,
                description="验证资产文件并生成报告"
            )]
    
    # 意图2：资产估值
    elif any(keyword in user_input for keyword in ["估值", "评估", "价值", "多少钱"]):
        if not verification_done:
            return [Step(
                name="提醒先验证",
                executor=lambda si: StepOutput(
                    content="请先完成资产验证后再进行估值。",
                    success=False
                )
            )]
        else:
            return [Step(
                name="资产估值",
                agent=asset_valuation_agent,
                description="对资产进行市场估值"
            )]
    
    # 意图3：资产token化
    elif any(keyword in user_input for keyword in ["token", "代币", "上链", "部署"]):
        if not valuation_done:
            return [Step(
                name="提醒先估值",
                executor=lambda si: StepOutput(
                    content="请先完成资产估值后再进行token化。",
                    success=False
                )
            )]
        else:
            return [Step(
                name="链上公证",
                agent=onchain_notarization_agent,
                description="在Sepolia测试网部署ERC20代币"
            )]
    
    # 默认：引导用户
    else:
        return [Step(
            name="用户引导",
            executor=lambda si: StepOutput(
                content="""欢迎使用RWA资产token化服务！
                
请选择您需要的服务：
1. 资产验证 - 上传资产文件进行验证
2. 资产估值 - 提供资产信息进行市场评估
3. 资产token化 - 将资产上链并生成代币

请告诉我您想要进行哪一步操作。""",
                success=True
            )
        )]

# ===== 创建RWA工作流 =====

rwa_workflow = Workflow(
    name="RWA Asset Tokenization Workflow",
    description="实现资产验证、估值和链上token化的完整流程",
    steps=[
        Router(
            name="意图识别路由",
            selector=intent_router,
            choices=[
                Step(name="资产验证", agent=asset_verification_agent),
                Step(name="资产估值", agent=asset_valuation_agent),
                Step(name="链上公证", agent=onchain_notarization_agent),
            ],
            description="根据用户意图路由到相应的处理流程"
        )
    ],
    
    debug_mode=True
)

def run_rwa_workflow(message: str, **kwargs):
    """运行RWA工作流的便捷函数（同步方式）"""
    return rwa_workflow.run(message=message, **kwargs)


async def arun_rwa_workflow(message: str, **kwargs):
    """运行RWA工作流的便捷函数（异步方式）"""
    return await rwa_workflow.arun(message=message, **kwargs)


def print_rwa_workflow(message: str, **kwargs):
    """打印RWA工作流响应的便捷函数（同步方式）"""
    return rwa_workflow.print_response(message=message, **kwargs)


async def aprint_rwa_workflow(message: str, **kwargs):
    """打印RWA工作流响应的便捷函数（异步方式）"""
    return await rwa_workflow.aprint_response(message=message, **kwargs)