"""测试合规咨询和投资咨询代理集成"""

import asyncio
from agents.rwa_workflow import arun_rwa_workflow

async def test_compliance_agent():
    """测试合规咨询代理"""
    print("=" * 80)
    print("测试 1: 合规咨询代理")
    print("=" * 80)
    
    query = "我想在美国进行房地产代币化，需要遵守哪些SEC的规定？"
    print(f"\n用户查询: {query}")
    print("-" * 80)
    
    try:
        response = await arun_rwa_workflow(message=query)
        print("\n✅ 合规代理响应:")
        print(response.content if hasattr(response, 'content') else str(response))
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
    
    print("=" * 80)


async def test_investment_agent():
    """测试投资咨询代理"""
    print("\n" + "=" * 80)
    print("测试 2: 投资咨询代理")
    print("=" * 80)
    
    query = """
    我是保守型投资者，有10万美元可投资RWA资产。
    风险承受能力低，偏好稳定收益。
    请帮我分析RWA市场并推荐合适的投资组合。
    """
    print(f"\n用户查询: {query.strip()}")
    print("-" * 80)
    
    try:
        response = await arun_rwa_workflow(message=query)
        print("\n✅ 投资代理响应:")
        print(response.content if hasattr(response, 'content') else str(response))
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
    
    print("=" * 80)


async def test_welcome_message():
    """测试欢迎消息"""
    print("\n" + "=" * 80)
    print("测试 3: 欢迎消息")
    print("=" * 80)
    
    query = "你好"
    print(f"\n用户查询: {query}")
    print("-" * 80)
    
    try:
        response = await arun_rwa_workflow(message=query)
        print("\n✅ 系统响应:")
        print(response.content if hasattr(response, 'content') else str(response))
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
    
    print("=" * 80)


async def main():
    """运行所有测试"""
    print("\n")
    print("🚀 开始测试RWA合规咨询和投资咨询代理集成")
    print("\n")
    
    # 测试欢迎消息
    await test_welcome_message()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试合规代理
    await test_compliance_agent()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试投资代理
    await test_investment_agent()
    
    print("\n")
    print("✅ 所有测试完成!")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
