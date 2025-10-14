"""RWA Workflow for Asset Verification, Valuation and Tokenization

这个文件实现了一个完整的RWA（Real World Assets）资产代币化工作流，
包含资产验证、资产估值和链上公证三个核心步骤。

工作流程：
1. 资产验证 - 验证用户上传的资产文件的真实性和合法性
2. 资产估值 - 基于资产信息和市场数据进行价值评估
3. 代币部署 - 在以太坊Sepolia测试网部署ERC20代币合约

使用方式：
- 直接运行: python rwa_workflow.py
- 程序调用: from rwa_workflow import run_rwa_workflow, print_rwa_workflow

特点：
- 使用Agno Workflows 2.0框架
- 支持条件判断和流程控制
- 自动化验证和评估逻辑
- 完整的错误处理和状态管理
- 可扩展的代理系统
"""

import sys
import os
from agno.workflow.v2 import Step, Workflow, Condition
from agno.workflow.v2.types import StepInput, StepOutput
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from typing import List, AsyncIterator, Union
import re
import asyncio
from agno.tools.mcp import MCPTools

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


# ==================== 智能意图识别与路由函数 ====================

def intent_classifier(step_input: StepInput) -> StepOutput:
    """智能识别用户意图并路由到相应的处理流程"""
    message = (step_input.message or "").lower()
    
    # 意图识别关键词
    verification_keywords = ["验证", "上传", "文件", "房产证", "证书", "verify", "upload", "document"]
    valuation_keywords = ["估值", "评估", "价值", "价格", "valuation", "appraise", "estimate"]
    tokenization_keywords = ["代币", "token", "部署", "合约", "contract", "发行", "上链", "区块链"]
    consultation_keywords = ["什么", "如何", "怎么", "介绍", "说明", "help", "what", "how"]
    
    # 判断用户意图
    if any(keyword in message for keyword in verification_keywords):
        intent = "verification"
    elif any(keyword in message for keyword in valuation_keywords):
        intent = "valuation"
    elif any(keyword in message for keyword in tokenization_keywords):
        intent = "tokenization"
    elif any(keyword in message for keyword in consultation_keywords):
        intent = "consultation"
    else:
        # 默认意图 - 尝试理解用户需求
        intent = "general"
    
    # 通过输出传递意图
    return StepOutput(
        step_name="Intent Classifier",
        content=f"🎯 INTENT:{intent}",  # 通过content传递意图
        stop=False
    )


def route_by_intent(step_input: StepInput) -> StepOutput:
    """基于用户意图路由到相应的处理流程"""
    # 从上一步的输出提取意图
    previous_content = step_input.previous_step_content or ""
    intent = "general"
    
    if "INTENT:verification" in previous_content:
        intent = "verification"
    elif "INTENT:valuation" in previous_content:
        intent = "valuation"
    elif "INTENT:tokenization" in previous_content:
        intent = "tokenization"
    elif "INTENT:consultation" in previous_content:
        intent = "consultation"
    
    # 返回包含流程标识的输出
    if intent == "verification":
        return StepOutput(
            step_name="Intent Router",
            content="FLOW:verification",  # 通过content传递流程信息
            stop=False
        )
    elif intent == "valuation":
        return StepOutput(
            step_name="Intent Router",
            content="FLOW:valuation",
            stop=False
        )
    elif intent == "tokenization":
        return StepOutput(
            step_name="Intent Router",
            content="FLOW:tokenization",
            stop=False
        )
    elif intent == "consultation":
        return StepOutput(
            step_name="Intent Router",
            content="FLOW:consultation",
            stop=False
        )
    else:
        return StepOutput(
            step_name="Intent Router",
            content="FLOW:general",
            stop=False
        )


# ==================== 流程控制函数 ====================

def verification_flow_controller(step_input: StepInput) -> StepOutput:
    """资产验证流程控制器"""
    message = step_input.message or ""
    
    # 检查是否上传了文件
    file_indicators = ["上传", "文件", "图片", "照片", "房产证", "证书", "准备好了", "已上传"]
    has_file = any(indicator in message for indicator in file_indicators)
    
    if not has_file:
        return StepOutput(
            step_name="Verification Flow Controller",
            content="""📁 **资产验证流程**
            
请上传您的资产相关文件以开始验证流程：

📋 **需要上传的文件类型：**
• 房产证照片或扫描件
• 土地使用证
• 建筑许可证
• 其他相关产权证明文件

📝 **上传要求：**
• 文件格式：JPG、PNG、PDF
• 图片清晰，文字可读
• 确保证件信息完整

⏳ **请上传文件后回复"已上传文件"继续流程。**""",
            stop=True  # 等待用户上传文件
        )
    
    # 文件已上传，继续验证流程
    return StepOutput(
        step_name="Verification Flow Controller",
        content="✅ 检测到文件上传，正在启动资产验证流程...",
        stop=False
    )


def valuation_flow_controller(step_input: StepInput) -> StepOutput:
    """资产估值流程控制器"""
    message = step_input.message or ""
    
    # 检查是否提供了资产信息
    asset_info_indicators = ["面积", "地区", "年限", "房龄", "住宅", "商业", "类型", "位置"]
    has_asset_info = any(indicator in message for indicator in asset_info_indicators)
    
    if not has_asset_info:
        return StepOutput(
            step_name="Valuation Flow Controller",
            content="""⚠️ **资产估值流程**
            
请先确认资产验证已完成，并提供资产详细信息：

🔍 **如果尚未完成验证，请先进行资产验证。**

📊 **估值所需信息：**
• 资产类型和具体位置
• 建筑面积或土地面积
• 使用年限和当前状况
• 周边环境和配套设施

📝 **请提供完整的资产信息后继续估值流程。**""",
            stop=True
        )
    
    return StepOutput(
        step_name="Valuation Flow Controller",
        content="✅ 资产信息已收集，正在启动专业估值流程...",
        stop=False
    )


def tokenization_flow_controller(step_input: StepInput) -> StepOutput:
    """资产代币化流程控制器"""
    message = step_input.message or ""
    
    # 检查是否提供了代币信息
    token_info_indicators = ["代币名称", "代币符号", "供应量", "token", "symbol", "supply"]
    has_token_info = any(indicator in message for indicator in token_info_indicators)
    
    if not has_token_info:
        return StepOutput(
            step_name="Tokenization Flow Controller",
            content="""⚠️ **资产代币化流程**
            
请先确认资产估值已完成，并提供代币信息：

🔍 **如果尚未完成估值，请先进行资产估值。**

🪙 **代币化所需信息：**
• 代币名称和符号
• 代币总供应量
• 技术参数设置

📝 **请提供完整的代币信息后继续部署流程。**""",
            stop=True
        )
    
    return StepOutput(
        step_name="Tokenization Flow Controller",
        content="✅ 代币信息已收集，正在准备区块链部署...",
        stop=False
    )


def consultation_handler(step_input: StepInput) -> StepOutput:
    """处理一般咨询和非流程相关问题"""
    return StepOutput(
        step_name="Consultation Handler",
        content="""💡 **RWA资产代币化服务介绍**

🏠 **什么是RWA资产代币化？**
RWA（Real World Assets）资产代币化是将传统实物资产（如房地产、艺术品、商品等）转换为区块链上的数字代币的过程。

🔄 **我们的服务流程：**

1️⃣ **资产验证**
   • 上传资产相关证明文件
   • AI智能验证文件真实性
   • 生成详细验证报告

2️⃣ **资产估值**
   • 提供资产详细信息
   • 基于市场数据进行专业估值
   • 生成权威估值报告

3️⃣ **代币部署**
   • 设计代币参数
   • 在以太坊区块链部署ERC20合约
   • 获取代币合约地址

💪 **服务优势：**
• 全自动化流程，操作简单
• AI驱动的智能验证和估值
• 安全可靠的区块链部署
• 专业的技术支持

🚀 **开始使用：**
只需说"我要验证资产"、"我要估值"或"我要代币化"即可开始相应流程！

❓ 如有其他问题，请随时咨询。""",
        stop=False
    )


# ==================== 评估函数 ====================

def verification_evaluator(step_input: StepInput) -> StepOutput:
    """评估资产验证结果"""
    content = step_input.previous_step_content or ""
    
    # 检查验证结果
    failed_indicators = ["验证失败", "invalid", "伪造", "不合法", "无效", "failed", "fraud", "fake"]
    
    if any(indicator in content.lower() for indicator in failed_indicators):
        return StepOutput(
            step_name="Verification Evaluator",
            content=f"🚨 **资产验证失败，流程终止**\n\n{content}\n\n❌ 请检查上传的文件是否正确，或联系客服获取帮助。",
            stop=True
        )
    
    return StepOutput(
        step_name="Verification Evaluator",
        content=f"""✅ **资产验证通过**

{content}

📋 **请提供以下资产详细信息以进行估值：**

🏠 **基本信息：**
• 资产类型（住宅/商业地产/工业用地/其他）
• 所在地区（省市区详细地址）
• 建筑面积或土地面积（平方米）

⏰ **使用信息：**
• 使用年限或房龄
• 当前使用状况
• 装修情况

💡 **其他信息：**
• 周边配套设施
• 交通便利性
• 市场特殊因素

📝 **请提供上述信息后继续估值流程。**""",
        stop=False
    )


def valuation_evaluator(step_input: StepInput) -> StepOutput:
    """评估资产估值结果"""
    content = step_input.previous_step_content or ""
    
    return StepOutput(
        step_name="Valuation Evaluator",
        content=f"""✅ **资产估值完成**

{content}

🪙 **请提供代币化相关信息：**

🏷️ **基本代币信息：**
• 代币名称（如：Beijing Property Token）
• 代币符号（如：BPT，建议3-5个字符）
• 代币总供应量（建议基于资产估值设定）

⚙️ **技术参数：**
• 小数位数（默认18位，标准ERC20格式）
• 是否需要特殊功能（暂停、铸造等）

💡 **代币设计建议：**
• 供应量可基于资产价值按比例设定
• 符号应简洁易记且具有代表性
• 名称应反映资产特征和地理位置

📝 **请提供上述代币信息后开始部署流程。**""",
        stop=False
    )


def deployment_evaluator(step_input: StepInput) -> StepOutput:
    """评估代币部署结果并生成最终报告"""
    content = step_input.previous_step_content or ""
    
    # 提取以太坊地址和交易哈希
    eth_address_pattern = r'0x[a-fA-F0-9]{40}'
    tx_hash_pattern = r'0x[a-fA-F0-9]{64}'
    
    addresses = re.findall(eth_address_pattern, content)
    tx_hashes = re.findall(tx_hash_pattern, content)
    
    # 检查部署是否成功
    failure_indicators = ["部署失败", "deployment failed", "错误", "error", "failed"]
    
    if any(indicator in content.lower() for indicator in failure_indicators):
        return StepOutput(
            step_name="Deployment Evaluator",
            content=f"""❌ **代币部署失败**

{content}

🔧 **可能的解决方案：**
• 检查网络连接和以太坊节点状态
• 确认账户余额是否足够支付Gas费
• 验证代币参数是否正确
• 检查智能合约代码是否有问题

🔄 **您可以：**
• 修改代币参数后重新尝试
• 检查错误信息并调整配置
• 联系技术支持获取帮助

📞 如需帮助，请提供完整的错误信息。""",
            stop=True
        )
    
    # 生成成功报告
    success_report = f"""🎉 **RWA资产代币化流程成功完成！**

{'='*60}
📋 **完整流程报告**
{'='*60}

{content}

🔗 **区块链信息：**
• 网络：以太坊Sepolia测试网
• 合约标准：ERC20"""
    
    if addresses:
        success_report += f"\n• 合约地址：{addresses[0]}"
        success_report += f"\n• 区块链浏览器：https://sepolia.etherscan.io/address/{addresses[0]}"
    
    if tx_hashes:
        success_report += f"\n• 部署交易：{tx_hashes[0]}"
        success_report += f"\n• 交易详情：https://sepolia.etherscan.io/tx/{tx_hashes[0]}"
    
    success_report += """\n
✅ **后续操作指南：**
• 可在MetaMask等钱包中添加代币合约地址查看余额
• 使用区块链浏览器查看合约详情和交易记录
• 可通过智能合约接口进行代币转账等操作

🏆 **恭喜！您的资产已成功代币化并部署到区块链上。**"""
    
    return StepOutput(
        step_name="Deployment Evaluator",
        content=success_report,
        stop=False
    )


# ==================== 条件判断函数 ====================

def is_verification_flow(step_input: StepInput) -> bool:
    """判断是否进入验证流程"""
    previous_content = step_input.previous_step_content or ""
    return "FLOW:verification" in previous_content


def is_valuation_flow(step_input: StepInput) -> bool:
    """判断是否进入估值流程"""
    previous_content = step_input.previous_step_content or ""
    return "FLOW:valuation" in previous_content
# ==================== 定义智能工作流步骤 ====================

# 步骤1：用户意图识别
intent_classification_step = Step(
    name="Intent Classification",
    executor=intent_classifier,
    description="识别用户意图并路由到相应流程"
)

# 步骤2：意图路由器
intent_routing_step = Step(
    name="Intent Routing",
    executor=route_by_intent,
    description="根据用户意图路由到相应的处理流程"
)

# ==================== 资产验证流程步骤 ====================
# 步骤3a：验证流程控制
verification_control_step = Step(
    name="Verification Control",
    executor=verification_flow_controller,
    description="控制资产验证流程，检查文件上传状态"
)

# 步骤4a：资产验证执行
asset_verification_step = Step(
    name="Asset Verification",
    agent=asset_verification_agent,
    description="验证用户上传的资产文件的真实性和合法性"
)

# 步骤5a：验证结果评估
verification_evaluation_step = Step(
    name="Verification Evaluation",
    executor=verification_evaluator,
    description="评估资产验证结果"
)

# ==================== 资产估值流程步骤 ====================
# 步骤3b：估值流程控制
valuation_control_step = Step(
    name="Valuation Control",
    executor=valuation_flow_controller,
    description="控制资产估值流程，检查验证状态和资产信息"
)

# 步骤4b：资产估值执行
asset_valuation_step = Step(
    name="Asset Valuation", 
    agent=asset_valuation_agent,
    description="基于资产信息进行市场估值"
)

# 步骤5b：估值结果评估
valuation_evaluation_step = Step(
    name="Valuation Evaluation",
    executor=valuation_evaluator,
    description="评估资产估值结果"
)

# ==================== 代币化流程步骤 ====================
# 步骤3c：代币化流程控制
tokenization_control_step = Step(
    name="Tokenization Control",
    executor=tokenization_flow_controller,
    description="控制资产代币化流程，检查估值状态和代币信息"
)

# 定义异步Step函数
async def async_onchain_step(step_input: StepInput) -> StepOutput:
    response = await onchain_notarization_agent.arun(step_input.message)
    return StepOutput(content=response.content)

# 步骤4c：代币部署执行
token_deployment_step = Step(
    name="Token Deployment",
    executor=async_onchain_step,
    description="在以太坊Sepolia测试网部署ERC20代币合约"
)

# 步骤5c：部署结果评估
deployment_evaluation_step = Step(
    name="Deployment Evaluation",
    executor=deployment_evaluator,
    description="评估代币部署结果并生成最终报告"
)

# ==================== 咨询流程步骤 ====================
# 步骤3d：咨询处理
consultation_step = Step(
    name="Consultation",
    executor=consultation_handler,
    description="处理一般咨询和非流程相关问题"
)


# ==================== 创建智能RWA工作流 ====================
rwa_workflow = Workflow(
    name="Smart RWA Asset Tokenization Workflow",
    description="智能化的RWA资产代币化工作流，支持意图识别和条件路由",
    storage=storage,
    workflow_session_state={},  # 初始化共享状态
    steps=[
        # 阶段1：意图识别与路由
        intent_classification_step,
        intent_routing_step,
        
        # 阶段2：条件性执行 - 资产验证流程
        Condition(
            name="Verification Flow",
            evaluator=is_verification_flow,
            steps=[
                verification_control_step,
                asset_verification_step,
                verification_evaluation_step,
            ]
        ),
        
        # 阶段3：条件性执行 - 资产估值流程
        Condition(
            name="Valuation Flow",
            evaluator=is_valuation_flow,
            steps=[
                valuation_control_step,
                asset_valuation_step,
                valuation_evaluation_step,
            ]
        ),
        
        # 阶段4：条件性执行 - 代币化流程
        Condition(
            name="Tokenization Flow",
            evaluator=lambda step_input: "FLOW:tokenization" in (step_input.previous_step_content or ""),
            steps=[
                tokenization_control_step,
                token_deployment_step,
                deployment_evaluation_step,
            ]
        ),
        
        # 阶段5：条件性执行 - 咨询流程
        Condition(
            name="Consultation Flow",
            evaluator=lambda step_input: "FLOW:consultation" in (step_input.previous_step_content or ""),
            steps=[consultation_step]
        ),
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


async def main():
    """测试智能RWA工作流（异步执行）"""
    print("🧠 智能RWA资产代币化工作流测试")
    print("=" * 60)
    
    try:
        # 测试用例1：资产验证意图
        print("\n📝 测试用例1：资产验证意图")
        print("-" * 40)
        
        verification_message = "我想验证我的房产证，已经上传了文件"
        
        response1 = await rwa_workflow.arun(message=verification_message)
        print(f"验证流程响应：\n{response1.content}")
        
        # 测试用例2：资产估值意图
        print("\n📊 测试用例2：资产估值意图")
        print("-" * 40)
        
        valuation_message = "我要估值我的房产，类型是住宅，位于北京朝阳区，面积120平米，房龄5年"
        
        response2 = await rwa_workflow.arun(message=valuation_message)
        print(f"估值流程响应：\n{response2.content}")
        
        # 测试用例3：代币化意图
        print("\n🪙 测试用例3：代币化意图")
        print("-" * 40)
        
        tokenization_message = "我要进行代币化，代币名称是Beijing Property Token，符号BPT，供应量1000000"
        
        response3 = await rwa_workflow.arun(message=tokenization_message)
        print(f"代币化流程响应：\n{response3.content}")
        
        # 测试用例4：一般咨询
        print("\n❓ 测试用例4：一般咨询")
        print("-" * 40)
        
        consultation_message = "什么是RWA资产代币化？你们能提供什么服务？"
        
        response4 = await rwa_workflow.arun(message=consultation_message)
        print(f"咨询服务响应：\n{response4.content}")
        
        print("\n✅ 智能RWA工作流测试完成")
        
        # 显示使用示例
        print("\n" + "="*60)
        print("📚 使用示例")
        print("="*60)
        print("""
1. 直接运行测试：
   python rwa_workflow.py

2. 在代码中使用（同步方式）：
   from rwa_workflow import run_rwa_workflow
   
   # 运行工作流
   response = run_rwa_workflow("我要验证我的房产...")

3. 在代码中使用（异步方式 - 推荐）：
   import asyncio
   from rwa_workflow import arun_rwa_workflow
   
   async def process():
       response = await arun_rwa_workflow("我要估值我的资产...")
       return response
   
   response = asyncio.run(process())

4. 在Streamlit中集成：
   import streamlit as st
   import asyncio
   from rwa_workflow import arun_rwa_workflow
   
   if st.button("开始RWA流程"):
       response = asyncio.run(arun_rwa_workflow(user_input))
       st.write(response.content)

5. 智能意图识别示例：
   - "我要验证资产" → 自动进入验证流程
   - "我要估值" → 自动进入估值流程
   - "我要代币化" → 自动进入代币化流程
   - "什么是RWA" → 自动提供咨询服务
        """)
        
    except Exception as e:
        print(f"❌ 工作流测试失败：{str(e)}")
        print("\n🔧 可能的解决方案：")
        print("1. 检查环境变量配置 (AZURE_OPENAI_API_KEY 等)")
        print("2. 确认网络连接正常")
        print("3. 验证各代理组件是否正确初始化")
        return False
    
    return True


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())