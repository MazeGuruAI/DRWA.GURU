"""Main Streamlit Application for the RWA Team"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import nest_asyncio
from agents.rwa_team import rwa_team
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
        st.markdown("### 💡 关于RWA团队")
        st.markdown("""
        **团队成员：**
        - 🔍 **资产验证代理**: 验证资产文件真实性
        - 💰 **资产估值代理**: 进行专业资产评估
        - ⛓️ **区块链公证代理**: 部署ERC20代币
        
        **服务流程：**
        1. 上传资产证明文件
        2. 资产验证和合规检查
        3. 市场评估和定价
        4. 代币化和链上发行
        """)
    
    # Initialize RWA team (no need to store in session state as it's a singleton)
    # RWA team will maintain its own conversation context
    
    # Initialize conversation history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = """
        👋 欢迎使用RWA资产代币化平台！
        
        我是专业的RWA团队，可以帮助您：
        - 🔍 验证资产文件的真实性和合法性
        - 💰 进行专业的资产价值评估
        - ⛓️ 在区块链上发行资产代币
        
        请先上传您的资产证明文件（如房产证、土地证等），然后告诉我您希望进行资产代币化的需求。
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
        
        # 生成团队响应
        with st.chat_message("assistant"):
            with st.spinner("RWA团队正在处理您的请求..."):
                try:
                    # 调用RWA团队，传递消息和图片
                    if agno_images:
                        # 如果有图片，同时传递消息和图片
                        response = rwa_team.run(
                            message=complete_message,
                            images=agno_images
                        )
                    else:
                        # 只有文本消息
                        response = rwa_team.run(message=complete_message)
                    
                    # 处理响应
                    if hasattr(response, 'content'):
                        response_content = response.content
                    else:
                        response_content = str(response)
                    
                    # 显示响应
                    st.markdown(response_content)
                    
                    # 将团队响应添加到聊天历史
                    add_message("assistant", response_content)
                    
                except Exception as e:
                    error_message = f"❌ 处理请求时出现错误: {str(e)}"
                    st.error(error_message)
                    add_message("assistant", error_message)


if __name__ == "__main__":
    main()