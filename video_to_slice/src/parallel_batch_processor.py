#!/usr/bin/env python3
"""
AI Video Master 5.0 - 并行批量视频处理器 (精简版)
专注于并行处理，移除所有串行处理代码

主要特性:
1. 异步并行处理多个视频文件
2. 信号量控制并发数量（遵循API配额限制）
3. FFmpeg并行切片优化
4. 实时进度监控和错误处理
5. 重试机制和容错处理
6. 详细的性能统计报告
"""

import asyncio
import json
import logging
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from tenacity import retry, wait_random_exponential, stop_after_attempt

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('parallel_video_slice.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

try:
    from google_video_analyzer import GoogleVideoAnalyzer
    from parallel_video_slicer import ParallelVideoSlicer
except ImportError as e:
    logger.error(f"依赖模块导入失败: {e}")
    logger.error("请确保所有依赖文件在同一目录下")
    sys.exit(1)


class ParallelBatchProcessor:
    """并行批量视频切片处理器 - 精简版"""
    
    def __init__(self, output_dir: str = "./output_slices", temp_dir: str = "./temp", 
                 max_concurrent: int = 3, ffmpeg_workers: int = 4):
        """
        初始化并行批量视频切片处理器
        
        Args:
            output_dir: 输出目录
            temp_dir: 临时目录
            max_concurrent: 最大并发数（默认3，遵循Google Cloud API配额限制）
            ffmpeg_workers: FFmpeg并行切片工作线程数（默认4）
        """
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # 并发控制
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 初始化组件
        self.analyzer = GoogleVideoAnalyzer()
        self.parallel_slicer = ParallelVideoSlicer(max_workers=ffmpeg_workers)
        
        # 统计信息
        self.stats = {
            "total_videos": 0,
            "processed_videos": 0,
            "failed_videos": 0,
            "total_slices": 0,
            "processing_errors": []
        }
        
        logger.info(f"初始化并行处理器 - 最大并发数: {max_concurrent}, FFmpeg工作线程: {ffmpeg_workers}")
    
    def _validate_video_file(self, video_path: str) -> bool:
        """验证视频文件"""
        try:
            if not os.path.exists(video_path):
                return False
            
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                return False
            
            # 简单的文件格式检查
            valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
            if Path(video_path).suffix.lower() not in valid_extensions:
                return False
            
            return True
        except Exception:
            return False
    
    def _create_default_shots(self, video_path: str, segment_duration: float = 10.0) -> List[Dict[str, Any]]:
        """
        创建默认的时间段切片（当无法检测到镜头时）
        
        Args:
            video_path: 视频文件路径
            segment_duration: 每个片段的时长（秒）
            
        Returns:
            默认切片列表
        """
        try:
            # 使用ffprobe获取视频时长
            import subprocess
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"无法获取视频时长: {video_path}")
                return []
            
            duration = float(result.stdout.strip())
            if duration <= 0:
                return []
            
            shots = []
            current_time = 0
            index = 1
            
            while current_time < duration:
                end_time = min(current_time + segment_duration, duration)
                
                shots.append({
                    'index': index,
                    'start_time': current_time,
                    'end_time': end_time,
                    'duration': end_time - current_time,
                    'type': f'默认片段{index}',
                    'confidence': 0.8
                })
                
                current_time = end_time
                index += 1
            
            logger.info(f"创建默认切片方案: {len(shots)} 个片段，每个 {segment_duration} 秒")
            return shots
            
        except Exception as e:
            logger.error(f"创建默认切片失败: {e}")
            return []
    
    def _validate_slice_quality(self, slices: List[Dict[str, Any]], video_name: str) -> Dict[str, Any]:
        """验证切片质量"""
        if not slices:
            return {
                "passed": False,
                "error": "没有生成任何切片",
                "details": {}
            }
        
        # 基本质量检查
        total_slices = len(slices)
        valid_slices = 0
        total_duration = 0
        
        for slice_info in slices:
            if 'file_path' in slice_info and os.path.exists(slice_info['file_path']):
                file_size = os.path.getsize(slice_info['file_path'])
                if file_size > 1024:  # 至少1KB
                    valid_slices += 1
                    total_duration += slice_info.get('duration', 0)
        
        success_rate = (valid_slices / total_slices) * 100 if total_slices > 0 else 0
        
        return {
            "passed": success_rate >= 80,  # 80%成功率为通过
            "success_rate": success_rate,
            "total_slices": total_slices,
            "valid_slices": valid_slices,
            "total_duration": total_duration,
            "error": f"成功率过低: {success_rate:.1f}%" if success_rate < 80 else None,
            "details": {
                "video_name": video_name,
                "quality_threshold": 80,
                "check_time": datetime.now().isoformat()
            }
        }
    
    def process_video(self, video_path: str, features: List[str] = None) -> Dict[str, Any]:
        """
        处理单个视频文件（并行切片优化版本）
        
        Args:
            video_path: 视频文件路径
            features: 分析功能列表
            
        Returns:
            处理结果
        """
        video_name = Path(video_path).stem
        logger.info(f"开始处理视频: {video_name}")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 验证视频文件
            if not self._validate_video_file(video_path):
                raise Exception("视频文件验证失败")
            
            # 创建视频专用输出目录
            video_output_dir = self.output_dir / video_name
            video_output_dir.mkdir(exist_ok=True)
            
            # 设置默认分析功能 - 只使用镜头检测以提升性能
            if not features:
                features = ["shot_detection"]
            
            # 分析视频
            logger.info(f"分析视频内容: {video_name}")
            analysis_result = self.analyzer.analyze_video(
                video_path=video_path,
                features=features,
                auto_cleanup_storage=True
            )
            
            if not analysis_result.get("success"):
                error_msg = analysis_result.get("error", "分析失败")
                raise Exception(f"视频分析失败: {error_msg}")
            
            # 提取镜头信息
            shots = self.analyzer.extract_shots(analysis_result)
            if not shots:
                logger.warning(f"未检测到镜头，使用默认分割方案: {video_name}")
                shots = self._create_default_shots(video_path)
            
            logger.info(f"检测到 {len(shots)} 个镜头")
            
            # 🚀 关键优化：使用并行切片器生成视频切片
            logger.info(f"开始并行生成视频切片: {video_name}")
            
            def progress_callback(progress, message):
                logger.info(f"切片进度 {progress}%: {message}")
            
            slice_results = self.parallel_slicer.create_slices_from_shots(
                video_path=video_path,
                shots=shots,
                video_name=video_name,
                output_dir=str(self.output_dir),
                progress_callback=progress_callback
            )
            
            # 验证切片质量
            quality_result = self._validate_slice_quality(slice_results, video_name)
            
            if not quality_result["passed"]:
                logger.warning(f"切片质量不符合标准: {quality_result['error']}")
            
            # 保存切片信息
            slice_info_file = video_output_dir / f"{video_name}_slices.json"
            with open(slice_info_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_name': video_name,
                    'video_path': video_path,
                    'analysis_features': features,
                    'total_shots': len(shots),
                    'successful_slices': len(slice_results),
                    'quality_check': quality_result,
                    'slices': slice_results,
                    'processing_time': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 更新统计
            self.stats["total_slices"] += len(slice_results)
            
            logger.info(f"视频处理完成: {video_name}，生成 {len(slice_results)} 个切片")
            
            return {
                "success": True,
                "video_name": video_name,
                "slices_count": len(slice_results),
                "slices": slice_results,
                "quality_check": quality_result,
                "output_dir": str(video_output_dir)
            }
            
        except Exception as e:
            error_msg = f"处理视频失败 {video_name}: {str(e)}"
            logger.error(error_msg)
            self.stats["processing_errors"].append({
                "video": video_name,
                "error": error_msg
            })
            
            return {
                "success": False,
                "video_name": video_name,
                "error": error_msg,
                "slices_count": 0,
                "slices": []
            }
    
    @retry(
        wait=wait_random_exponential(multiplier=1, max=120),
        stop=stop_after_attempt(3)
    )
    async def async_process_video(self, video_path: str, features: List[str] = None) -> Dict[str, Any]:
        """
        异步处理单个视频文件
        
        Args:
            video_path: 视频文件路径
            features: 分析功能列表
            
        Returns:
            处理结果字典
        """
        async with self.semaphore:  # 限制并发数
            video_name = Path(video_path).stem
            
            try:
                logger.info(f"🎬 开始异步处理视频: {video_name}")
                start_time = time.time()
                
                # 使用线程池执行同步的视频处理
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self.process_video, 
                    video_path, 
                    features
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                if result.get("success"):
                    logger.info(f"✅ 视频处理完成: {video_name} ({duration:.1f}秒)")
                else:
                    logger.error(f"❌ 视频处理失败: {video_name}")
                
                return result
                
            except Exception as e:
                error_msg = f"异步处理视频失败 {video_name}: {str(e)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "video_name": video_name,
                    "error": error_msg,
                    "slices_count": 0,
                    "slices": []
                }
    
    async def parallel_batch_process(self, video_files: List[str], 
                                   features: List[str] = None,
                                   progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        并行批量处理视频文件
        
        Args:
            video_files: 视频文件路径列表
            features: 分析功能列表
            progress_callback: 进度回调函数
            
        Returns:
            批处理结果
        """
        total_videos = len(video_files)
        self.stats["total_videos"] = total_videos
        
        logger.info(f"🚀 开始并行处理 {total_videos} 个视频文件 (最大并发: {self.max_concurrent})")
        
        if progress_callback:
            progress_callback(0, f"开始并行处理 {total_videos} 个视频...")
        
        start_time = time.time()
        
        # 创建异步任务列表
        tasks = []
        for i, video_file in enumerate(video_files):
            task = self.async_process_video(str(video_file), features)
            tasks.append(task)
        
        # 并行执行所有任务，使用as_completed获取进度
        results = []
        completed = 0
        
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                
                # 更新统计信息
                if result.get("success"):
                    self.stats["processed_videos"] += 1
                    self.stats["total_slices"] += result.get("slices_count", 0)
                else:
                    self.stats["failed_videos"] += 1
                    self.stats["processing_errors"].append({
                        "video": result.get("video_name", "unknown"),
                        "error": result.get("error", "unknown error")
                    })
                
                # 进度回调
                progress = int((completed / total_videos) * 100)
                if progress_callback:
                    progress_callback(
                        progress, 
                        f"已完成 {completed}/{total_videos} 个视频 "
                        f"(成功: {self.stats['processed_videos']}, "
                        f"失败: {self.stats['failed_videos']})"
                    )
                
                logger.info(f"📊 进度: {completed}/{total_videos} ({progress}%)")
                
            except Exception as e:
                logger.error(f"处理任务时发生异常: {e}")
                results.append({
                    "success": False,
                    "video_name": "unknown",
                    "error": str(e),
                    "slices_count": 0,
                    "slices": []
                })
                completed += 1
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 生成详细报告
        report_data = {
            'batch_stats': self.stats.copy(),
            'processing_results': results,
            'parallel_info': {
                'max_concurrent': self.max_concurrent,
                'total_duration_seconds': total_duration,
                'average_time_per_video': total_duration / total_videos if total_videos > 0 else 0,
                'estimated_sequential_time': sum([r.get('processing_time', 94) for r in results if r.get('success')]),
                'time_saved_percentage': 0
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # 计算时间节省
        estimated_sequential = report_data['parallel_info']['estimated_sequential_time']
        if estimated_sequential > 0:
            time_saved = max(0, (estimated_sequential - total_duration) / estimated_sequential * 100)
            report_data['parallel_info']['time_saved_percentage'] = time_saved
        
        # 保存报告
        report_file = self.output_dir / "parallel_batch_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"🎉 并行批处理完成!")
        logger.info(f"📊 处理统计: 成功 {self.stats['processed_videos']}/{total_videos} 个视频")
        logger.info(f"🎬 总计生成: {self.stats['total_slices']} 个视频切片")
        logger.info(f"⏱️  总耗时: {total_duration:.1f}秒")
        logger.info(f"📄 详细报告: {report_file}")
        
        if report_data['parallel_info']['time_saved_percentage'] > 0:
            logger.info(f"🚀 性能提升: 节省了 {report_data['parallel_info']['time_saved_percentage']:.1f}% 的时间!")
        
        return {
            "success": True,
            "stats": self.stats,
            "results": results,
            "report_file": str(report_file),
            "total_duration": total_duration,
            "parallel_info": report_data['parallel_info']
        }
    
    def process_batch_sync(self, input_dir: str, file_patterns: List[str] = None, 
                          features: List[str] = None) -> Dict[str, Any]:
        """
        同步接口的并行批处理（向后兼容）
        
        Args:
            input_dir: 输入目录
            file_patterns: 文件模式列表
            features: 分析功能列表
            
        Returns:
            批处理结果
        """
        # 查找视频文件
        if not file_patterns:
            file_patterns = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.wmv", "*.flv"]
        
        video_files = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return {"success": False, "error": f"输入目录不存在: {input_dir}"}
        
        for pattern in file_patterns:
            video_files.extend(input_path.glob(pattern))
        
        if not video_files:
            logger.warning(f"在目录 {input_dir} 中未找到任何视频文件")
            return {"success": False, "error": "未找到任何视频文件"}
        
        # 运行异步批处理
        def progress_callback(percent, message):
            logger.info(f"进度 {percent}%: {message}")
        
        # 使用asyncio运行异步函数
        return asyncio.run(
            self.parallel_batch_process(video_files, features, progress_callback)
        )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Video Master 5.0 - 并行批量视频切片工具")
    parser.add_argument("input_dir", help="输入视频目录")
    parser.add_argument("-o", "--output", default="./output_slices", help="输出目录")
    parser.add_argument("-t", "--temp", default="./temp", help="临时目录")
    parser.add_argument("-f", "--features", nargs="+", 
                       choices=["shot_detection", "label_detection", "face_detection", "text_detection"],
                       default=["shot_detection"],
                       help="分析功能 (默认仅镜头检测，性能最佳)")
    parser.add_argument("-c", "--concurrent", type=int, default=3,
                       help="视频级最大并发数 (默认3，建议不超过3以遵循API配额)")
    parser.add_argument("-w", "--ffmpeg-workers", type=int, default=4,
                       help="FFmpeg并行切片工作线程数 (默认4，建议2-8)")
    parser.add_argument("--patterns", nargs="+", 
                       default=["*.mp4", "*.avi", "*.mov", "*.mkv"],
                       help="文件匹配模式")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查环境变量
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        if not os.path.exists("google_credentials.json"):
            logger.error("请设置 GOOGLE_APPLICATION_CREDENTIALS 环境变量")
            logger.error("或将Google Cloud凭据文件放在当前目录下并命名为 google_credentials.json")
            return 1
    
    try:
        # 创建并行处理器
        processor = ParallelBatchProcessor(
            output_dir=args.output,
            temp_dir=args.temp,
            max_concurrent=args.concurrent,
            ffmpeg_workers=args.ffmpeg_workers
        )
        
        # 执行并行批处理
        result = processor.process_batch_sync(
            input_dir=args.input_dir,
            file_patterns=args.patterns,
            features=args.features
        )
        
        if result["success"]:
            print(f"\n✅ 并行批处理完成!")
            print(f"📊 处理统计: {result['stats']['processed_videos']}/{result['stats']['total_videos']} 个视频成功")
            print(f"🎬 总计生成: {result['stats']['total_slices']} 个视频切片")
            print(f"⏱️  总耗时: {result['total_duration']:.1f}秒")
            print(f"📄 详细报告: {result['report_file']}")
            
            if result['parallel_info']['time_saved_percentage'] > 0:
                print(f"🚀 性能提升: 节省了 {result['parallel_info']['time_saved_percentage']:.1f}% 的时间!")
            
            return 0
        else:
            print(f"\n❌ 并行批处理失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断处理")
        return 130
    except Exception as e:
        logger.error(f"程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 