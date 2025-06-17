# 输入视频目录

请将需要转录的视频文件放置在此目录中。

## 支持的视频格式

- `.mp4` - MP4视频文件
- `.mov` - QuickTime视频文件
- `.avi` - AVI视频文件
- `.mkv` - Matroska视频文件
- `.webm` - WebM视频文件

## 使用说明

1. 将视频文件复制到此目录：
   ```bash
   cp /path/to/your/videos/* input_videos/
   ```

2. 返回上级目录运行转录程序：
   ```bash
   cd ..
   python batch_video_to_srt.py
   ```

3. 转录完成后，SRT字幕文件将保存在 `output_srt/` 目录中

## 注意事项

- 确保视频文件包含音轨
- 建议视频文件名不包含特殊字符
- 大文件可能需要较长处理时间 