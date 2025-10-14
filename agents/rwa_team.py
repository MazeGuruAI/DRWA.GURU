"""Main Agno Agent for the Streamlit Application"""

from agno.agent import Agent
from agno.team import Team
from config import get_ai_model
from agents.asset_verification_agent import get_asset_verification_agent
from agents.asset_valuation_agent import get_asset_valuation_agent
from agents.onchain_notarization_agent import get_onchain_notarization_agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools

# 初始化内存和存储
memory_db = SqliteMemoryDb(table_name="rwa_team_memory", db_file="storage/rwa_memory.db")
memory = Memory(db=memory_db)
sessions = SqliteStorage(table_name="rwa_team_sessions", db_file="storage/rwa_sessions.db")

asset_valuation_agent = get_asset_valuation_agent()
asset_verification_agent = get_asset_verification_agent()
onchain_notarization_agent = get_onchain_notarization_agent()

rwa_team = Team(
    name="RWA Team",
    members=[asset_valuation_agent, asset_verification_agent, onchain_notarization_agent],
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
    你是一个专业的RWA（Real World Asset）资产代币化团队，负责帮助用户完成资产验证、估值和代币化的全流程服务。

    ### 团队成员及职责：
    - **asset_verification_agent**: 验证用户上传的资产文件（房产证、土地证等），验证其真实性、有效性和合法性，生成验证报告并记录资产关键信息
    - **asset_valuation_agent**: 基于资产验证信息和用户提供的详细信息（资产类型、地区、面积、使用年限等），通过市场数据查询对资产进行专业估值
    - **onchain_notarization_agent**: 根据估值结果和用户指定的代币参数（代币名称、符号、供应量等），在以太坊Sepolia测试网部署ERC20代币合约
    
    ### 核心工作流程 - 基于用户意图智能路由：
    
    **第一步：识别用户意图**
    - 仔细分析用户的请求，判断用户想要进行的操作：
      * 资产验证
      * 资产估值
      * 资产代币化（Token化）
      * 一般咨询或非相关问题
    
    **场景一：用户想要进行资产验证**
    1. 首先检查用户是否已上传文件或图片
    2. 如果**未上传**：
       - 友好提醒用户需要上传资产相关文件（如房产证、土地证的照片或扫描件）
       - 说明上传文件的重要性和要求
       - 等待用户上传后再继续
    3. 如果**已上传**：
       - 立即调用 asset_verification_agent 进行资产验证
       - 生成验证报告并输出给用户
       - 将验证结果存入记忆
       - 询问用户资产的详细信息：
         * 资产类型（住宅、商业地产、土地等）
         * 所在地区（省市区详细地址）
         * 建筑面积或土地面积
         * 使用年限/房龄
         * 其他相关信息
       - 如果验证发现资产信息造假或存在严重问题，立即中断流程并告知用户
    
    **场景二：用户想要进行资产估值**
    1. 首先检查资产是否已完成验证
    2. 如果**未完成验证**：
       - 告知用户必须先完成资产验证
       - 引导用户进入资产验证流程
    3. 如果**验证已通过**：
       - 确认已收集必要的资产信息（类型、地区、面积、年限等）
       - 如果信息不完整，补充询问缺失信息
       - 调用 asset_valuation_agent 进行资产估值
       - 输出估值报告（包含市场分析、价值评估、风险提示等）
       - 将估值结果存入记忆
       - 询问用户代币化相关信息：
         * 代币名称（Token Name）
         * 代币符号（Token Symbol）
         * 代币总供应量（Total Supply）
         * 代币精度（Decimals，默认18）
         * 其他代币参数
    
    **场景三：用户想要资产Token化（代币化）**
    1. 首先检查资产是否已完成估值
    2. 如果**未完成估值**：
       - 告知用户必须先完成资产估值
       - 引导用户按顺序完成验证和估值流程
    3. 如果**估值已完成**：
       - 确认已收集代币信息（名称、符号、供应量等）
       - 如果信息不完整，补充询问缺失信息
       - 基于估值报告和用户输入，生成完整的Token元数据
       - 调用 onchain_notarization_agent 在以太坊Sepolia测试网部署ERC20合约
       - 如果部署成功：
         * 返回合约地址
         * 返回交易哈希
         * 返回部署者地址
         * 提供区块链浏览器链接
         * 说明后续使用方式
       - 如果部署失败：
         * 详细说明失败原因
         * 提供可能的解决方案
         * 询问是否需要重试
    
    **场景四：非相关问题或一般咨询**
    - 直接使用AI能力回答用户问题
    - 不启动工作流程
    - 可以介绍RWA服务内容和流程

    ### 核心原则：
    1. **严格遵守顺序**：验证 → 估值 → 代币化，不可颠倒或跳过
    2. **状态检查优先**：每个环节开始前都要检查前置条件是否满足
    3. **智能意图识别**：准确判断用户当前想要执行的操作
    4. **友好引导**：缺少信息时主动询问，而不是直接拒绝
    5. **记忆管理**：及时存储各阶段的结果，便于后续调用
    6. **异常处理**：发现问题立即中断并给出清晰说明
    7. **用户体验**：保持专业、友好、高效的交互方式

    ### 输出质量标准：
    - **准确性**: 确保所有信息准确可靠，数据来源清晰
    - **完整性**: 提供全面详细的分析报告，不遗漏关键信息
    - **结构化**: 输出清晰易读，使用标题、列表、表格等格式
    - **实用性**: 提供可操作的建议和明确的下一步指引
    - **专业性**: 使用专业术语，体现金融和区块链领域专业水准

    ### 最佳实践：
    - 始终从用户意图出发，提供个性化服务
    - 充分利用每个团队成员的专业能力
    - 保持流程透明，让用户了解每个步骤的进展
    - 遇到错误或异常时，提供清晰的解释和解决方案
    - 定期确认用户是否理解，是否需要进一步说明
    
    """,
)


def main():
    """Test the RWA team with a sample asset verification and valuation workflow."""
    print("=" * 60)
    print("🏢 启动RWA团队测试")
    print("=" * 60)
    
    try:
        # 测试RWA团队的基本功能
        print("\n📋 团队成员信息:")
        print(f"- {asset_verification_agent.name}: 资产验证代理")
        print(f"- {asset_valuation_agent.name}: 资产估值代理")
        print(f"- {onchain_notarization_agent.name}: 区块链公证代理")
        
        print("\n🚀 开始RWA流程测试...")
        
        # 模拟用户请求
        user_request = """
        你好，我希望将我的房产进行代币化。我有一套位于北京市朝阳区的住宅房产，
        建筑面积120平米，房龄5年，希望能够进行资产验证、估值并发行代币。
        请指导我完成整个流程。
        """
        
        print(f"\n📝 用户请求: {user_request.strip()}")
        print("\n" + "="*60)
        print("🔄 RWA团队处理中...")
        print("="*60)
        
        # 调用RWA团队处理用户请求
        response = rwa_team.run(
            message=user_request
        )
        
        print("\n" + "="*60)
        print("✅ RWA团队处理完成")
        print("="*60)
        print("\n📊 处理结果:")
        print(response.content if hasattr(response, 'content') else str(response))
        
        # 显示会话状态
        if hasattr(rwa_team, 'session_state') and rwa_team.session_state:
            print("\n📈 会话状态:")
            for key, value in rwa_team.session_state.items():
                print(f"  {key}: {value}")
        
        return response
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {str(e)}")
        print("\n💡 可能的解决方案:")
        print("1. 检查环境变量配置 (AZURE_OPENAI_API_KEY 等)")
        print("2. 确认网络连接正常")
        print("3. 验证各代理组件是否正确初始化")
        
        # 尝试简单的团队信息测试
        print("\n🔍 尝试基础团队信息测试...")
        try:
            simple_response = rwa_team.run(
                message="请介绍一下RWA团队的功能和服务"
            )
            print("✅ 基础功能测试成功")
            print(f"响应: {simple_response.content if hasattr(simple_response, 'content') else str(simple_response)}")
        except Exception as simple_e:
            print(f"❌ 基础功能测试也失败: {str(simple_e)}")
        
        return None




if __name__ == "__main__":
    main()

