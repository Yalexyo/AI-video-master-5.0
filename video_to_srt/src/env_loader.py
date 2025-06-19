#!/usr/bin/env python3
"""
环境变量加载模块
自动加载项目根目录下的 .env 文件
"""

import os
from pathlib import Path
from typing import Optional

# 尝试导入 python-dotenv
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def load_project_env() -> bool:
    """
    加载项目环境变量
    
    Returns:
        bool: 加载成功返回True，否则返回False
    """
    # 查找项目根目录的 .env 文件
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # 从 src/ 回到项目根目录
    env_file = project_root / ".env"
    
    if not env_file.exists():
        return False
    
    if DOTENV_AVAILABLE:
        # 使用 python-dotenv 加载
        load_dotenv(env_file)
        return True
    else:
        # 手动解析 .env 文件
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # 设置环境变量（不覆盖已存在的）
                        if key not in os.environ:
                            os.environ[key] = value
            return True
        except Exception:
            return False

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    获取环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        环境变量值或默认值
    """
    # 先尝试加载 .env 文件
    load_project_env()
    
    return os.environ.get(key, default)

def get_dashscope_api_key() -> Optional[str]:
    """
    获取 DashScope API 密钥
    
    Returns:
        API密钥或None
    """
    return get_env_var("DASHSCOPE_API_KEY")

def get_default_vocab_id() -> Optional[str]:
    """
    获取默认词汇表ID
    
    Returns:
        词汇表ID或None
    """
    return get_env_var("DEFAULT_VOCAB_ID")

def get_default_language() -> str:
    """
    获取默认语言
    
    Returns:
        默认语言，默认为 'zh'
    """
    return get_env_var("DEFAULT_LANGUAGE", "zh")

def get_default_quality() -> str:
    """
    获取默认音频质量
    
    Returns:
        默认音频质量，默认为 'auto'
    """
    return get_env_var("DEFAULT_QUALITY", "auto")

# 自动加载环境变量
load_project_env() 