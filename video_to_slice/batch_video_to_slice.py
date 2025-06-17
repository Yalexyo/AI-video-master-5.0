#!/usr/bin/env python3
"""
批量视频切片工具
使用Google Video Intelligence API分析视频并生成切片

主要功能：
1. 批量处理视频文件
2. 使用Google Cloud Video Intelligence API分析视频内容
3. 根据镜头检测(Shot Detection)自动切片
4. 支持自定义切片参数
5. 质量保证和错误处理
"""

import os
import sys
import json
import logging
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('video_slice.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

try:
    from google_video_analyzer import GoogleVideoAnalyzer
    from video_slicer import VideoSlicer
except ImportError as e:
    logger.error(f"依赖模块导入失败: {e}")
    logger.error("请确保所有依赖文件在同一目录下")
    sys.exit(1)


class BatchVideoSlicer:
    """批量视频切片处理器"""
    
    def __init__(self, output_dir: str = "./output_slices", temp_dir: str = "./temp"):
        """
        初始化批量视频切片处理器
        
        Args:
            output_dir: 输出目录
            temp_dir: 临时目录
        """
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        
        # 创建目录
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # 初始化分析器和切片器
        self.analyzer = GoogleVideoAnalyzer()
        self.slicer = VideoSlicer()
        
        # 统计信息
        self.stats = {
            "total_videos": 0,
            "processed_videos": 0,
            "failed_videos": 0,
            "total_slices": 0,
            "processing_errors": []
        }
    
    def _validate_slice_quality(self, slices: List[Dict[str, Any]], video_name: str) -> Dict[str, Any]:
        """
        验证切片质量
        
        Args:
            slices: 切片列表
            video_name: 视频名称
            
        Returns:
            验证结果
        """
        if not slices:
            return {
                "passed": False,
                "error": "没有生成任何切片",
                "stats": {},
                "details": {}
            }
        
        stats = {
            "valid_slices": 0,
            "invalid_slices": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "min_duration": float('inf'),
            "max_duration": 0
        }
        
        # 质量检查
        total_slices = len(slices)
        valid_slices = 0
        invalid_slices = 0
        total_duration = 0
        durations = []
        
        for slice_info in slices:
            duration = slice_info.get('duration', 0)
            file_path = slice_info.get('file_path', '')
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                invalid_slices += 1
                continue
                
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # 小于1KB认为无效
                invalid_slices += 1
                continue
                
            # 检查时长
            if duration <= 0 or duration > 300:  # 时长不合理
                invalid_slices += 1
                continue
            
            valid_slices += 1
            total_duration += duration
            durations.append(duration)
        
        # 计算统计数据
        if durations:
            stats.update({
                "valid_slices": valid_slices,
                "invalid_slices": invalid_slices,
                "total_duration": total_duration,
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations)
            })
        
        # 质量标准
        valid_ratio = valid_slices / total_slices if total_slices > 0 else 0
        error_ratio = invalid_slices / total_slices if total_slices > 0 else 0
        
        # 质量检查阈值
        min_valid_ratio = 0.8  # 至少80%的切片有效
        max_error_ratio = 0.2  # 错误率不超过20%
        min_slice_count = 2    # 至少2个切片
        
        if valid_ratio < min_valid_ratio:
            return {
                "passed": False,
                "error": f"有效切片比例过低: {valid_ratio:.1%} < {min_valid_ratio:.1%}",
                "stats": stats,
                "details": {"valid_ratio": valid_ratio, "error_ratio": error_ratio}
            }
        
        if error_ratio > max_error_ratio:
            return {
                "passed": False,
                "error": f"错误率过高: {error_ratio:.1%} > {max_error_ratio:.1%}",
                "stats": stats,
                "details": {"valid_ratio": valid_ratio, "error_ratio": error_ratio}
            }
        
        if valid_slices < min_slice_count:
            return {
                "passed": False,
                "error": f"有效切片数量不足: {valid_slices} < {min_slice_count}",
                "stats": stats,
                "details": {"valid_ratio": valid_ratio, "error_ratio": error_ratio}
            }
        
        return {
            "passed": True,
            "error": None,
            "stats": stats,
            "details": {
                "total_slices": total_slices,
                "valid_slices": valid_slices,
                "invalid_slices": invalid_slices,
                "valid_ratio": valid_ratio,
                "error_ratio": error_ratio,
                "total_duration": total_duration,
                "avg_duration": stats["avg_duration"],
                "min_duration": stats["min_duration"] if stats["min_duration"] != float('inf') else 0,
                "max_duration": stats["max_duration"]
            }
        }
    
    def process_video(self, video_path: str, features: List[str] = None) -> Dict[str, Any]:
        """
        处理单个视频文件
        
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
            if not self.slicer.validate_video_file(video_path):
                raise Exception("视频文件验证失败")
            
            # 创建视频专用输出目录
            video_output_dir = self.output_dir / video_name
            video_output_dir.mkdir(exist_ok=True)
            
            # 设置默认分析功能
            if not features:
                features = ["shot_detection", "label_detection"]
            
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
                # 如果没有检测到镜头，创建默认的时间段切片
                shots = self._create_default_shots(video_path)
            
            logger.info(f"检测到 {len(shots)} 个镜头")
            
            # 生成视频切片
            logger.info(f"开始生成视频切片: {video_name}")
            slice_results = []
            
            for i, shot in enumerate(shots):
                start_time = shot.get('start_time', 0)
                end_time = shot.get('end_time', start_time + 5)
                duration = end_time - start_time
                
                # 跳过过短的镜头
                if duration < 1.0:
                    logger.debug(f"跳过过短镜头 {i+1}: {duration:.2f}秒")
                    continue
                
                # 生成切片文件名
                slice_filename = f"{video_name}_slice_{i+1:03d}_{start_time:.1f}s-{end_time:.1f}s.mp4"
                slice_path = video_output_dir / slice_filename
                
                # 切片视频 - 使用兼容VideoProcessor的接口
                segment_path = self.slicer.extract_segment(
                    video_path=video_path,
                    start_time=start_time,
                    end_time=end_time,
                    segment_index=i + 1,
                    semantic_type=shot.get('type', f'镜头{i+1}'),
                    video_id=video_name,
                    output_dir=str(video_output_dir)
                )
                
                if segment_path:
                    slice_info = {
                        'index': i + 1,
                        'file_path': segment_path,
                        'filename': Path(segment_path).name,
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'type': shot.get('type', f'镜头{i+1}'),
                        'confidence': shot.get('confidence', 1.0)
                    }
                    slice_results.append(slice_info)
                    logger.debug(f"生成切片成功: {Path(segment_path).name}")
                else:
                    logger.warning(f"生成切片失败: {slice_filename}")
            
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
    
    def _create_default_shots(self, video_path: str, segment_duration: float = 10.0) -> List[Dict[str, Any]]:
        """
        当无法检测到镜头时，创建默认的时间段切片
        
        Args:
            video_path: 视频文件路径
            segment_duration: 每个片段的时长（秒）
            
        Returns:
            默认切片列表
        """
        try:
            # 获取视频时长
            duration = self.slicer.get_video_duration(video_path)
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
    
    def process_batch(self, input_dir: str, file_patterns: List[str] = None) -> Dict[str, Any]:
        """
        批量处理视频文件
        
        Args:
            input_dir: 输入目录
            file_patterns: 文件模式列表
            
        Returns:
            批处理结果
        """
        if not file_patterns:
            file_patterns = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.wmv", "*.flv"]
        
        # 查找视频文件
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
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        # 批量处理
        results = []
        self.stats["total_videos"] = len(video_files)
        
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"处理进度: {i}/{len(video_files)} - {video_file.name}")
            
            result = self.process_video(str(video_file))
            results.append(result)
            
            if result["success"]:
                self.stats["processed_videos"] += 1
            else:
                self.stats["failed_videos"] += 1
        
        # 生成批处理报告
        report_file = self.output_dir / "batch_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'batch_stats': self.stats,
                'processing_results': results,
                'generated_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"批处理完成: 成功 {self.stats['processed_videos']}/{self.stats['total_videos']} 个视频")
        logger.info(f"总计生成 {self.stats['total_slices']} 个视频切片")
        logger.info(f"处理报告已保存: {report_file}")
        
        return {
            "success": True,
            "stats": self.stats,
            "results": results,
            "report_file": str(report_file)
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量视频切片工具")
    parser.add_argument("input_dir", help="输入视频目录")
    parser.add_argument("-o", "--output", default="./output_slices", help="输出目录")
    parser.add_argument("-t", "--temp", default="./temp", help="临时目录")
    parser.add_argument("-f", "--features", nargs="+", 
                       choices=["shot_detection", "label_detection", "face_detection", "text_detection"],
                       default=["shot_detection", "label_detection"],
                       help="分析功能")
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
        # 创建批处理器
        processor = BatchVideoSlicer(
            output_dir=args.output,
            temp_dir=args.temp
        )
        
        # 执行批处理
        result = processor.process_batch(
            input_dir=args.input_dir,
            file_patterns=args.patterns
        )
        
        if result["success"]:
            print(f"\n✅ 批处理完成!")
            print(f"📊 处理统计: {result['stats']['processed_videos']}/{result['stats']['total_videos']} 个视频成功")
            print(f"🎬 总计生成: {result['stats']['total_slices']} 个视频切片")
            print(f"📄 详细报告: {result['report_file']}")
            return 0
        else:
            print(f"\n❌ 批处理失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("用户中断处理")
        return 130
    except Exception as e:
        logger.error(f"程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 