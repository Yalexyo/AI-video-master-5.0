#!/usr/bin/env python3
"""
AI Video Master 5.0 - 统一运行入口 (纯并行版)
专注于并行处理，提供最佳性能

功能特性:
- 🚀 双层并行处理 (视频级 + 切片级)
- 🎯 智能并发控制 (遵循API配额)
- 📊 实时进度监控
- 🛡️ 自动重试和容错
- 📈 详细性能报告
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="🎬 AI Video Master 5.0 - 并行视频切片处理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s data/input/                         # 处理输入目录下所有视频
  %(prog)s data/input/ -o data/output/         # 指定输出目录
  %(prog)s data/input/ -c 2 -w 6               # 调整并发参数
  %(prog)s data/input/ -f shot_detection       # 仅镜头检测(最快)
  %(prog)s data/input/ -v                      # 详细输出

性能优化建议:
  - 使用默认参数通常性能最佳
  - 视频并发数不要超过3 (API限制)
  - FFmpeg线程数建议为CPU核心数的一半
  - 仅使用镜头检测功能可获得最佳速度
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
    
    # 功能参数
    parser.add_argument("-f", "--features", 
                       nargs="+",
                       choices=["shot_detection", "label_detection", "face_detection", "text_detection"],
                       default=["shot_detection"],
                       help="分析功能 (默认: shot_detection，性能最佳)")
    
    # 性能参数
    parser.add_argument("-c", "--concurrent", 
                       type=int, 
                       default=3,
                       help="视频级并发数 (默认: 3，建议不超过3)")
    parser.add_argument("-w", "--ffmpeg-workers", 
                       type=int, 
                       default=4,
                       help="FFmpeg并行线程数 (默认: 4，建议2-8)")
    
    # 文件过滤参数
    parser.add_argument("--patterns", 
                       nargs="+",
                       default=["*.mp4", "*.avi", "*.mov", "*.mkv"],
                       help="文件匹配模式 (默认: mp4,avi,mov,mkv)")
    
    # 输出控制
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="详细输出模式")
    parser.add_argument("-q", "--quiet", 
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
        print("🎬 AI Video Master 5.0 - 并行视频切片处理系统")
        print("=" * 60)
        print(f"📁 输入目录: {args.input_dir}")
        print(f"📂 输出目录: {args.output}")
        print(f"🎯 分析功能: {', '.join(args.features)}")
        print(f"🚀 视频并发数: {args.concurrent}")
        print(f"⚡ FFmpeg线程数: {args.ffmpeg_workers}")
        print(f"📄 文件模式: {', '.join(args.patterns)}")
        print("=" * 60)
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        return 1
    
    # 检查环境变量
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        google_cred_path = os.path.join(os.path.dirname(__file__), "config", "video-ai-461014-d0c437ff635f.json")
        if os.path.exists(google_cred_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_cred_path
            logger.info(f"使用项目配置的Google凭据: {google_cred_path}")
        else:
            logger.error("❌ Google Cloud凭据未设置")
            logger.error("请设置 GOOGLE_APPLICATION_CREDENTIALS 环境变量")
            logger.error("或将凭据文件放在 config/ 目录下")
            return 1
    
    try:
        # 导入并行处理器
        from parallel_batch_processor import ParallelBatchProcessor
        
        logger.info("🚀 启动并行批处理器...")
        
        # 创建处理器
        processor = ParallelBatchProcessor(
            output_dir=args.output,
            temp_dir=args.temp,
            max_concurrent=args.concurrent,
            ffmpeg_workers=args.ffmpeg_workers
        )
        
        # 执行处理
        result = processor.process_batch_sync(
            input_dir=args.input_dir,
            file_patterns=args.patterns,
            features=args.features
        )
        
        # 显示结果
        if result["success"]:
            if not args.quiet:
                print("\n" + "=" * 60)
                print("✅ 并行批处理完成!")
                print(f"📊 处理统计: {result['stats']['processed_videos']}/{result['stats']['total_videos']} 个视频成功")
                print(f"🎬 总计生成: {result['stats']['total_slices']} 个视频切片")
                print(f"⏱️  总耗时: {result['total_duration']:.1f}秒")
                print(f"📄 详细报告: {result['report_file']}")
                
                if result['parallel_info']['time_saved_percentage'] > 0:
                    print(f"🚀 性能提升: 节省了 {result['parallel_info']['time_saved_percentage']:.1f}% 的时间!")
                
                # 显示性能统计
                avg_time = result['parallel_info']['average_time_per_video']
                print(f"📈 平均每视频: {avg_time:.1f}秒")
                print("=" * 60)
            
            logger.info("处理完成，程序正常退出")
            return 0
        else:
            logger.error(f"❌ 批处理失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⚠️  用户中断处理")
        return 130
    except ImportError as e:
        logger.error(f"❌ 依赖模块导入失败: {e}")
        logger.error("请确保所有依赖文件在 src/ 目录下")
        return 1
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        if args.verbose:
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return 1
    

if __name__ == "__main__":
    sys.exit(main()) 