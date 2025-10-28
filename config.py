"""Configuration settings for the Agno Streamlit application"""

import os
from typing import Dict, Any, Optional
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from agno.models.base import Model
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # Database settings (if using PostgreSQL)
    DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")
    
    # Storage settings
    STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
    
    # Knowledge base settings
    KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "./knowledge")

    # Azure OpenAI 配置
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: Optional[str] = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_MODEL_ID: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    # DeepSeek 配置（腾讯云）
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_ENDPOINT: str = os.getenv("DEEPSEEK_API_ENDPOINT") or "https://api.lkeap.cloud.tencent.com/v1"
    DEEPSEEK_DEPLOYMENT_NAME: str = os.getenv("DEEPSEEK_DEPLOYMENT_NAME") or "deepseek-v3.1"
    DEEPSEEK_MODEL_ID: str = os.getenv("DEEPSEEK_DEPLOYMENT_NAME") or "deepseek-v3.1"

    # Azure Embedder 配置
    AZURE_EMBEDDER_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_EMBEDDER_OPENAI_API_KEY")
    AZURE_EMBEDDER_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_EMBEDDER_OPENAI_ENDPOINT")
    AZURE_EMBEDDER_OPENAI_API_VERSION: str = os.getenv("AZURE_EMBEDDER_OPENAI_API_VERSION") or "2024-07-01-preview"
    AZURE_EMBEDDER_DEPLOYMENT: str = os.getenv("AZURE_EMBEDDER_DEPLOYMENT") or "text-embedding-ada-002"

    @classmethod
    def validate_config(cls) -> bool:
        """验证必要的配置是否存在"""
        # 验证DeepSeek配置（默认使用）
        if not cls.DEEPSEEK_API_KEY:
            print(f"❌ 缺少必要的环境变量: DEEPSEEK_API_KEY")
            return False

        # 验证Azure配置（可选）
        if cls.AZURE_OPENAI_API_KEY and not cls.AZURE_OPENAI_ENDPOINT:
            print(f"❌ Azure配置不完整，缺少: AZURE_OPENAI_ENDPOINT")
            return False

        if cls.AZURE_OPENAI_ENDPOINT and not cls.AZURE_OPENAI_API_KEY:
            print(f"❌ Azure配置不完整，缺少: AZURE_OPENAI_API_KEY")
            return False

        return True

    @classmethod
    def get_old_version_azure_openai_config(cls, id=None) -> dict:
        """获取Azure OpenAI配置字典"""
        model_id = id if id else cls.AZURE_OPENAI_MODEL_ID
        return {
            "id": model_id,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "azure_deployment": cls.AZURE_OPENAI_DEPLOYMENT,
        }

    @classmethod
    def get_new_version_azure_openai_config(cls, id=None) -> dict:
        """获取Azure OpenAI配置字典"""
        model_id = id if id else cls.AZURE_OPENAI_MODEL_ID
        return {
            "id": model_id,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "base_url": f"{cls.AZURE_OPENAI_ENDPOINT}/openai/v1/"
        }

    @classmethod
    def get_deepseek_config(cls, id=None) -> dict:
        """获取DeepSeek配置字典（适配腾讯云）"""
        model_id = id if id else cls.DEEPSEEK_MODEL_ID
        return {
            "id": model_id,
            "api_key": cls.DEEPSEEK_API_KEY,
            "base_url": cls.DEEPSEEK_API_ENDPOINT,
            # thinking_enabled参数可能不被当前版本的DeepSeek类支持
            # "thinking_enabled": False  # 临时移除此参数以避免初始化错误
        }

    @classmethod
    def get_azure_embedder_config(cls, id=None) -> dict:
        """获取Azure Embedder配置字典"""
        model_id = id if id else cls.AZURE_EMBEDDER_DEPLOYMENT
        return {
            "id": model_id,
            "api_key": cls.AZURE_EMBEDDER_OPENAI_API_KEY,
            "api_version": cls.AZURE_EMBEDDER_OPENAI_API_VERSION,
            "base_url": cls.AZURE_EMBEDDER_OPENAI_ENDPOINT,
        }


def get_ai_model(model_id=None, model_type="deepseek") -> Model:
    """
    获取AI模型实例

    Args:
        model_id: 模型ID，如不指定则使用默认配置
        model_type: 模型类型，支持 "deepseek" 或 "azure"

    Returns:
        模型实例
    """
    if model_type.lower() == "azure":
        # config = Config.get_old_version_azure_openai_config(model_id)
        # return AzureOpenAI(**config)
        config = Config.get_new_version_azure_openai_config(model_id)
        return OpenAIChat(**config)
    else:
        config = Config.get_deepseek_config(model_id)
        return DeepSeek(**config)
