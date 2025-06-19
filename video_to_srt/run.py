#!/usr/bin/env python3
"""
AI Video Master 5.0 - 视频转SRT字幕系统 (规范化版)
专注于高质量语音识别转字幕，采用标准化项目结构

功能特性:
- 🎯 DashScope高精度语音识别
- 📝 自动生成SRT字幕文件
- 🔄 批量处理多个视频文件
- 🛡️ 智能质量过滤和错误处理
- 📊 详细的处理统计报告
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入环境变量加载器
from src.env_loader import get_dashscope_api_key, get_default_vocab_id, get_default_language, get_default_quality

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="🎬 AI Video Master 5.0 - 视频转SRT字幕系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s data/input/                         # 处理输入目录下所有视频
  %(prog)s data/input/ -o data/output/         # 指定输出目录
  %(prog)s data/input/ -q high                 # 高质量模式
  %(prog)s data/input/ -l zh                   # 指定语言
  %(prog)s data/input/ -v                      # 详细输出

支持格式:
  - 视频: MP4, MOV, AVI, MKV, WEBM, WMV, FLV
  - 音频: MP3, WAV, AAC, FLAC, OGG
        """
    )
    
    # 基本参数
    parser.add_argument("input_dir", 
                       help="输入视频目录路径")
    parser.add_argument("-o", "--output", 
                       default="./data/output",
                       help="输出目录 (默认: ./data/output)")
    parser.add_argument("-t", "--temp", 
                       default="./data/temp",
                       help="临时目录 (默认: ./data/temp)")
    
    # 质量参数
    parser.add_argument("-q", "--quality", 
                       choices=["auto", "high", "standard"],
                       default=get_default_quality(),
                       help="音频质量模式 (默认: 从.env文件读取)")
    parser.add_argument("-l", "--language", 
                       default=get_default_language(),
                       help="识别语言 (默认: 从.env文件读取)")
    
    # 🎯 热词参数 - 只使用预设词汇表ID
    parser.add_argument("--vocab-id", 
                       type=str,
                       default=get_default_vocab_id(),
                       help="预设词汇表ID (默认: 从.env文件读取婴幼儿奶粉专用热词表)")
    
    # 文件过滤参数
    parser.add_argument("--patterns", 
                       nargs="+",
                       default=["*.mp4", "*.mov", "*.avi", "*.mkv", "*.webm"],
                       help="文件匹配模式 (默认: 视频格式)")
    
    # 输出控制
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="详细输出模式")
    parser.add_argument("--quiet", 
                       action="store_true",
                       help="安静模式 (仅显示错误)")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 显示启动信息
    if not args.quiet:
        print("🎬 AI Video Master 5.0 - 视频转SRT字幕系统")
        print("=" * 60)
        print(f"📁 输入目录: {args.input_dir}")
        print(f"📂 输出目录: {args.output}")
        print(f"🎯 质量模式: {args.quality}")
        print(f"🌐 识别语言: {args.language}")
        print(f"📄 文件模式: {', '.join(args.patterns)}")
        print("=" * 60)
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        return 1
    
    # 检查API密钥（自动从.env文件读取）
    api_key = get_dashscope_api_key()
    if not api_key:
        logger.error("❌ DashScope API密钥未设置")
        logger.error("请检查以下配置:")
        logger.error("1. 在项目根目录的.env文件中设置: DASHSCOPE_API_KEY=your_api_key")
        logger.error("2. 或设置环境变量: export DASHSCOPE_API_KEY=your_api_key")
        logger.error("3. 参考 config/config_example.txt 文件")
        return 1
    
    # 🎯 显示热词配置信息
    if not args.quiet and args.vocab_id:
        print("🎯 热词配置:")
        print(f"  📋 预设词汇表ID: {args.vocab_id}")
        print(f"  🍼 专用领域: 婴幼儿奶粉 (启赋、蕴淳、蓝钻等10个专业词汇)")
        print("=" * 60)
    
    # 检查是否有视频文件
    input_path = Path(args.input_dir)
    video_files = []
    for pattern in args.patterns:
        video_files.extend(input_path.glob(pattern))
        video_files.extend(input_path.glob(pattern.upper()))
    
    if not video_files:
        logger.error(f"在 {args.input_dir} 中未找到匹配的文件")
        logger.error(f"支持的格式: {', '.join(args.patterns)}")
        return 1
    
    if not args.quiet:
        print(f"📁 发现 {len(video_files)} 个文件:")
    for video in video_files:
        print(f"  - {video.name}")
        print(f"\n🚀 开始批量转录...")
    
    try:
        # 导入批量转录器
        from batch_video_to_srt import BatchVideoTranscriber
        
        logger.info("🚀 启动批量转录器...")
        
        # 创建转录器
        transcriber = BatchVideoTranscriber(
            api_key=api_key
        )
        
        # 执行批量处理
        # 将文件模式转换为扩展名格式
        supported_formats = []
        for pattern in args.patterns:
            if pattern.startswith('*.'):
                supported_formats.append(pattern[1:].lower())  # 移除 * 保留 .ext
        
        result = transcriber.batch_process(
            input_dir=args.input_dir,
            output_dir=args.output,
            supported_formats=supported_formats,
            preset_vocabulary_id=args.vocab_id
        )
        
        # 显示结果
        if result["success"]:
            if not args.quiet:
                print("\n" + "=" * 60)
                print("✅ 批量转录完成!")
                results = result["results"]
                print(f"📊 处理统计:")
                print(f"  ✅ 成功: {results['success_count']}")
                print(f"  ❌ 失败: {results['failed_count']}")
                print(f"  🔒 质量拒绝: {results['quality_rejected_count']}")
                print(f"📂 输出目录: {args.output}")
                print(f"📄 详细报告: {result.get('report_file', '未生成')}")
                print("=" * 60)
            
            logger.info("转录完成，程序正常退出")
            return 0
        else:
            logger.error(f"❌ 批量转录失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⚠️  用户中断处理")
        return 130
    except ImportError as e:
        logger.error(f"❌ 依赖模块导入失败: {e}")
        logger.error("请确保所有依赖文件在 src/ 目录下")
        logger.error("或运行: uv sync")
        return 1
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        if args.verbose:
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 