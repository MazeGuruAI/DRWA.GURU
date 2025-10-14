# 📁 文件上传与AI识别功能指南

## 🎯 功能概述

本RWA资产代币化平台支持多种文件上传和AI识别功能，特别优化了图片和文档的智能分析能力。

## 🖼️ 图片识别功能

### 支持的图片格式
- **JPG/JPEG**: 标准图片格式
- **PNG**: 支持透明背景的图片
- **其他常见格式**: BMP, GIF等

### 图片处理流程
1. **上传图片**: 在侧边栏选择图片文件
2. **自动转换**: 系统自动将图片转换为`agno.media.Image`对象
3. **传递给Team**: 图片随消息一起发送给RWA团队
4. **AI分析**: 支持视觉识别的AI模型分析图片内容

### 代码实现示例
```python
# 创建agno Image对象
from agno.media import Image

# 方法1: 使用文件路径
image = Image(filepath="path/to/image.jpg")

# 方法2: 使用字节内容
image = Image(content=image_bytes)

# 发送给Team
response = rwa_team.run(
    message="请分析这张图片",
    images=[image]
)
```

## 📄 文档识别功能

### 支持的文档格式
- **PDF**: 合同、证书、报告等
- **DOC/DOCX**: Word文档
- **其他**: 根据需要可扩展更多格式

### 文档处理流程
1. **上传文档**: 选择文档文件
2. **内容提取**: 系统提取文档基本信息
3. **AI分析**: AI代理分析文档内容和结构
4. **验证报告**: 生成文档真实性和合法性报告

## 🔧 技术实现细节

### 前端文件处理
```python
def process_uploaded_files(uploaded_files):
    """处理上传的文件并返回文件信息"""
    files_data = []
    
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.getvalue()  # 获取文件字节内容
        file_info = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": uploaded_file.size,
            "bytes": file_bytes
        }
        files_data.append(file_info)
    
    return files_data
```

### 图片对象创建
```python
def create_agno_images_from_bytes(files_data):
    """从文件字节数据创建agno Image对象"""
    images = []
    
    for file_info in files_data:
        if file_info['type'].startswith('image/'):
            agno_image = Image(content=file_info['bytes'])
            images.append(agno_image)
    
    return images
```

### Team调用
```python
# 发送消息和图片给Team
if agno_images:
    response = rwa_team.run(
        message=complete_message,
        images=agno_images
    )
else:
    response = rwa_team.run(message=complete_message)
```

## 🚀 使用场景

### 1. 房产证验证
- 上传房产证图片
- AI自动识别证书信息
- 验证证书真实性和合法性
- 提取关键资产信息

### 2. 资产评估
- 上传资产相关图片和文档
- AI分析资产状况和特征
- 结合市场数据进行估值
- 生成专业评估报告

### 3. 合规检查
- 上传合同和证明文件
- AI检查文档完整性
- 验证法律合规性
- 识别潜在风险点

## ⚙️ 配置参数

### Team.run方法参数
根据项目内存中的规范，Team.run方法支持以下参数：

```python
response = rwa_team.run(
    message="消息内容",           # 必需
    user_id="用户ID",            # 可选
    session_id="会话ID",         # 可选
    images=[image1, image2],    # 可选，图片列表
    stream=False,               # 可选，是否流式响应
    stream_intermediate_steps=False,  # 可选
    show_full_reasoning=False   # 可选
)
```

## 🎯 最佳实践

### 1. 文件大小控制
- 建议图片文件小于10MB
- 文档文件小于20MB
- 系统会自动显示文件大小信息

### 2. 格式选择
- 图片: 优先使用JPG格式，文件更小
- 文档: PDF格式兼容性最好
- 扫描件: 确保图片清晰度足够

### 3. 批量处理
- 支持同时上传多个文件
- 系统会逐个处理每个文件
- 显示处理进度和结果

### 4. 错误处理
```python
try:
    agno_images = create_agno_images_from_bytes(files_data)
    response = rwa_team.run(message=message, images=agno_images)
except Exception as e:
    st.error(f"处理文件时出错: {str(e)}")
```

## 📋 故障排除

### 常见问题
1. **图片无法识别**: 检查文件格式和大小
2. **处理超时**: 文件过大或网络问题
3. **格式不支持**: 转换为支持的格式

### 调试信息
- 查看浏览器控制台错误
- 检查Streamlit日志输出
- 验证文件完整性

## 🔄 版本更新

当前版本支持的主要功能：
- ✅ 多图片上传和识别
- ✅ 文档信息提取
- ✅ AI视觉分析
- ✅ 错误处理和用户反馈
- 🔄 PDF文本提取（规划中）
- 🔄 音频识别（规划中）

---

**注意**: 确保上传的文件不包含敏感信息，系统会临时处理文件内容用于AI分析。