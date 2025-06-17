# AI Video Master 5.0

这是一个AI视频处理工具集，包含两个主要功能模块：

## 功能模块

### 1. 视频切片工具 (video_to_slice)
将视频文件切分成多个小片段的工具。

**主要文件：**
- `video_slicer.py` - 核心视频切片功能
- `google_video_analyzer.py` - Google API视频分析
- `batch_video_to_slice.py` - 批量处理视频切片
- `run.py` - 主运行脚本

### 2. 视频转字幕工具 (video_to_srt)
将视频文件转换为SRT字幕文件的工具。

**主要文件：**
- `srt_utils.py` - SRT字幕处理工具
- `dashscope_audio_analyzer.py` - DashScope音频分析
- `batch_video_to_srt.py` - 批量处理视频转字幕
- `run.py` - 主运行脚本

## 使用方法

### 视频切片
```bash
cd video_to_slice
pip install -r requirements.txt
python run.py
```

### 视频转字幕
```bash
cd video_to_srt
pip install -r requirements.txt
python run.py
```

## 配置

每个模块都包含 `config_example.txt` 文件，请根据需要复制并修改为 `config.txt`。

## 目录结构

```
demo/
├── video_to_slice/          # 视频切片模块
│   ├── input_videos/        # 输入视频文件夹
│   ├── output_slices/       # 输出切片文件夹
│   └── ...
└── video_to_srt/           # 视频转字幕模块
    ├── input_videos/        # 输入视频文件夹
    ├── output_srt/         # 输出字幕文件夹
    └── ...
```

## 注意事项

- 确保已安装所需的Python依赖
- 配置相应的API密钥（如Google API、DashScope API等）
- 视频文件放置在对应的 `input_videos` 文件夹中 