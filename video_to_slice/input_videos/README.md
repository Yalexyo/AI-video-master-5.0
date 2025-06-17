# 输入视频目录

请将需要切片的视频文件放在此目录下。

## 支持的视频格式

- MP4 (推荐)
- AVI
- MOV
- MKV
- WMV
- FLV
- WebM
- M4V
- 3GP
- TS

## 文件要求

- 文件大小: ≤ 2GB (Google Cloud限制)
- 视频时长: 建议 ≤ 60分钟
- 分辨率: 无特殊限制
- 编码格式: 主流编码格式均支持

## 示例文件结构

```
input_videos/
├── presentation_video.mp4
├── interview_recording.mov
├── training_session.avi
└── demo_footage.mkv
```

## 使用提示

1. **文件命名**: 使用有意义的文件名，避免特殊字符
2. **文件质量**: 确保视频文件完整，无损坏
3. **网络带宽**: 大文件需要上传到Google Cloud，确保网络稳定
4. **成本控制**: 较长的视频会产生更多API费用

## 测试建议

首次使用时，建议先用较短的测试视频（1-5分钟）验证配置是否正确。 