# 批量视频转录为SRT字幕文件

🔒 **严格质量保证版** - 只生成高质量的精确时间戳SRT文件

## 功能特性

### 🎯 核心功能
- 📹 **批量处理**: 一次性处理整个文件夹的视频文件
- 🎵 **智能音频提取**: 自动从视频中提取音频进行转录
- 📝 **精确时间戳**: 生成带有毫秒级时间戳的标准SRT字幕文件
- 🤖 **AI语音识别**: 使用阿里云DashScope API进行高精度语音转录

### 🔒 质量保证特性
- ✅ **严格验证**: 验证时间戳片段的存在性和有效性
- 🚫 **质量拒绝**: 拒绝生成低质量或无时间戳的SRT文件
- 📊 **详细统计**: 提供质量统计和错误分类报告
- 🎯 **高标准**: 90%以上有效片段比例要求，10%以下错误率限制
- 🔍 **重叠检测**: 时间戳重叠和文本缺失验证

### 📁 支持格式
- **视频格式**: MP4, MOV, AVI, MKV, WEBM
- **输出格式**: 标准SRT字幕文件
- **语言支持**: 中文 (默认), 支持多语言扩展

## 安装配置

### 1. 系统依赖

#### macOS
```bash
# 安装 ffmpeg (MoviePy 依赖)
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
# 安装 ffmpeg
sudo apt update
sudo apt install ffmpeg
```

#### Windows
1. 下载 [ffmpeg](https://ffmpeg.org/download.html)
2. 解压到程序目录
3. 将 ffmpeg 路径添加到系统 PATH 环境变量

### 2. Python依赖安装

```bash
# 安装依赖包
pip install -r requirements.txt

# 或者手动安装核心依赖
pip install dashscope>=1.13.3 moviepy>=1.0.3 requests>=2.31.0

# 可选: 安装OSS SDK (用于云存储)
pip install oss2>=2.17.0
```

### 3. 环境变量配置

#### 必需配置
创建 `.env` 文件或设置环境变量：

```bash
# 阿里云DashScope API密钥 (必需)
export DASHSCOPE_API_KEY=your_dashscope_api_key
```

#### 可选配置 (OSS云存储)
```bash
# 阿里云OSS配置 (可选，用于音频文件上传)
export OSS_ACCESS_KEY_ID=your_access_key_id
export OSS_ACCESS_KEY_SECRET=your_access_key_secret
export OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
export OSS_BUCKET_NAME=your_bucket_name
```

### 4. 获取DashScope API密钥

1. 访问 [阿里云模型服务平台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 在控制台获取API密钥
5. 确保账户有足够余额进行语音转录

## 使用方法

### 1. 目录结构

```
video_to_srt/
├── batch_video_to_srt.py      # 主程序
├── dashscope_audio_analyzer.py # DashScope分析器
├── srt_utils.py               # SRT工具函数
├── requirements.txt           # 依赖包
├── README.md                 # 说明文档
├── input_videos/             # 输入视频目录 (需创建)
│   ├── video1.mp4
│   ├── video2.mov
│   └── ...
└── output_srt/              # 输出SRT目录 (自动创建)
    ├── video1.srt
    ├── video2.srt
    └── ...
```

### 2. 基本使用

#### 使用默认目录
```bash
# 将视频文件放入 input_videos/ 目录
mkdir input_videos
cp /path/to/your/videos/* input_videos/

# 运行批量转录
python batch_video_to_srt.py
```

#### 指定输入输出目录
```bash
# 基本用法
python batch_video_to_srt.py -i /path/to/videos -o /path/to/srt

# 指定API密钥
python batch_video_to_srt.py -i videos/ -o srt/ --api_key your_dashscope_key

# 详细模式 (查看质量检查过程)
python batch_video_to_srt.py -v

# 指定支持的视频格式
python batch_video_to_srt.py --formats .mp4 .mov .avi
```

### 3. 命令行参数

```bash
python batch_video_to_srt.py [选项]

选项:
  -i, --input_dir    输入视频文件夹路径 (默认: ./input_videos)
  -o, --output_dir   输出SRT文件夹路径 (默认: ./output_srt)
  --api_key         DashScope API密钥 (可选，优先级高于环境变量)
  --formats         支持的视频格式 (默认: .mp4 .mov .avi .mkv .webm)
  -v, --verbose     详细输出模式
  -h, --help        显示帮助信息
```

## 质量保证

### 🔒 严格质量标准

本工具采用严格的质量保证机制，确保只生成高质量的SRT文件：

1. **时间戳片段验证**: 必须包含有效的时间戳片段
2. **有效片段比例**: ≥90% 的片段必须有效
3. **错误率限制**: ≤10% 的错误率
4. **重叠检测**: 检测并报告时间戳重叠问题
5. **文本完整性**: 验证每个片段都包含有效文本

### 📊 质量统计报告

处理完成后会显示详细的质量统计：

```
🎉 批量处理完成!
============================================================
📁 总文件数: 10
✅ 成功转录: 8
🔒 质量拒绝: 1
❌ 其他失败: 1
📂 输出目录: ./output_srt

📊 质量统计报告:
   总时间戳片段: 1250
   有效片段数: 1200
   总转录时长: 3600.0秒
   平均片段时长: 2.9秒
   时间戳质量率: 96.0%

🎯 质量保证总结:
   成功率: 80.0%
   质量拒绝率: 10.0%
   质量标准: 严格模式 🔒
✨ 整体质量: 优秀
```

## 文件说明

### 核心文件

- **`batch_video_to_srt.py`**: 主程序，负责批量处理和质量控制
- **`dashscope_audio_analyzer.py`**: DashScope语音转录分析器
- **`srt_utils.py`**: SRT格式转换工具函数
- **`requirements.txt`**: Python依赖包列表

### 依赖关系

```
batch_video_to_srt.py
├── dashscope_audio_analyzer.py (语音转录)
├── srt_utils.py (SRT格式转换)
├── moviepy (视频音频处理)
└── dashscope (阿里云API)
```

## 常见问题

### Q1: 提示"DashScope分析器不可用"
**A:** 检查以下配置：
1. 确认已设置 `DASHSCOPE_API_KEY` 环境变量
2. 确认已安装 `dashscope` 包：`pip install dashscope`
3. 确认API密钥有效且账户有余额

### Q2: 提示"音频提取失败"
**A:** 检查视频文件：
1. 确认视频文件包含音轨
2. 确认已安装ffmpeg：`ffmpeg -version`
3. 确认视频文件格式被支持

### Q3: 提示"质量检查失败"
**A:** 这是正常的质量保证机制：
1. 工具会拒绝生成低质量的SRT文件
2. 检查音频质量是否清晰
3. 确认语音内容不是静音或音乐

### Q4: 处理速度较慢
**A:** 转录速度取决于：
1. 视频文件大小和时长
2. 网络连接速度 (上传到云端处理)
3. DashScope API的处理队列

### Q5: OSS上传失败
**A:** OSS配置是可选的：
1. 如果没有配置OSS，会尝试备用方案
2. 配置OSS可以提高大文件的处理效率
3. 检查OSS配置是否正确

## 技术细节

### 处理流程

1. **视频扫描**: 扫描输入目录，识别支持的视频格式
2. **音频提取**: 使用MoviePy从视频中提取音频 (MP3格式)
3. **文件上传**: 将音频文件上传到阿里云OSS (或使用本地路径)
4. **语音转录**: 调用DashScope API进行语音识别
5. **结果下载**: 下载并解析转录结果JSON文件
6. **质量验证**: 严格验证时间戳片段的有效性
7. **SRT生成**: 将符合质量标准的结果转换为SRT格式
8. **文件保存**: 保存到输出目录

### API使用

- **模型**: paraformer-v2 (阿里云最新多语种模型)
- **功能**: 启用词级别时间戳、标点符号预测、ITN
- **语言**: 默认中文，支持多语言扩展
- **格式**: 支持多种音频和视频格式

## 开发信息

- **版本**: 1.0.0
- **Python要求**: ≥3.10
- **许可证**: 请参考主项目许可证
- **维护状态**: 活跃维护

## 更新日志

### v1.0.0 (2024-01-XX)
- 🎉 初始版本发布
- ✅ 实现批量视频转SRT功能
- 🔒 添加严格质量保证机制
- 📊 提供详细质量统计报告
- 📁 支持多种视频格式
- �� 集成阿里云DashScope API 