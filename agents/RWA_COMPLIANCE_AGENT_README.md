# RWA Compliance and Regulation Agent

## 概述

RWA合规监管Agent是一个基于Agno框架的智能代理，专门为RWA（真实世界资产）代币化项目提供全球监管合规指导。该Agent整合了多个国家和地区的监管政策文档，并实时获取最新的RWA行业新闻，为用户提供准确、及时的合规建议。

## 核心功能

### 1. 多司法管辖区监管知识

Agent覆盖以下主要地区的RWA代币化监管框架：

- **美国 (US)**: SEC证券法规、Howey测试、注册豁免等
- **香港 (Hong Kong)**: SFC代币化框架、VASP牌照制度
- **中国大陆 (China)**: 加密货币禁令、区块链服务提供商注册要求
- **阿联酋 (UAE)**: ADGM和DFSA数字资产监管框架
- **欧盟 (EU)**: MiCA（加密资产市场监管）综合框架
- **英国 (UK)**: FCA加密资产监管、金融推广制度
- **瑞士 (Switzerland)**: FINMA ICO指南、DLT法案
- **国际标准**: FATF、IOSCO、OECD等国际组织指南

### 2. RAG知识库

Agent使用检索增强生成(RAG)技术，整合以下知识源：

**Web知识源**:
- US SEC关于加密和代币化的声明
- 中国加密监管专家指南
- 阿联酋ADGM数字资产规则手册
- 欧盟MiCA监管框架
- 瑞士FINMA金融科技发展

**PDF文档源**:
- 香港SFC代币化研讨会文件
- 英国FCA加密资产监管咨询文件
- OECD资产代币化报告

### 3. 实时新闻集成

Agent自动抓取最新的RWA行业新闻和监管动态：
- 数据源：https://app.rwa.xyz/news
- 监控内容：新监管政策、执法行动、主要项目启动、市场趋势

### 4. 合规咨询能力

- **监管分析**: 解读特定司法管辖区的监管要求
- **合规评估**: 评估代币化项目的合规状态
- **风险识别**: 识别潜在的监管和合规风险
- **最佳实践**: 提供实用的合规策略和建议
- **跨境合规**: 处理多司法管辖区的复杂合规场景

## 安装和配置

### 1. 环境要求

```bash
# Python 3.8+
# 已安装的依赖（见requirements.txt）
agno
openai
streamlit
requests
```

### 2. 下载监管文档

运行文档下载脚本以获取PDF监管文档：

```bash
# 确保安装了requests库
pip install requests

# 运行下载脚本
cd agents
python download_compliance_docs.py
```

该脚本会自动：
- 创建 `./knowledge/compliance/` 目录
- 下载香港SFC、英国FCA、OECD等监管文档
- 验证下载完整性

**注意**: 某些PDF可能需要手动下载，如遇到下载失败：
1. 访问脚本中提供的原始URL
2. 手动下载PDF文件
3. 放置到 `./knowledge/compliance/` 目录下

### 3. 配置API密钥

在项目根目录的 `.env` 文件中配置：

```bash
# Azure OpenAI (用于主模型)
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_VERSION=2024-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Embedder (用于RAG知识库)
AZURE_EMBEDDER_OPENAI_API_KEY=your_embedder_api_key
AZURE_EMBEDDER_OPENAI_ENDPOINT=your_embedder_endpoint
AZURE_EMBEDDER_OPENAI_API_VERSION=2024-07-01-preview
AZURE_EMBEDDER_DEPLOYMENT=text-embedding-ada-002

# 或使用DeepSeek (备选)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_ENDPOINT=https://api.lkeap.cloud.tencent.com/v1
DEEPSEEK_DEPLOYMENT_NAME=deepseek-v3.1
```

## 使用方法

### 方式1: 独立运行

直接运行合规Agent进行交互式咨询：

```bash
cd agents
python rwa_compliance_agent.py
```

这将启动交互式模式，您可以直接提问监管和合规问题。

### 方式2: 在代码中集成

```python
from agents.rwa_compliance_agent import get_rwa_compliance_agent

# 创建合规Agent实例
compliance_agent = get_rwa_compliance_agent()

# 提问监管问题
response = compliance_agent.run("""
    我想在美国代币化商业地产。
    需要遵守哪些SEC监管要求？
    有哪些注册豁免可用？
""")

print(response.content)
```

### 方式3: 集成到RWA团队

将合规Agent添加到现有的RWA团队中：

```python
from agents.rwa_compliance_agent import get_rwa_compliance_agent
from agno.team import Team

# 创建合规Agent
compliance_agent = get_rwa_compliance_agent()

# 添加到RWA团队
rwa_team = Team(
    name="RWA Team",
    members=[
        asset_verification_agent,
        asset_valuation_agent,
        onchain_notarization_agent,
        compliance_agent  # 新增合规Agent
    ],
    # ... 其他配置
)
```

## 使用示例

### 示例1: 特定司法管辖区咨询

```python
query = """
我计划在香港推出一个代币化房地产平台。
需要获得哪些SFC牌照？
对专业投资者和零售投资者有什么不同的要求？
"""
response = compliance_agent.run(query)
```

### 示例2: 多司法管辖区比较

```python
query = """
比较香港、新加坡和瑞士对RWA代币化的监管环境。
哪个司法管辖区最适合启动代币化债券平台？
"""
response = compliance_agent.run(query)
```

### 示例3: 最新监管动态

```python
query = """
最近有哪些RWA代币化的监管新政策？
请检查 https://app.rwa.xyz/news 的最新新闻。
有没有影响欧盟MiCA实施的重要更新？
"""
response = compliance_agent.run(query)
```

### 示例4: 合规流程指导

```python
query = """
我是一家美国初创公司，想要代币化私募股权基金。
请提供完整的合规流程路线图，包括：
1. 法律结构设计
2. SEC注册或豁免选择
3. KYC/AML要求
4. 持续合规义务
"""
response = compliance_agent.run(query)
```

## Agent工作流程

当用户提问时，Agent按以下步骤处理：

1. **识别司法管辖区**: 确定用户关心的国家/地区
2. **搜索知识库**: 查询RAG知识库中的相关监管政策
3. **获取最新新闻**: 从RWA新闻源获取最新监管动态
4. **综合分析**: 结合知识库和新闻进行深度分析
5. **提供指导**: 以清晰、结构化的方式提供合规建议

## 知识库内容

### Web知识源

| 地区 | 来源 | 内容 |
|------|------|------|
| 美国 | SEC官网 | 加密资产证券监管声明 |
| 中国 | CMS Law | 中国加密监管专家指南 |
| 阿联酋 | ADGM | 数字资产监管规则手册 |
| 欧盟 | ESMA | MiCA监管框架 |
| 瑞士 | FINMA | 金融科技监管发展 |

### PDF文档源

| 文档名称 | 地区 | 描述 |
|----------|------|------|
| hk_sfc_tokenisation.pdf | 香港 | SFC代币化研讨会指南 |
| uk_fca_crypto.pdf | 英国 | FCA加密资产监管咨询 |
| oecd_tokenisation.pdf | 国际 | OECD资产代币化报告 |

## 输出格式

Agent的响应使用Markdown格式，包含：

- **清晰的章节标题**: 组织良好的信息结构
- **要点列表**: 关键监管要求和合规义务
- **表格**: 对比不同司法管辖区或监管选项
- **引用来源**: 具体的法规、指南和官方文件引用
- **行动建议**: 可执行的下一步操作

## 注意事项

⚠️ **重要免责声明**:

1. **非法律建议**: 本Agent提供的信息仅供参考，不构成法律建议
2. **咨询专业人士**: 在做出任何合规决策前，请咨询持牌律师和合规顾问
3. **监管变化**: 监管环境持续演变，请务必核实最新要求
4. **司法管辖区差异**: 不同地区的法律要求可能存在显著差异
5. **尽职调查**: 用户应自行进行充分的尽职调查和风险评估

## 故障排除

### 知识库加载失败

如果遇到"Could not load knowledge base"警告：

1. 检查PDF文件是否存在于 `./knowledge/compliance/` 目录
2. 运行 `download_compliance_docs.py` 下载缺失的文档
3. 验证embedder API配置是否正确

### Web知识源访问失败

某些监管网站可能有访问限制：

1. 检查网络连接和代理设置
2. 某些URL可能需要VPN访问
3. 可以手动访问URL获取信息后提问

### API配额限制

如遇到API配额问题：

1. 检查Azure OpenAI或DeepSeek的配额限制
2. 考虑使用rate limiting或缓存机制
3. 升级API订阅计划

## 扩展和定制

### 添加新的监管文档

1. 将PDF文件放入 `./knowledge/compliance/` 目录
2. 在 `rwa_compliance_agent.py` 的 `pdf_sources` 列表中添加配置
3. 重新运行Agent以加载新知识

### 添加新的Web知识源

在 `rwa_compliance_agent.py` 的 `web_sources` 列表中添加：

```python
{
    "name": "新监管机构名称",
    "url": "https://regulator.example.com/guidance",
    "description": "监管指南描述"
}
```

### 自定义Agent指令

修改 `instructions` 参数以调整Agent的行为和输出风格。

## 相关文档

- [Agno框架文档](https://docs.agno.com)
- [RWA投资Agent](./RWA_INVESTMENT_AGENT_README.md)
- [RWA工作流](./RWA_WORKFLOW_README.md)

## 技术栈

- **框架**: Agno (Multi-Agent AI Framework)
- **LLM**: Azure OpenAI GPT-4 / DeepSeek V3.1
- **Embeddings**: Azure OpenAI text-embedding-ada-002
- **向量数据库**: LanceDB
- **知识库**: PDFKnowledgeBase, WebsiteKnowledgeBase
- **工具**: BaiduSearchTools, WebsiteTools, ReasoningTools

## 许可证

本项目遵循与主项目相同的许可证。

## 联系和支持

如有问题或建议，请：
1. 提交GitHub Issue
2. 参考项目README.md
3. 查看相关文档和示例

---

**最后更新**: 2025-10-28
**版本**: 1.0.0
**作者**: DRWA.GURU Team
