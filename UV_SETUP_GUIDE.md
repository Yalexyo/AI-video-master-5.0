# 🚀 AI Video Master 5.0 - UV 环境设置指南

## 📋 项目概述

本项目使用现代化的 Python 包管理工具 `uv` 来管理依赖和虚拟环境，提供更快速和可靠的包管理体验。

## 🔧 系统要求

- **Python**: 3.10+ (推荐 3.10.16+)
- **UV**: 已安装 (当前版本: 0.7.13+)
- **FFmpeg**: 用于视频/音频处理

## 📦 项目结构

```
demo/
├── video_to_slice/          # 视频切片模块
│   ├── .venv/              # UV 虚拟环境
│   ├── pyproject.toml      # 项目配置和依赖
│   ├── .python-version     # Python 版本锁定 (3.10)
│   └── *.py               # Python 脚本
├── video_to_srt/           # 视频转字幕模块  
│   ├── .venv/              # UV 虚拟环境
│   ├── pyproject.toml      # 项目配置和依赖
│   ├── .python-version     # Python 版本锁定 (3.10)
│   └── *.py               # Python 脚本
├── activate_envs.sh        # 环境管理脚本
├── setup_config.sh         # 配置文件设置脚本 ⭐ 仍然重要！
└── UV_SETUP_GUIDE.md      # 本指南
```

## 🎯 快速开始

### 1️⃣ 设置配置和检查状态

```bash
# 第一步：设置API密钥和配置文件 ⚠️ 重要步骤！
./setup_config.sh all

# 第二步：检查项目状态
./setup_config.sh status
```

### 2️⃣ 编辑配置文件

```bash
# 编辑环境变量（包含API密钥）
cp .env_template .env
nano .env

# 分别编辑各项目配置
nano video_to_slice/config.txt    # Google Cloud配置
nano video_to_srt/config.txt      # DashScope配置

# 加载环境变量
source .env
```

### 3️⃣ 激活和运行

```bash
# 激活视频切片环境
source activate_envs.sh slice

# 运行项目
uv run run.py
```

## 🔧 为什么 setup_config.sh 仍然重要？

虽然我们使用了 UV 管理Python依赖，但 `setup_config.sh` 负责**业务配置**，完全不同的功能：

### UV 的职责 🐍
- ✅ 管理 Python 包依赖
- ✅ 创建和管理虚拟环境
- ✅ 锁定包版本

### setup_config.sh 的职责 🔧
- ✅ 设置 API 密钥 (Google Cloud, DashScope)
- ✅ 创建配置文件 (config.txt)
- ✅ 生成环境变量模板 (.env)
- ✅ 提供配置指导

## 🔑 配置设置详解

### 方式1: 使用配置脚本（推荐）

```bash
# 全部配置
./setup_config.sh all

# 或分别配置
./setup_config.sh slice    # 视频切片配置
./setup_config.sh srt      # 视频转字幕配置  
./setup_config.sh env      # 环境变量模板
```

### 方式2: 手动配置

```bash
# 复制配置模板
cp video_to_slice/config_example.txt video_to_slice/config.txt
cp video_to_srt/config_example.txt video_to_srt/config.txt

# 编辑配置
nano video_to_slice/config.txt
nano video_to_srt/config.txt
```

## 🚀 完整工作流程

```bash
# 1. 克隆项目后的初始设置
./setup_config.sh all                    # 设置配置文件
./setup_config.sh status                 # 检查项目状态

# 2. 配置API密钥
nano .env                                 # 编辑环境变量

# 3. 运行项目 (环境会自动创建和安装依赖)
source activate_envs.sh slice             # 激活视频切片环境
uv run run.py                            # 运行脚本

# 或者
source activate_envs.sh srt               # 激活视频转字幕环境
uv run batch_video_to_srt.py input_videos/ -o output_srt/
```

## 📝 核心API配置

### Google Cloud Video Intelligence (视频切片)

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用 Video Intelligence API
3. 创建服务账号并下载 JSON 密钥文件
4. 设置环境变量：
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   ```

### DashScope API (视频转字幕)

1. 访问 [DashScope](https://dashscope.aliyun.com/)
2. 注册并获取 API Key
3. 设置环境变量：
   ```bash
   export DASHSCOPE_API_KEY="your_api_key"
   ```

## 🆚 脚本功能对比

| 脚本文件 | 主要功能 | UV时代是否需要 |
|----------|----------|----------------|
| `activate_envs.sh` | 环境激活和依赖管理 | ✅ **需要** (已更新支持UV) |
| `setup_config.sh` | API密钥和业务配置 | ✅ **需要** (与包管理无关) |
| `requirements.txt` | 依赖列表 | ❌ 已被 `pyproject.toml` 替代 |

## 🔧 UV 命令速查

```bash
# 环境管理
uv venv                    # 创建虚拟环境
uv python pin 3.10         # 锁定Python版本

# 依赖管理  
uv add requests            # 添加依赖
uv remove requests         # 移除依赖
uv sync                    # 同步依赖

# 运行脚本
uv run script.py           # 运行脚本（自动激活环境）
```

## ✨ 完整示例

```bash
# 全新设置
git clone <your-repo>
cd demo

# 🔧 配置阶段
./setup_config.sh all                     # 设置业务配置
./setup_config.sh status                  # 检查配置状态

# ⚙️ 个性化配置
cp .env_template .env
nano .env                                 # 填入你的API密钥

# 🚀 开始使用 (环境会自动创建和安装依赖)
source activate_envs.sh slice             # 激活环境
uv run run.py                            # 运行项目
```

---

🎉 **现在你有了完整的现代化Python项目环境！**

**关键点**：
- `setup_config.sh` **仍然必需** - 负责API密钥等业务配置
- UV 只负责Python包管理，不涉及业务配置
- 两者配合使用才能完整设置项目环境 