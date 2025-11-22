# 视频弹幕/字幕 OCR 提取与查询系统

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PaddleOCR](https://img.shields.io/badge/OCR-PaddleOCR-orange)

一个基于 PaddleOCR 的视频文字自动提取与查询工具

</div>

## 📖 项目简介

本项目最初用于提取《凡人修仙传》动画片尾众筹名单，帮助道友快速找到自己的名字在视频中的位置。但它的应用场景远不止于此！

**适用场景：**
- 🎬 动画/电影片尾字幕提取
- 📺 视频弹幕内容提取与分析
- 📋 会议/讲座视频中的文字记录
- 🎮 游戏视频中的弹幕/聊天记录提取
- 📝 任何包含文字的视频内容提取

## ✨ 功能特点

- **🤖 智能 OCR 识别**：基于百度 PaddleOCR，支持中英文及多语言
- **⚡ GPU/CPU 自动切换**：优先使用 GPU 加速，失败时自动回退到 CPU 模式
- **🎯 精准定位**：记录每个文字出现的精确时间戳
- **🔍 模糊搜索**：提供 Web 界面，支持快速模糊查询
- **📊 实时监控**：可视化进度条，实时查看处理状态
- **📄 分页浏览**：支持查看所有已识别内容，分页展示
- **⚙️ 灵活配置**：可自定义识别频率、置信度阈值等参数

## 🖼️ 界面预览

### 搜索界面
通过关键词快速定位文字出现的时间点

### 进度监控
实时查看视频处理进度和识别统计

## 🛠️ 环境要求

### 必需条件
- **Python**: 3.8 - 3.11（推荐 3.10）
  - ⚠️ Python 3.12+ 可能与 PaddlePaddle 存在兼容性问题
- **操作系统**: Windows / Linux / macOS
- **内存**: 建议 4GB 以上
- **存储**: 至少 2GB 空闲空间（用于模型下载）

### 可选（用于 GPU 加速）
- **NVIDIA GPU**: 支持 CUDA 的显卡
- **CUDA**: 11.2+ 或 11.8+（根据 PaddlePaddle 版本）
- **cuDNN**: 与 CUDA 版本匹配

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/video-ocr-extractor.git
cd video-ocr-extractor
```

### 2. 安装依赖

#### Windows 用户（CPU 版本）

```bash
# 安装 PaddlePaddle CPU 版本
pip install paddlepaddle==2.5.1 -i https://mirror.baidu.com/pypi/simple

# 安装其他依赖
pip install -r requirements.txt
```

#### Windows 用户（GPU 版本）

```bash
# 安装 PaddlePaddle GPU 版本（需要先安装 CUDA）
pip install paddlepaddle-gpu==2.5.1 -i https://mirror.baidu.com/pypi/simple

# 安装其他依赖
pip install -r requirements.txt
```

#### Linux/macOS 用户

```bash
# CPU 版本
pip install paddlepaddle==2.5.1

# GPU 版本（需要 CUDA）
pip install paddlepaddle-gpu==2.5.1

# 其他依赖
pip install -r requirements.txt
```

> **注意**：PaddleOCR 首次运行会自动下载模型文件（约 100MB），请保持网络畅通。

### 3. 准备视频文件

将你的视频文件放入项目根目录，命名为 `input_video.mp4`（或在 `process_video.py` 中修改文件名）。

### 4. 启动服务

#### 方式一：使用两个终端（推荐）

**终端 1 - 启动 Web 服务器：**
```bash
python app.py
```

**终端 2 - 运行视频识别：**
```bash
python process_video.py
```

然后访问：
- 🔍 搜索界面：http://127.0.0.1:5000
- 📊 进度监控：http://127.0.0.1:5000/progress
- 📋 所有记录：http://127.0.0.1:5000/all

#### 方式二：只运行识别（无 Web 界面）

```bash
python process_video.py
```

识别完成后，再启动 Web 服务查询结果。

## ⚙️ 配置说明

### 视频识别配置（`process_video.py`）

```python
# =================配置区域=================
VIDEO_PATH = 'input_video.mp4'  # 视频文件路径
DB_PATH = 'names.db'            # 数据库文件名
SKIP_FRAMES = 120               # 每隔多少帧识别一次（30fps视频下，120=4秒识别一次）
CONFIDENCE_THRESHOLD = 0.8      # 置信度阈值（0-1），低于此值的文字会被过滤
# ==========================================
```

### Web 服务配置（`app.py`）

```python
ITEMS_PER_PAGE = 50             # 每页显示条数
OFFSET_SECONDS = 19 * 60 + 20   # 时间偏移量（秒），用于修正录屏时间
```

## 📂 项目结构

```
video-ocr-extractor/
│
├── app.py                  # Flask Web 服务主程序
├── process_video.py        # 视频 OCR 识别主程序
├── requirements.txt        # Python 依赖列表
├── README.md              # 项目说明文档
├── LICENSE                # 开源协议
│
├── templates/             # HTML 模板目录
│   ├── index.html        # 搜索首页
│   ├── all_names.html    # 全部记录页
│   └── progress.html     # 进度监控页
│
├── static/               # 静态资源目录（可选）
│
├── input_video.mp4       # 待处理视频（需自行准备，不包含在仓库中）
└── names.db             # SQLite 数据库（自动生成，不包含在仓库中）
```

## 🔧 常见问题

### Q1: 提示缺少 CUDA/cuDNN 库怎么办？

**A:** 程序会自动回退到 CPU 模式。如需 GPU 加速：
1. 安装 [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. 下载匹配的 [cuDNN](https://developer.nvidia.com/cudnn)
3. 将 cuDNN 的 `bin` 目录添加到系统 PATH

### Q2: 识别速度很慢？

**A:** 
- CPU 模式下处理较慢是正常现象
- 可以增大 `SKIP_FRAMES` 参数，减少识别频率
- 建议使用 GPU 加速（可提速 5-10 倍）

### Q3: 识别准确率不高？

**A:**
- 调低 `CONFIDENCE_THRESHOLD` 参数（会增加误识别）
- 确保视频清晰度足够
- 文字大小建议不要太小

### Q4: 支持哪些视频格式？

**A:** 支持 OpenCV 能读取的所有格式：MP4、AVI、MOV、MKV 等。

### Q5: 可以识别英文/其他语言吗？

**A:** 可以！在 `process_video.py` 中修改：
```python
ocr = PaddleOCR(use_textline_orientation=True, lang="en")  # 英文
# 支持：ch, en, fr, german, korean, japan 等
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 工具
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/video-ocr-extractor/issues)
- 发送邮件至：your-email@example.com

---

<div align="center">

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！

祝道友早日找到自己的名字！🌟

</div>
