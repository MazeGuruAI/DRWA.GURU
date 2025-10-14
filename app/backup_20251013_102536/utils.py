"""Utility functions for the RWA Streamlit application"""

from typing import List, Dict, Any
import streamlit as st
import base64
import io
from agno.media import Image
import tempfile
import os


def add_message(role: str, content: str, file_data: List[Dict] = None) -> None:
    """Add a message to the session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    message = {"role": role, "content": content}
    if file_data:
        message["files"] = file_data
        
    st.session_state.messages.append(message)


def display_messages() -> None:
    """Display chat messages from session state."""
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Display message content
                st.markdown(message["content"])
                
                # Display files if attached
                if "files" in message and message["files"]:
                    for file_info in message["files"]:
                        st.markdown(f"📎 **{file_info['name']}** ({file_info['size_mb']:.2f}MB)")


def clear_chat_history() -> None:
    """Clear the chat history."""
    st.session_state.messages = []


def get_file_content_base64(uploaded_file) -> str:
    """Convert uploaded file content to base64 string."""
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')


def process_uploaded_files(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded files and return file information."""
    files_data = []
    
    for uploaded_file in uploaded_files:
        file_content = get_file_content_base64(uploaded_file)
        file_bytes = uploaded_file.getvalue()  # 获取文件的字节内容
        
        file_info = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "size_mb": uploaded_file.size / (1024 * 1024),
            "content": file_content,
            "bytes": file_bytes  # 添加字节内容
        }
        files_data.append(file_info)
    
    return files_data


def create_agno_images_from_files(files_data: List[Dict[str, Any]]) -> List[Image]:
    """从文件数据创建agno Image对象列表"""
    images = []
    
    for file_info in files_data:
        # 只处理图片文件
        if file_info['type'] and file_info['type'].startswith('image/'):
            try:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_info['name'].split('.')[-1]}") as temp_file:
                    temp_file.write(file_info['bytes'])
                    temp_path = temp_file.name
                
                # 创建agno Image对象
                agno_image = Image(filepath=temp_path)
                images.append(agno_image)
                
                # 清理临时文件（可选，系统会自动清理）
                # os.unlink(temp_path)
                
            except Exception as e:
                st.warning(f"处理图片文件 {file_info['name']} 时出错: {str(e)}")
    
    return images


def create_agno_images_from_bytes(files_data: List[Dict[str, Any]]) -> List[Image]:
    """从文件字节数据直接创建agno Image对象列表"""
    images = []
    
    for file_info in files_data:
        # 只处理图片文件
        if file_info['type'] and file_info['type'].startswith('image/'):
            try:
                # 直接使用字节内容创建Image对象
                agno_image = Image(content=file_info['bytes'])
                images.append(agno_image)
            except Exception as e:
                st.warning(f"处理图片文件 {file_info['name']} 时出错: {str(e)}")
    
    return images


def format_file_info_for_agent(files_data: List[Dict[str, Any]]) -> str:
    """Format file information for agent processing."""
    if not files_data:
        return ""
    
    file_info_text = "\n\n=== 用户上传的文件信息 ===\n"
    for file_info in files_data:
        file_info_text += f"- 文件名: {file_info['name']}\n"
        file_info_text += f"- 文件类型: {file_info['type']}\n"
        file_info_text += f"- 文件大小: {file_info['size_mb']:.2f}MB\n"
        file_info_text += "\n"
    
    file_info_text += "请对这些文件进行验证和分析。\n"
    file_info_text += "=== 文件信息结束 ===\n\n"
    
    return file_info_text