#!/usr/bin/env python3
"""
批量视频切片工具 - 快速启动脚本
提供便捷的启动方式和环境检查
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    checks = {
        "Python版本": False,
        "FFmpeg": False,
        "依赖包": False,
        "Google Cloud凭据": False
    }
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version >= (3, 10):
        checks["Python版本"] = True
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}.{python_version.micro} < 3.10")
    
    # 检查FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
        if result.returncode == 0:
            checks["FFmpeg"] = True
            print("✅ FFmpeg 已安装")
        else:
            print("❌ FFmpeg 不可用")
    except FileNotFoundError:
        print("❌ FFmpeg 未安装")
    except subprocess.TimeoutExpired:
        print("⚠️ FFmpeg 检查超时")
    
    # 检查依赖包
    try:
        import google.cloud.videointelligence_v1
        import google.cloud.storage
        import requests
        checks["依赖包"] = True
        print("✅ Python依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
    
    # 检查Google Cloud凭据
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(cred_path):
            checks["Google Cloud凭据"] = True
            print(f"✅ Google Cloud凭据: {cred_path}")
        else:
            print(f"❌ 凭据文件不存在: {cred_path}")
    elif os.path.exists("google_credentials.json"):
        checks["Google Cloud凭据"] = True
        print("✅ Google Cloud凭据: ./google_credentials.json")
    else:
        print("❌ 未找到Google Cloud凭据")
    
    return all(checks.values()), checks

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装Python依赖包...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("1. 基本用法:")
    print("   python batch_video_to_slice.py input_videos/")
    print()
    print("2. 指定输出目录:")
    print("   python batch_video_to_slice.py input_videos/ -o my_output/")
    print()
    print("3. 详细输出:")
    print("   python batch_video_to_slice.py input_videos/ -v")
    print()
    print("4. 自定义分析功能:")
    print("   python batch_video_to_slice.py input_videos/ -f shot_detection label_detection")

def main():
    """主函数"""
    print("🎬 批量视频切片工具 - 环境检查")
    print("=" * 50)
    
    # 检查环境
    all_ok, checks = check_environment()
    
    if not all_ok:
        print("\n⚠️ 环境检查发现问题:")
        
        for check_name, status in checks.items():
            if not status:
                print(f"   - {check_name}")
        
        print("\n🔧 解决方案:")
        
        if not checks["Python版本"]:
            print("   - 升级Python到3.10+版本")
        
        if not checks["FFmpeg"]:
            print("   - 安装FFmpeg:")
            print("     macOS: brew install ffmpeg")
            print("     Ubuntu: sudo apt install ffmpeg")
            print("     Windows: https://ffmpeg.org/download.html")
        
        if not checks["依赖包"]:
            response = input("\n是否自动安装Python依赖包? (y/n): ")
            if response.lower() in ['y', 'yes']:
                if install_dependencies():
                    checks["依赖包"] = True
        
        if not checks["Google Cloud凭据"]:
            print("   - 设置Google Cloud凭据:")
            print("     方法1: export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
            print("     方法2: 将凭据文件重命名为 google_credentials.json 放在当前目录")
            print("   - 参考config_example.txt了解详细配置")
    
    # 检查输入目录
    input_dir = Path("input_videos")
    if not input_dir.exists():
        input_dir.mkdir()
        print(f"\n📁 已创建输入目录: {input_dir}")
        print("   请将视频文件放入此目录")
    else:
        video_files = list(input_dir.glob("*.mp4")) + list(input_dir.glob("*.avi")) + \
                     list(input_dir.glob("*.mov")) + list(input_dir.glob("*.mkv"))
        if video_files:
            print(f"\n📁 发现 {len(video_files)} 个视频文件:")
            for video in video_files[:5]:  # 只显示前5个
                print(f"   - {video.name}")
            if len(video_files) > 5:
                print(f"   ... 还有 {len(video_files) - 5} 个文件")
        else:
            print(f"\n📁 输入目录为空: {input_dir}")
            print("   请将视频文件放入此目录")
    
    # 检查输出目录
    output_dir = Path("output_slices")
    if not output_dir.exists():
        output_dir.mkdir()
        print(f"\n📂 已创建输出目录: {output_dir}")
    
    print("\n" + "=" * 50)
    
    if all(checks.values()):
        print("✅ 环境检查通过，可以开始使用!")
        
        if len(sys.argv) > 1:
            # 如果提供了参数，直接运行
            print("\n🚀 启动批量视频切片...")
            from batch_video_to_slice import main as slice_main
            sys.exit(slice_main())
        else:
            show_usage_examples()
            
            # 询问是否直接运行
            if input_dir.exists() and list(input_dir.glob("*")):
                response = input(f"\n是否处理 {input_dir} 目录下的视频? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    sys.argv = [sys.argv[0], str(input_dir)]
                    from batch_video_to_slice import main as slice_main
                    sys.exit(slice_main())
    else:
        print("❌ 请解决环境问题后重试")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 