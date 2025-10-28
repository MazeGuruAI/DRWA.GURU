"""Quick verification script for RWA Compliance Agent setup"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_status(check_name, passed, message=""):
    """Print check status"""
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if message:
        print(f"   {message}")

def verify_setup():
    """Verify RWA Compliance Agent setup"""
    
    print_header("RWA Compliance Agent - Setup Verification")
    
    total_checks = 0
    passed_checks = 0
    
    # Check 1: Python version
    total_checks += 1
    python_version = sys.version_info
    is_python_ok = python_version >= (3, 8)
    print_status(
        "Python Version",
        is_python_ok,
        f"Python {python_version.major}.{python_version.minor}.{python_version.micro}" +
        (" (OK)" if is_python_ok else " (需要 3.8+)")
    )
    if is_python_ok:
        passed_checks += 1
    
    # Check 2: Required files exist
    print("\n" + "-" * 80)
    print("检查文件...")
    print("-" * 80)
    
    required_files = [
        ("agents/rwa_compliance_agent.py", "核心Agent"),
        ("agents/download_compliance_docs.py", "文档下载脚本"),
        ("agents/test_compliance_agent.py", "测试脚本"),
        ("agents/rwa_team.py", "RWA团队（已更新）"),
        ("agents/RWA_COMPLIANCE_AGENT_README.md", "完整文档"),
        ("agents/COMPLIANCE_QUICK_START.md", "快速指南"),
        ("knowledge/compliance/README.md", "知识库说明"),
        ("config.py", "配置文件"),
        ("requirements.txt", "依赖列表"),
    ]
    
    for file_path, description in required_files:
        total_checks += 1
        exists = os.path.exists(file_path)
        print_status(f"{description}: {file_path}", exists)
        if exists:
            passed_checks += 1
    
    # Check 3: Knowledge directory
    print("\n" + "-" * 80)
    print("检查目录...")
    print("-" * 80)
    
    total_checks += 1
    knowledge_dir = Path("knowledge/compliance")
    dir_exists = knowledge_dir.exists() and knowledge_dir.is_dir()
    print_status("Knowledge目录", dir_exists, str(knowledge_dir))
    if dir_exists:
        passed_checks += 1
    
    # Check 4: PDF documents (optional)
    print("\n" + "-" * 80)
    print("检查PDF文档（可选）...")
    print("-" * 80)
    
    pdf_files = [
        "knowledge/compliance/hk_sfc_tokenisation.pdf",
        "knowledge/compliance/uk_fca_crypto.pdf",
        "knowledge/compliance/oecd_tokenisation.pdf",
    ]
    
    pdf_count = 0
    for pdf_path in pdf_files:
        exists = os.path.exists(pdf_path)
        if exists:
            size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            print_status(f"PDF文档", exists, f"{pdf_path} ({size_mb:.2f} MB)")
            pdf_count += 1
        else:
            print_status(f"PDF文档", exists, f"{pdf_path} (未下载)")
    
    if pdf_count == 0:
        print("\n⚠️ 提示: 没有找到PDF文档。运行 'python agents/download_compliance_docs.py' 来下载。")
    elif pdf_count < len(pdf_files):
        print(f"\n⚠️ 提示: 只找到 {pdf_count}/{len(pdf_files)} 个PDF文档。")
    else:
        print(f"\n✅ 所有 {pdf_count} 个PDF文档已就绪！")
    
    # Check 5: Environment variables
    print("\n" + "-" * 80)
    print("检查环境变量...")
    print("-" * 80)
    
    # Try to load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ 已加载 .env 文件")
    except ImportError:
        print("⚠️ python-dotenv 未安装（可选）")
    
    env_vars = [
        ("AZURE_OPENAI_API_KEY", "Azure OpenAI API密钥"),
        ("AZURE_OPENAI_ENDPOINT", "Azure OpenAI Endpoint"),
        ("AZURE_EMBEDDER_OPENAI_API_KEY", "Azure Embedder API密钥"),
        ("DEEPSEEK_API_KEY", "DeepSeek API密钥（备选）"),
    ]
    
    env_count = 0
    for var_name, description in env_vars:
        total_checks += 1
        is_set = bool(os.getenv(var_name))
        if is_set:
            print_status(description, True, f"{var_name} = ***已设置***")
            passed_checks += 1
            env_count += 1
        else:
            print_status(description, False, f"{var_name} = 未设置")
    
    if env_count == 0:
        print("\n❌ 错误: 没有配置任何API密钥！Agent无法运行。")
        print("   请在 .env 文件中配置 Azure OpenAI 或 DeepSeek 的API密钥。")
    
    # Check 6: Python dependencies
    print("\n" + "-" * 80)
    print("检查Python依赖...")
    print("-" * 80)
    
    dependencies = [
        ("agno", "Agno框架"),
        ("openai", "OpenAI SDK"),
        ("streamlit", "Streamlit"),
        ("requests", "Requests库"),
    ]
    
    for module_name, description in dependencies:
        total_checks += 1
        try:
            __import__(module_name)
            print_status(description, True, f"{module_name} 已安装")
            passed_checks += 1
        except ImportError:
            print_status(description, False, f"{module_name} 未安装")
    
    # Check 7: Try to import agent (optional advanced check)
    print("\n" + "-" * 80)
    print("检查Agent导入...")
    print("-" * 80)
    
    total_checks += 1
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from agents.rwa_compliance_agent import get_rwa_compliance_agent
        print_status("Agent导入", True, "rwa_compliance_agent.get_rwa_compliance_agent")
        passed_checks += 1
    except Exception as e:
        print_status("Agent导入", False, f"错误: {str(e)}")
    
    # Summary
    print_header("验证总结")
    
    print(f"\n总检查项: {total_checks}")
    print(f"✅ 通过: {passed_checks}")
    print(f"❌ 失败: {total_checks - passed_checks}")
    print(f"成功率: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 完美！所有检查都通过了！")
        print("   您可以开始使用 RWA Compliance Agent 了。")
        print("\n下一步:")
        print("   1. 下载PDF文档: python agents/download_compliance_docs.py")
        print("   2. 运行测试: python agents/test_compliance_agent.py --quick")
        print("   3. 启动Agent: python agents/rwa_compliance_agent.py")
    elif passed_checks >= total_checks * 0.7:
        print("\n✅ 良好！大部分检查通过。")
        print("   请解决上述警告和错误项。")
        print("\n建议:")
        print("   1. 配置缺失的环境变量")
        print("   2. 安装缺失的Python依赖: pip install -r requirements.txt")
        print("   3. 下载PDF文档: python agents/download_compliance_docs.py")
    else:
        print("\n❌ 需要修复！许多检查失败。")
        print("\n必须执行:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 配置 .env 文件中的API密钥")
        print("   3. 确保所有必需文件存在")
    
    print("\n" + "=" * 80)
    print("查看详细文档: agents/COMPLIANCE_QUICK_START.md")
    print("=" * 80 + "\n")
    
    return passed_checks == total_checks


if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)
