"""
视频切片器
专门处理视频切片和分割功能的模块
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class VideoSlicer:
    """视频切片处理器，与组装工厂VideoProcessor兼容"""
    
    def __init__(self):
        """初始化视频切片器"""
        self.temp_dir = Path("./temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 兼容VideoProcessor的接口
        self.segments_output_dir = Path("./output_slices")
        self.segments_output_dir.mkdir(exist_ok=True)
    
    def extract_segment(self, video_path: str, start_time: float, end_time: float, 
                       segment_index: int, semantic_type: str, video_id: str, 
                       output_dir: str = None) -> Optional[str]:
        """
        从视频中提取一个片段（兼容VideoProcessor接口）
        
        Args:
            video_path: 原始视频文件路径
            start_time: 片段开始时间（秒）
            end_time: 片段结束时间（秒）
            segment_index: 片段的索引号
            semantic_type: 片段的语义类型
            video_id: 原始视频的ID（通常是文件名，不含扩展名）
            output_dir: 可选的输出目录，如果提供，将片段保存到此目录而非默认目录
            
        Returns:
            提取的片段文件路径，如果失败则返回None
        """
        if not os.path.exists(video_path):
            logger.error(f"原始视频文件不存在: {video_path}")
            return None
        
        # 确定输出路径
        segment_filename = f"{video_id}_semantic_seg_{segment_index}_{semantic_type.replace(' ', '_')}.mp4"
        
        if output_dir:
            # 如果提供了输出目录，使用它
            os.makedirs(output_dir, exist_ok=True)
            output_path = Path(output_dir) / segment_filename
        else:
            # 否则使用默认的segments目录
            output_path = self.segments_output_dir / segment_filename
        
        logger.info(f"准备提取片段: {output_path} 从 {video_path} [{start_time:.3f}s - {end_time:.3f}s]")
        
        try:
            # 使用FFmpeg直接切分，获得更高的时间精度
            # 格式化时间为高精度格式 (HH:MM:SS.mmm)
            start_time_str = self._format_time_for_ffmpeg(start_time)
            duration = end_time - start_time
            duration_str = self._format_time_for_ffmpeg(duration)
            
            logger.info(f"FFmpeg时间参数: start={start_time_str}, duration={duration_str}")
            
            # 构建FFmpeg命令，使用高精度切分
            cmd = [
                "ffmpeg", "-y",  # 覆盖输出文件
                "-i", str(video_path),  # 输入文件
                "-ss", start_time_str,  # 精确的开始时间
                "-t", duration_str,     # 精确的持续时间（而不是结束时间）
                "-c:v", "libx264",      # 视频编码器
                "-c:a", "aac",          # 音频编码器
                "-preset", "fast",      # 编码速度
                "-crf", "23",           # 质量控制
                "-avoid_negative_ts", "make_zero",  # 避免负时间戳
                "-fflags", "+genpts",   # 生成PTS
                "-copyts",              # 复制时间戳
                "-start_at_zero",       # 从零开始
                str(output_path)
            ]
            
            logger.debug(f"执行FFmpeg命令: {' '.join(cmd)}")
            
            # 执行FFmpeg命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg切分失败，返回码: {result.returncode}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                return None
            
            # 验证输出文件
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.error(f"切分后的文件不存在或为空: {output_path}")
                return None
            
            logger.info(f"成功提取视频片段: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"提取视频片段 {output_path} 时发生错误: {type(e).__name__} - {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # 清理可能的失败文件
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception as e_remove:
                    logger.warning(f"清理失败的片段文件 {output_path} 时出错: {e_remove}")
            return None
    
    def extract_slice(
        self, 
        video_path: str, 
        output_path: str, 
        start_time: float, 
        end_time: float
    ) -> bool:
        """
        从视频中提取一个切片（简化接口）
        
        Args:
            video_path: 原始视频文件路径
            output_path: 输出切片文件路径
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）
            
        Returns:
            成功返回True，失败返回False
        """
        if not os.path.exists(video_path):
            logger.error(f"原始视频文件不存在: {video_path}")
            return False
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 计算持续时间
        duration = end_time - start_time
        if duration <= 0:
            logger.error(f"无效的时间范围: {start_time}s - {end_time}s")
            return False
        
        # 格式化时间为FFmpeg格式
        start_time_str = self._format_time_for_ffmpeg(start_time)
        duration_str = self._format_time_for_ffmpeg(duration)
        
        logger.info(f"提取切片: {Path(output_path).name} [{start_time:.3f}s - {end_time:.3f}s]")
        
        try:
            # 构建FFmpeg命令
            cmd = [
                "ffmpeg", "-y",  # 覆盖输出文件
                "-i", str(video_path),  # 输入文件
                "-ss", start_time_str,  # 开始时间
                "-t", duration_str,     # 持续时间
                "-c:v", "libx264",      # 视频编码器
                "-c:a", "aac",          # 音频编码器
                "-preset", "fast",      # 编码速度
                "-crf", "23",           # 质量控制
                "-avoid_negative_ts", "make_zero",  # 避免负时间戳
                "-fflags", "+genpts",   # 生成PTS
                str(output_path)
            ]
            
            logger.debug(f"执行FFmpeg命令: {' '.join(cmd)}")
            
            # 执行FFmpeg命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg切片失败，返回码: {result.returncode}")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                return False
            
            # 验证输出文件
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.error(f"切片文件不存在或为空: {output_path}")
                return False
            
            logger.debug(f"成功提取视频切片: {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg切片超时: {output_path}")
            return False
        except Exception as e:
            logger.error(f"提取视频切片失败: {e}")
            return False
    
    def get_video_duration(self, video_path: str) -> float:
        """
        获取视频时长
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频时长（秒），失败返回0
        """
        try:
            # 使用ffprobe获取视频信息
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"获取视频时长失败: {result.stderr}")
                return 0
            
            duration = float(result.stdout.strip())
            logger.debug(f"视频时长: {duration:.2f} 秒")
            return duration
            
        except Exception as e:
            logger.error(f"获取视频时长时出错: {e}")
            return 0
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        获取视频详细信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            import json
            
            # 使用ffprobe获取详细信息
            cmd = [
                "ffprobe", "-v", "error",
                "-show_format", "-show_streams",
                "-of", "json",
                video_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"获取视频信息失败: {result.stderr}")
                return {}
            
            info = json.loads(result.stdout)
            
            # 提取关键信息
            video_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
            
            if not video_stream:
                logger.warning(f"未找到视频流: {video_path}")
                return {}
            
            # 计算视频时长
            duration = float(info.get("format", {}).get("duration", 0))
            if duration == 0 and video_stream.get("duration"):
                duration = float(video_stream.get("duration"))
            
            # 获取分辨率
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            
            return {
                "duration": duration,
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}",
                "codec": video_stream.get("codec_name"),
                "fps": self._parse_fps(video_stream.get("r_frame_rate", "0/1")),
                "bitrate": int(video_stream.get("bit_rate", 0)),
                "format": info.get("format", {}).get("format_name", ""),
                "file_size": int(info.get("format", {}).get("size", 0))
            }
            
        except Exception as e:
            logger.error(f"获取视频信息时出错: {e}")
            return {}
    
    def validate_video_file(self, video_path: str) -> bool:
        """
        验证视频文件是否有效
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            有效返回True，无效返回False
        """
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            logger.error(f"视频文件为空: {video_path}")
            return False
        
        # 检查是否可以获取视频信息
        info = self.get_video_info(video_path)
        if not info or info.get("duration", 0) <= 0:
            logger.error(f"无法读取视频信息或视频时长为0: {video_path}")
            return False
        
        logger.debug(f"视频文件验证通过: {video_path}")
        return True
    
    def _format_time_for_ffmpeg(self, seconds: float) -> str:
        """
        将秒数格式化为FFmpeg可识别的时间格式
        
        Args:
            seconds: 秒数（可以包含小数）
            
        Returns:
            格式化的时间字符串 (HH:MM:SS.mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        # 格式化为 HH:MM:SS.mmm 格式，保留3位小数
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    
    def _parse_fps(self, fps_string: str) -> float:
        """
        解析帧率字符串
        
        Args:
            fps_string: 帧率字符串（如 "30/1"）
            
        Returns:
            帧率值
        """
        try:
            if "/" in fps_string:
                num, den = fps_string.split("/")
                return float(num) / float(den) if float(den) != 0 else 0
            else:
                return float(fps_string)
        except:
            return 0.0
    
    def create_preview_images(
        self, 
        video_path: str, 
        output_dir: str, 
        count: int = 5
    ) -> List[str]:
        """
        为视频切片创建预览图
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            count: 预览图数量
            
        Returns:
            预览图文件路径列表
        """
        preview_images = []
        
        try:
            duration = self.get_video_duration(video_path)
            if duration <= 0:
                return preview_images
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 计算时间点
            interval = duration / (count + 1)
            
            for i in range(count):
                timestamp = (i + 1) * interval
                preview_path = os.path.join(
                    output_dir, 
                    f"preview_{i+1:02d}_{timestamp:.1f}s.jpg"
                )
                
                # 使用ffmpeg提取帧
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-ss", str(timestamp),
                    "-vframes", "1",
                    "-q:v", "2",  # 高质量
                    preview_path
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and os.path.exists(preview_path):
                    preview_images.append(preview_path)
                    logger.debug(f"生成预览图: {preview_path}")
                else:
                    logger.warning(f"生成预览图失败: {preview_path}")
            
        except Exception as e:
            logger.error(f"创建预览图失败: {e}")
        
        return preview_images
    
    def optimize_slice(self, input_path: str, output_path: str) -> bool:
        """
        优化视频切片（减小文件大小，保持质量）
        
        Args:
            input_path: 输入切片路径
            output_path: 输出切片路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            # 使用ffmpeg优化视频
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", "23",  # 质量控制
                "-preset", "medium",  # 编码速度与压缩率平衡
                "-c:a", "aac",
                "-b:a", "128k",
                output_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                logger.error(f"切片优化失败: {result.stderr}")
                return False
            
            logger.info(f"切片优化成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"优化切片时出错: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的视频格式"""
        return [
            ".mp4", ".avi", ".mov", ".mkv", ".wmv", 
            ".flv", ".webm", ".m4v", ".3gp", ".ts"
        ] 