#!/bin/bash

# AI Video Master 5.0 配置向导 (UV版本)
echo "⚙️ AI Video Master 5.0 配置向导 (已优化)"
echo "============================================"

function setup_video_slice_config() {
    echo ""
    echo "🎬 设置视频切片项目配置..."
    
    if [ ! -f "video_to_slice/config.txt" ]; then
        cp "video_to_slice/config_example.txt" "video_to_slice/config.txt"
        echo "✅ 已创建 video_to_slice/config.txt"
        echo "📝 请编辑配置文件，添加你的 Google Cloud 凭据："
        echo "   nano video_to_slice/config.txt"
    else
        echo "⚠️  配置文件已存在: video_to_slice/config.txt"
    fi
    
    echo ""
    echo "🔑 Google Cloud 配置步骤："
    echo "1. 访问 https://console.cloud.google.com/"
    echo "2. 创建项目并启用 Video Intelligence API"
    echo "3. 创建服务账号并下载 JSON 密钥文件"
    echo "4. 将JSON文件放在 video_to_slice/ 目录下"
    echo ""
    echo "💡 提示: 使用 activate_envs.sh 会自动设置凭据路径！"
}

function setup_video_srt_config() {
    echo ""
    echo "📝 设置视频转字幕项目配置..."
    
    if [ ! -f "video_to_srt/config.txt" ]; then
        cp "video_to_srt/config_example.txt" "video_to_srt/config.txt"
        echo "✅ 已创建 video_to_srt/config.txt"
        echo "📝 请编辑配置文件，添加你的 DashScope API 密钥："
        echo "   nano video_to_srt/config.txt"
    else
        echo "⚠️  配置文件已存在: video_to_srt/config.txt"
    fi
    
    echo ""
    echo "🔑 DashScope & OSS 配置步骤："
    echo "1. 访问 https://dashscope.aliyun.com/ 获取API密钥"
    echo "2. 访问 https://oss.console.aliyun.com/ 配置OSS"
    echo "3. 在 .env 文件中设置所有密钥"
    echo ""
    echo "💡 提示: 推荐使用 .env 统一管理环境变量！"
}

function setup_env_variables() {
    echo ""
    echo "🔧 设置环境变量模板..."
    
    cat > .env_template << 'EOF'
# AI Video Master 5.0 环境变量配置 (更新版)
# 复制此文件为 .env 并填入真实的API密钥

# ========== 视频切片项目 ==========
# Google Cloud 认证 (路径由activate_envs.sh智能设置)
# GOOGLE_APPLICATION_CREDENTIALS 由 activate_envs.sh 智能设置

# ========== 视频转字幕项目 ==========
# DashScope API
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# 阿里云OSS配置（用于大文件上传）
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-cn-shanghai.aliyuncs.com"
export OSS_BUCKET_NAME="your_bucket_name"
export OSS_UPLOAD_DIR="upload"
export ENABLE_OSS="True"
EOF
    
    echo "✅ 已创建环境变量模板: .env_template"
    echo ""
    echo "📝 配置步骤："
    echo "   cp .env_template .env"
    echo "   nano .env  # 填入真实的API密钥"
    echo ""
    echo "🎯 推荐工作流："
    echo "   1. 编辑 .env 文件添加API密钥"
    echo "   2. 使用 source activate_envs.sh [项目] 一键启动"
    echo "   3. 享受智能环境变量管理！"
}

function check_current_status() {
    echo ""
    echo "📊 当前项目状态检查"
    echo "===================="
    
    echo ""
    echo "🔍 环境文件检查："
    if [ -f ".env" ]; then
        echo "  ✅ .env 文件存在"
        # 检查关键配置
        if grep -q "DASHSCOPE_API_KEY" .env && ! grep -q "your_dashscope_api_key" .env; then
            echo "  ✅ DashScope API 已配置"
        else
            echo "  ❌ DashScope API 需要配置"
        fi
        
        if grep -q "OSS_ACCESS_KEY_ID" .env && ! grep -q "your_access_key_id" .env; then
            echo "  ✅ 阿里云OSS 已配置"
        else
            echo "  ❌ 阿里云OSS 需要配置"
        fi
    else
        echo "  ❌ .env 文件不存在，请先运行: ./setup_config.sh env"
    fi
    
    echo ""
    echo "🔍 Google Cloud 凭据检查："
    if [ -f "video_to_slice/video-ai-461014-d0c437ff635f.json" ]; then
        echo "  ✅ Google Cloud JSON文件存在"
    else
        echo "  ❌ 需要将Google Cloud JSON文件放入 video_to_slice/ 目录"
    fi
    
    echo ""
    echo "🔍 虚拟环境检查："
    if [ -d "video_to_slice/.venv" ]; then
        echo "  ✅ 视频切片环境已创建"
    else
        echo "  ⚠️  视频切片环境待创建"
    fi
    
    if [ -d "video_to_srt/.venv" ]; then
        echo "  ✅ 视频转字幕环境已创建"
    else
        echo "  ⚠️  视频转字幕环境待创建"
    fi
    
    echo ""
    echo "🚀 下一步建议："
    if [ -f ".env" ] && [ -f "video_to_slice/video-ai-461014-d0c437ff635f.json" ]; then
        echo "  ✅ 配置完整！可以直接使用:"
        echo "     source activate_envs.sh slice    # 或"
        echo "     source activate_envs.sh srt"
    else
        echo "  📝 需要完成配置后再使用 activate_envs.sh"
    fi
}

# 主逻辑
case "$1" in
    "slice")
        setup_video_slice_config
        ;;
    "srt")
        setup_video_srt_config
        ;;
    "env")
        setup_env_variables
        ;;
    "status"|"check")
        check_current_status
        ;;
    "all"|"")
        setup_video_slice_config
        setup_video_srt_config
        setup_env_variables
        check_current_status
        ;;
    *)
        echo "使用方法:"
        echo "  ./setup_config.sh slice     # 设置视频切片配置"
        echo "  ./setup_config.sh srt       # 设置视频转字幕配置"
        echo "  ./setup_config.sh env       # 设置环境变量模板"
        echo "  ./setup_config.sh status    # 检查配置状态"
        echo "  ./setup_config.sh all       # 全部设置+状态检查"
        ;;
esac

echo ""
echo "🎉 配置向导完成！"
echo ""
echo "⚡ 快速启动流程："
echo "1. ./setup_config.sh env       # 创建环境变量模板"
echo "2. nano .env                   # 编辑API密钥"
echo "3. source activate_envs.sh slice|srt  # 智能启动环境"
echo ""
echo "📚 获取帮助："
echo "   source activate_envs.sh help   # 查看环境管理帮助"
echo "   ./setup_config.sh status       # 检查配置状态" 