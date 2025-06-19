#!/bin/bash
# AI Video Master 5.0 - 快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示启动信息
echo -e "${BLUE}🎬 AI Video Master 5.0 - 并行视频处理系统${NC}"
echo -e "${BLUE}=================================================${NC}"

# 检查Python环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，请先运行 'uv sync' 或激活现有环境${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${GREEN}🔧 激活虚拟环境...${NC}"
source .venv/bin/activate

# 检查输入目录
if [ ! -d "data/input" ] || [ -z "$(ls -A data/input 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  输入目录为空: data/input/${NC}"
    echo -e "${YELLOW}请将视频文件放入 data/input/ 目录${NC}"
    
    # 创建目录并显示帮助
    mkdir -p data/input
    echo -e "${BLUE}📁 已创建输入目录: data/input/${NC}"
    echo -e "${BLUE}💡 使用方法:${NC}"
    echo -e "   cp your_videos/* data/input/"
    echo -e "   $0"
    exit 1
fi

# 创建必要目录
mkdir -p data/output data/temp

# 检查Google凭据
if [ ! -f "config/video-ai-461014-d0c437ff635f.json" ] && [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}❌ Google Cloud凭据未配置${NC}"
    echo -e "${YELLOW}请将凭据文件放入 config/ 目录或设置环境变量${NC}"
    exit 1
fi

# 显示输入文件
echo -e "${GREEN}📁 发现输入视频文件:${NC}"
ls -la data/input/ | grep -E '\.(mp4|avi|mov|mkv|wmv|flv)$' || echo "  (无支持的视频文件)"

# 解析命令行参数
ARGS=""
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    ARGS="$ARGS -v"
    echo -e "${BLUE}🔍 启用详细输出模式${NC}"
fi

if [ "$1" = "-q" ] || [ "$1" = "--quiet" ]; then
    ARGS="$ARGS -q"
    echo -e "${BLUE}🔇 启用安静模式${NC}"
fi

# 运行处理
echo -e "${GREEN}🚀 开始处理视频...${NC}"
echo -e "${BLUE}=================================================${NC}"

python run.py data/input/ $ARGS

# 显示结果
if [ $? -eq 0 ]; then
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${GREEN}✅ 处理完成！${NC}"
    echo -e "${GREEN}📂 输出目录: data/output/${NC}"
    
    # 显示输出统计
    if [ -d "data/output" ]; then
        output_count=$(find data/output -name "*.mp4" 2>/dev/null | wc -l)
        echo -e "${GREEN}🎬 生成切片数量: $output_count${NC}"
    fi
else
    echo -e "${RED}❌ 处理失败${NC}"
    exit 1
fi 