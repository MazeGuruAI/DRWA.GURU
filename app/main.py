"""Main Streamlit Application for the RWA Team"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import nest_asyncio
import asyncio
from agents.rwa_workflow import rwa_workflow, arun_rwa_workflow
from app.utils import display_messages, add_message, clear_chat_history, process_uploaded_files, create_agno_images_from_bytes

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Configure the page
st.set_page_config(
    page_title="Enhanced Agno Streamlit App",
    page_icon="🤖",
    layout="wide",
)


def main():
    # App header
    st.title("🏢 RWA 资产代币化平台")
    st.markdown("专业的RWA资产验证、估值和代币化服务平台")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ 系统设置")
        
        # Session controls
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            clear_chat_history()
            if "uploaded_files_data" in st.session_state:
                del st.session_state.uploaded_files_data
            st.rerun()
        
        # File clear button
        if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data:
            if st.button("📁 清空已上传文件", use_container_width=True, type="secondary"):
                del st.session_state.uploaded_files_data
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📁 文件上传")
        
        # File uploader for asset verification
        uploaded_files = st.file_uploader(
            "上传资产相关文件",
            type=["pdf", "jpg", "jpeg", "png", "doc", "docx"],
            accept_multiple_files=True,
            help="支持上传房产证、土地证等资产证明文件"
        )
        
        # Process and store uploaded files
        if uploaded_files:
            st.success(f"✅ 已上传 {len(uploaded_files)} 个文件")
            # Store files in session state
            st.session_state.uploaded_files_data = process_uploaded_files(uploaded_files)
            
            # Display uploaded files info
            st.markdown("**已上传文件：**")
            for file_info in st.session_state.uploaded_files_data:
                st.markdown(f"📄 {file_info['name']} ({file_info['size_mb']:.2f}MB)")
        
        st.markdown("---")
        st.markdown("### 💡 关于RWA工作流")
        st.markdown("""
        **工作流步骤：**
        - 🔍 **资产验证**: 验证资产文件真实性和合法性
        - 💰 **资产估值**: 进行专业资产市场评估
        - ⛓️ **代币部署**: 在以太坊Sepolia测试网部署ERC20代币
        
        **流程特点：**
        1. 智能条件判断：根据验证结果决定后续步骤
        2. 异步执行：高效处理多个代理调用
        3. 完整报告：生成详细的代币化报告
        4. 错误处理：失败时自动中止并给出原因
        """)
    
    # Initialize RWA workflow session
    # The workflow maintains its own state and memory across interactions
    
    # Initialize conversation history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = """
        👋 欢迎使用RWA资产代币化平台！
        
        我是专业的RWA工作流系统，可以帮助您：
        - 🔍 验证资产文件的真实性和合法性
        - 💰 进行专业的资产价值评估
        - ⛓️ 在区块链上发行资产代币
        
        **使用步骤：**
        1. 上传您的资产证明文件（如房产证、土地证等）
        2. 提供资产的详细信息（类型、位置、面积、年限等）
        3. 设置代币参数（名称、符号、供应量等）
        4. 系统将自动完成整个代币化流程
        
        请先上传您的资产证明文件，然后告诉我您的代币化需求。
        """
        add_message("assistant", welcome_message)
    
    # Display chat history
    display_messages()
    
    # Chat input
    if prompt := st.chat_input("请输入您的问题..."):
        # 检查是否有上传的文件并创建agno Image对象
        agno_images = []
        file_info = ""
        
        if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data:
            # 创建agno Image对象列表（用于图片文件）
            agno_images = create_agno_images_from_bytes(st.session_state.uploaded_files_data)
            
            # 创建File信息文本（用于所有文件）
            file_names = [f['name'] for f in st.session_state.uploaded_files_data]
            file_info = f"\n\n[已上传文件: {', '.join(file_names)}]"
            
            # 显示上传文件信息
            if agno_images:
                st.info(f"🖼️ 已上传 {len(agno_images)} 个图片文件，将进行视觉分析")
        
        # 构建完整消息
        complete_message = prompt + file_info
        
        # 将用户消息添加到聊天历史
        add_message("user", prompt)
        
        # 生成工作流响应（异步执行）
        with st.chat_message("assistant"):
            with st.spinner("RWA工作流正在处理您的请求..."):
                try:
                    # 准备 additional_data
                    additional_data = {
                        "has_files": "uploaded_files_data" in st.session_state and bool(st.session_state.uploaded_files_data),
                        "files_count": len(st.session_state.uploaded_files_data) if "uploaded_files_data" in st.session_state and st.session_state.uploaded_files_data else 0
                    }
                    
                    # 使用 asyncio 运行异步工作流
                    if agno_images:
                        # 如果有图片，同时传递消息和图片
                        response = asyncio.run(arun_rwa_workflow(
                            message=complete_message,
                            images=agno_images,
                            additional_data=additional_data
                        ))
                    else:
                        # 只有文本消息
                        response = asyncio.run(arun_rwa_workflow(
                            message=complete_message,
                            additional_data=additional_data
                        ))
                    
                    # 处理响应
                    if hasattr(response, 'content'):
                        response_content = response.content
                    else:
                        response_content = str(response)
                    
                    # 显示响应
                    st.markdown(response_content)
                    
                    # 将工作流响应添加到聊天历史
                    add_message("assistant", response_content)
                    
                    # 显示工作流执行状态（如果可用）
                    if hasattr(response, 'workflow_metrics') and response.workflow_metrics:
                        with st.expander("📊 工作流执行详情", expanded=False):
                            try:
                                metrics = response.workflow_metrics
                                if hasattr(metrics, 'total_steps'):
                                    st.success(f"✅ 工作流执行完成，共执行 {metrics.total_steps} 个步骤")
                                else:
                                    st.info("✅ 工作流执行完成")
                                
                                # 显示异步执行信息
                                st.info("⚡ 工作流采用异步执行方式，性能更高效")
                            except Exception as e:
                                st.info(f"工作流执行完成（详情获取失败：{e}）")
                    
                except Exception as e:
                    error_message = f"❌ 处理请求时出现错误: {str(e)}"
                    st.error(error_message)
                    add_message("assistant", error_message)


if __name__ == "__main__":
    main()