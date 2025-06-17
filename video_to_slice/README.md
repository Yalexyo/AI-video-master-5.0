# 📹 Google Video Intelligence 批量视频切片工具

## ⚡ 项目特点

**🎯 完全兼容组装工厂实现**  
本工具严格按照已实现的组装工厂(`streamlit_app/pages/2_🧱_组装工厂.py`)中的核心功能实现，确保：
- 使用相同的 Google Cloud Video Intelligence API
- 兼容 `VideoProcessor.extract_segment` 接口
- 采用相同的 FFmpeg 切片参数和质量控制
- 保持与组装工厂一致的文件命名和目录结构

**🔥 核心功能**
- 🎬 使用 Google Cloud Video Intelligence API 进行智能视频分析
- ✂️ 基于镜头检测(Shot Detection)自动切片  
- 📊 支持多种分析功能：标签检测、人脸检测、文本检测
- 🔄 批量处理多个视频文件
- 📈 质量保证机制（80%有效切片率，20%最大错误率）
- 💾 自动生成详细的处理报告和元数据

## 🏗️ 架构设计

本工具采用与组装工厂完全一致的设计模式：

```
video_to_slice/
├── batch_video_to_slice.py    # 批处理主程序（对应组装工厂批处理逻辑）
├── google_video_analyzer.py   # Google Cloud分析器（对应streamlit_app版本）
├── video_slicer.py           # 视频切片器（兼容VideoProcessor接口）
├── run.py                    # 快速启动脚本
├── requirements.txt          # 依赖包（与项目主依赖一致）
└── README.md                 # 使用说明
```

## 📋 系统要求

### 必需软件
- **Python 3.10+**
- **FFmpeg** (视频处理)
- **FFprobe** (视频信息获取)

### Google Cloud 服务
- Google Cloud 项目
- Video Intelligence API 已启用
- Service Account 凭据

## ✨ 主要功能

- 🎯 **智能镜头检测**: 使用Google Cloud Video Intelligence API自动检测视频镜头变化
- 🔄 **批量处理**: 支持批量处理多个视频文件
- 📊 **质量保证**: 内置质量验证机制，确保切片文件的有效性
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- 📈 **详细统计**: 提供处理统计和详细报告
- 🎨 **多格式支持**: 支持MP4、AVI、MOV、MKV等主流视频格式

## 🚀 快速开始

### 环境要求

- Python 3.10+
- FFmpeg (用于视频处理)
- Google Cloud账户和项目

### 安装FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
下载安装包: https://ffmpeg.org/download.html

### 安装Python依赖

```bash
pip install -r requirements.txt
```

## 🔧 Google Cloud配置

### 1. 创建Google Cloud项目

访问 [Google Cloud Console](https://console.cloud.google.com/)
1. 创建新项目或选择现有项目
2. 记录项目ID

### 2. 启用Video Intelligence API

```bash
gcloud services enable videointelligence.googleapis.com
```

或在Console中手动启用：
- 导航到 APIs & Services > Library
- 搜索 "Video Intelligence API"
- 点击启用

### 3. 创建服务账号

1. 转到 IAM & Admin > Service Accounts
2. 点击 "Create Service Account"
3. 输入账号名称和描述
4. 授予角色:
   - Video Intelligence API User
   - Storage Object Admin (如果需要处理大文件)

### 4. 下载凭据文件

1. 在服务账号页面，点击您创建的账号
2. 转到 "Keys" 选项卡
3. 点击 "Add Key" > "Create new key"
4. 选择 JSON 格式
5. 下载并保存文件

### 5. 配置凭据

**方法1: 环境变量 (推荐)**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

**方法2: 放置在工具目录**
将凭据文件重命名为 `google_credentials.json` 并放在工具目录下。

## 📖 使用指南

### 基本用法

```bash
python batch_video_to_slice.py input_videos/
```

### 高级用法

```bash
python batch_video_to_slice.py input_videos/ \
  -o output_slices/ \
  -f shot_detection label_detection \
  --patterns "*.mp4" "*.avi" \
  -v
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | 输入视频目录 | **必填** |
| `-o, --output` | 输出目录 | `./output_slices` |
| `-t, --temp` | 临时目录 | `./temp` |
| `-f, --features` | 分析功能 | `shot_detection label_detection` |
| `--patterns` | 文件匹配模式 | `*.mp4 *.avi *.mov *.mkv` |
| `-v, --verbose` | 详细输出 | `False` |

### 支持的分析功能

- `shot_detection`: 镜头检测 (推荐)
- `label_detection`: 标签检测
- `face_detection`: 人脸检测
- `text_detection`: 文本检测

## 📁 输出结构

```
output_slices/
├── video1/
│   ├── video1_slice_001_0.0s-5.2s.mp4
│   ├── video1_slice_002_5.2s-12.8s.mp4
│   ├── video1_slice_003_12.8s-20.1s.mp4
│   └── video1_slices.json
├── video2/
│   ├── video2_slice_001_0.0s-7.5s.mp4
│   ├── video2_slice_002_7.5s-15.3s.mp4
│   └── video2_slices.json
└── batch_processing_report.json
```

### 切片信息文件格式

`video_slices.json` 包含每个视频的详细切片信息：

```json
{
  "video_name": "sample_video",
  "video_path": "/path/to/original/video.mp4",
  "analysis_features": ["shot_detection", "label_detection"],
  "total_shots": 5,
  "successful_slices": 4,
  "quality_check": {
    "passed": true,
    "stats": {
      "valid_slices": 4,
      "total_duration": 45.6,
      "avg_duration": 11.4
    }
  },
  "slices": [
    {
      "index": 1,
      "file_path": "/path/to/slice.mp4",
      "filename": "video_slice_001_0.0s-5.2s.mp4",
      "start_time": 0.0,
      "end_time": 5.2,
      "duration": 5.2,
      "type": "镜头1",
      "confidence": 1.0
    }
  ],
  "processing_time": "2024-01-15T10:30:00"
}
```

## 🔍 质量保证

工具内置了多层质量检查机制：

### 1. 输入验证
- 视频文件存在性检查
- 文件格式验证
- 视频可读性测试

### 2. 切片质量检查
- 文件大小验证 (最小1KB)
- 时长合理性检查 (1-300秒)
- 文件完整性验证

### 3. 批处理统计
- 有效切片比例 ≥ 80%
- 错误率 ≤ 20%
- 最少切片数量 ≥ 2

### 4. 错误处理
- 网络连接重试 (最多3次)
- 超时保护 (20分钟)
- 详细错误日志

## 💰 成本估算

Google Cloud Video Intelligence API按分钟计费：

| 功能 | 价格/分钟 |
|------|-----------|
| 镜头检测 | $0.005 |
| 标签检测 | $0.005 |
| 文本检测 | $0.005 |
| 人脸检测 | $0.010 |

**示例计算:**
- 10分钟视频 + 镜头检测 + 标签检测 = 10 × ($0.005 + $0.005) = $0.10

*实际价格请参考 [Google Cloud官方定价](https://cloud.google.com/video-intelligence/pricing)*

## 🚨 故障排除

### 常见问题

**1. 认证错误**
```
Error: Could not automatically determine credentials
```
解决方案：
- 检查 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量
- 确认凭据文件路径正确
- 验证JSON文件格式

**2. API未启用**
```
Error: Video Intelligence API has not been used
```
解决方案：
```bash
gcloud services enable videointelligence.googleapis.com
```

**3. FFmpeg未找到**
```
Error: ffmpeg command not found
```
解决方案：
- 安装FFmpeg: `brew install ffmpeg` (macOS)
- 确认FFmpeg在PATH中: `which ffmpeg`

**4. 权限不足**
```
Error: The caller does not have permission
```
解决方案：
- 检查服务账号权限
- 添加 "Video Intelligence API User" 角色

**5. 网络连接问题**
```
Error: 无法连接到Google Cloud服务
```
解决方案：
- 检查网络连接
- 确认防火墙设置
- 验证代理配置

### 调试技巧

**1. 启用详细日志**
```bash
python batch_video_to_slice.py input_videos/ -v
```

**2. 检查处理报告**
查看 `batch_processing_report.json` 了解详细统计。

**3. 单个文件测试**
先用小文件测试配置是否正确。

## 📊 性能优化

### 1. 文件大小优化
- 大文件 (>50MB) 自动上传到Cloud Storage
- 小文件直接通过API处理
- 自动清理临时文件

### 2. 批处理优化
- 并行处理多个视频
- 智能重试机制
- 内存使用优化

### 3. 网络优化
- 自动网络连接检查
- 超时保护机制
- 错误恢复策略

## 🔧 高级配置

### 自定义切片参数

可以通过修改 `batch_video_to_slice.py` 中的参数来调整切片行为：

```python
# 默认切片时长 (当无法检测镜头时)
segment_duration = 10.0  # 秒

# 最小切片时长
min_slice_duration = 1.0  # 秒

# 质量检查阈值
min_valid_ratio = 0.8     # 80%
max_error_ratio = 0.2     # 20%
```

### 输出格式自定义

切片文件命名格式：
```python
slice_filename = f"{video_name}_slice_{index:03d}_{start_time:.1f}s-{end_time:.1f}s.mp4"
```

## 📝 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 支持基本镜头检测和切片功能
- 内置质量保证机制
- 批量处理支持

## 🤝 贡献指南

欢迎提交Issues和Pull Requests！

### 开发环境搭建

1. Fork这个仓库
2. 创建开发分支: `git checkout -b feature/new-feature`
3. 安装开发依赖: `pip install -r requirements.txt`
4. 进行修改并测试
5. 提交Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [Google Cloud Video Intelligence API文档](https://cloud.google.com/video-intelligence/docs)
- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [Python Google Cloud SDK](https://github.com/googleapis/google-cloud-python)

## 💬 支持

如果您遇到问题或有建议，请：

1. 查看故障排除部分
2. 搜索现有Issues
3. 创建新Issue并提供详细信息

---

⭐ 如果这个工具对您有帮助，请给我们一个Star！ 