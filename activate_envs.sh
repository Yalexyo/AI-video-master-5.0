#!/bin/bash

# AI Video Master 5.0 环境管理脚本 (UV 版本) - 已清理优化
# 使用方法: source activate_envs.sh [项目名]

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 智能环境变量设置函数
setup_smart_env_vars() {
    local current_dir="$(pwd)"
    local json_file="video-ai-461014-d0c437ff635f.json"
    
    # 智能设置Google Cloud凭据路径
    if [[ "$current_dir" == *"/video_to_slice" ]]; then
        # 在video_to_slice目录中，使用相对路径
        if [ -f "./$json_file" ]; then
            export GOOGLE_APPLICATION_CREDENTIALS="./$json_file"
            echo "🔑 已设置Google凭据: $GOOGLE_APPLICATION_CREDENTIALS"
        fi
    else
        # 在项目根目录或其他位置，使用完整相对路径
        if [ -f "$PROJECT_ROOT/video_to_slice/$json_file" ]; then
            export GOOGLE_APPLICATION_CREDENTIALS="$PROJECT_ROOT/video_to_slice/$json_file"
            echo "🔑 已设置Google凭据: $GOOGLE_APPLICATION_CREDENTIALS"
        fi
    fi
    
    # 加载.env文件中的其他环境变量
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
        if [ -n "$DASHSCOPE_API_KEY" ]; then
            echo "🔑 已加载DashScope API密钥"
        fi
    fi
}

function show_help() {
    echo "🎬 AI Video Master 5.0 环境管理 (UV 版本 - 已优化)"
    echo ""
    echo "使用方法:"
    echo "  source activate_envs.sh slice     # 激活视频切片环境"
    echo "  source activate_envs.sh srt       # 激活视频转字幕环境"
    echo "  source activate_envs.sh status    # 显示项目状态"
    echo "  source activate_envs.sh help      # 显示帮助"
    echo ""
    echo "项目环境信息:"
    echo "  slice  -> video_to_slice/.venv (纯净环境 + 智能环境变量)"
    echo "  srt    -> video_to_srt/.venv (纯净环境 + 智能环境变量)"
    echo ""
    echo "退出环境: deactivate"
    echo ""
    echo "🔧 UV 命令参考:"
    echo "  uv add [包名]       # 添加依赖"
    echo "  uv remove [包名]    # 移除依赖"
    echo "  uv run [脚本]       # 运行脚本 (推荐)"
    echo "  uv sync            # 同步依赖"
    echo ""
    echo "✨ 集成功能:"
    echo "  - 智能环境变量设置 (自动识别工作目录)"
    echo "  - UV虚拟环境管理 (纯净隔离)"
    echo "  - 一键项目启动 (环境+依赖+配置)"
    echo "  - 删除旧环境，节省254MB空间"
}

function activate_slice_env() {
    echo "🎬 激活视频切片环境..."
    cd video_to_slice
    
    # 智能设置环境变量
    setup_smart_env_vars
    
    if [ ! -d ".venv" ]; then
        echo "❌ 虚拟环境不存在，正在创建..."
        uv venv
        echo "📦 安装依赖..."
        uv add google-cloud-videointelligence google-cloud-storage requests
    fi
    
    source .venv/bin/activate
    echo "✅ 已激活视频切片环境 (.venv)"
    echo "📁 当前目录: $(pwd)"
    echo "🐍 Python版本: $(python --version)"
    echo "📦 核心依赖:"
    uv pip list | grep -E "(google-cloud|requests)" | head -5
    
    # 显示环境变量状态
    echo ""
    echo "🔑 环境变量状态:"
    echo "  Google凭据: ${GOOGLE_APPLICATION_CREDENTIALS:-❌ 未设置}"
    if [ -f "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
        echo "  凭据文件: ✅ 存在"
    fi
    
    echo ""
    echo "🚀 运行示例:"
    echo "  uv run run.py                                    # 推荐方式"
    echo "  uv run batch_video_to_slice.py input_videos/ -o output_slices/"
    echo "  python run.py                                   # 传统方式"
}

function activate_srt_env() {
    echo "📝 激活视频转字幕环境..."
    cd video_to_srt
    
    # 智能设置环境变量
    setup_smart_env_vars
    
    if [ ! -d ".venv" ]; then
        echo "❌ 虚拟环境不存在，正在创建..."
        uv venv
        echo "📦 安装依赖..."
        uv add dashscope moviepy requests oss2
    fi
    
    source .venv/bin/activate
    echo "✅ 已激活视频转字幕环境 (.venv)"
    echo "📁 当前目录: $(pwd)"
    echo "🐍 Python版本: $(python --version)"
    echo "📦 核心依赖:"
    uv pip list | grep -E "(dashscope|moviepy|oss2)" | head -5
    
    # 显示环境变量状态
    echo ""
    echo "🔑 环境变量状态:"
    if [ -n "$DASHSCOPE_API_KEY" ]; then
        echo "  DashScope密钥: ✅ 已设置 (${DASHSCOPE_API_KEY:0:8}...)"
    else
        echo "  DashScope密钥: ❌ 未设置"
    fi
    
    if [ -n "$OSS_ACCESS_KEY_ID" ]; then
        echo "  OSS Access Key: ✅ 已设置 ($OSS_ACCESS_KEY_ID)"
    else
        echo "  OSS Access Key: ❌ 未设置"
    fi
    
    echo "  OSS Bucket: ${OSS_BUCKET_NAME:-❌ 未设置}"
    echo "  OSS Endpoint: ${OSS_ENDPOINT:-❌ 未设置}"
    echo "  OSS Upload Dir: ${OSS_UPLOAD_DIR:-❌ 未设置}"
    echo "  OSS 启用状态: ${ENABLE_OSS:-❌ 未设置}"
    
    echo ""
    echo "🚀 运行示例:"
    echo "  uv run run.py                                    # 推荐方式"
    echo "  uv run batch_video_to_srt.py input_videos/ -o output_srt/"
    echo "  python run.py                                   # 传统方式"
}

function show_status() {
    echo "📊 AI Video Master 5.0 项目状态"
    echo "================================"
    echo ""
    echo "🎬 视频切片项目:"
    if [ -d "video_to_slice/.venv" ]; then
        echo "  ✅ 环境: video_to_slice/.venv"
        echo "  📦 大小: $(cd video_to_slice && du -sh .venv | cut -f1)"
        if [ -f "video_to_slice/video-ai-461014-d0c437ff635f.json" ]; then
            echo "  🔑 凭据: ✅ Google Cloud JSON文件存在"
        else
            echo "  🔑 凭据: ❌ Google Cloud JSON文件缺失"
        fi
    else
        echo "  ❌ 环境未创建"
    fi
    
    echo ""
    echo "📝 视频转字幕项目:"
    if [ -d "video_to_srt/.venv" ]; then
        echo "  ✅ 环境: video_to_srt/.venv"
        echo "  📦 大小: $(cd video_to_srt && du -sh .venv | cut -f1)"
        if [ -f ".env" ]; then
            source .env
            echo "  🔑 凭据: ${DASHSCOPE_API_KEY:+✅ DashScope密钥已配置}"
        else
            echo "  🔑 凭据: ⚠️ 需要配置.env文件"
        fi
    else
        echo "  ❌ 环境未创建"
    fi
    
    echo ""
    echo "🧹 优化状态: 已清理，节省254MB空间"
    echo "🔧 管理工具: UV (现代化Python包管理)"
    echo "⚡ 特性: 智能环境变量 + 依赖隔离 + 一键启动"
}

# 主逻辑
case "$1" in
    "slice")
        activate_slice_env
        ;;
    "srt")
        activate_srt_env
        ;;
    "status")
        show_status
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ 未知选项: $1"
        show_help
        ;;
esac 