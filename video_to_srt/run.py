#!/usr/bin/env python3
"""
快速启动脚本 - 批量视频转SRT

简化的启动脚本，自动使用默认目录进行批量转录
"""

import os
import sys
from pathlib import Path

def main():
    """快速启动主函数"""
    print("🎬 批量视频转录为SRT字幕文件")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: 未设置 DASHSCOPE_API_KEY 环境变量")
        print("请先设置API密钥:")
        print("export DASHSCOPE_API_KEY=your_api_key")
        print("或参考 config_example.txt 文件")
        return 1
    
    # 检查输入目录
    input_dir = Path("input_videos")
    if not input_dir.exists():
        print(f"❌ 错误: 输入目录不存在: {input_dir}")
        print("请先创建输入目录并放入视频文件:")
        print("mkdir input_videos")
        return 1
    
    # 检查是否有视频文件
    video_files = []
    for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        video_files.extend(input_dir.glob(f"*{ext}"))
        video_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    if not video_files:
        print(f"❌ 错误: 在 {input_dir} 中未找到视频文件")
        print("支持的格式: .mp4, .mov, .avi, .mkv, .webm")
        return 1
    
    print(f"📁 发现 {len(video_files)} 个视频文件")
    for video in video_files:
        print(f"  - {video.name}")
    
    print("\n🚀 开始批量转录...")
    
    # 导入并运行主程序
    try:
        from batch_video_to_srt import BatchVideoTranscriber
        
        # 初始化转录器
        transcriber = BatchVideoTranscriber(api_key=api_key)
        
        # 批量处理
        result = transcriber.batch_process(
            input_dir="input_videos",
            output_dir="output_srt"
        )
        
        if result["success"]:
            results = result["results"]
            print(f"\n🎉 处理完成!")
            print(f"✅ 成功: {results['success_count']}")
            print(f"❌ 失败: {results['failed_count']}")
            print(f"🔒 质量拒绝: {results['quality_rejected_count']}")
            print(f"📂 输出目录: output_srt/")
            return 0
        else:
            print(f"❌ 批量处理失败: {result['error']}")
            return 1
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保安装了所需依赖:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 