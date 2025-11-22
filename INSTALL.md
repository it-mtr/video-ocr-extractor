# 详细安装指南

本文档提供详细的安装步骤和常见问题解决方案。

## 📦 前置要求

### Python 环境

1. **检查 Python 版本**

```bash
python --version
# 或
python3 --version
```

推荐版本：Python 3.8 - 3.11

2. **安装 Python（如果没有）**

- **Windows**: 从 [python.org](https://www.python.org/downloads/) 下载安装
  - ⚠️ 安装时勾选 "Add Python to PATH"
  
- **Linux/Ubuntu**:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

- **macOS**:
```bash
brew install python@3.10
```

### Git（可选）

```bash
# Windows: 下载安装 https://git-scm.com/
# Linux:
sudo apt install git
# macOS:
brew install git
```

## 🔧 安装步骤

### 方法一：使用 Git（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/video-ocr-extractor.git
cd video-ocr-extractor

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装 PaddlePaddle
# Windows CPU:
pip install paddlepaddle==2.5.1 -i https://mirror.baidu.com/pypi/simple

# 5. 安装其他依赖
pip install -r requirements.txt
```

### 方法二：直接下载

1. 访问项目页面，点击 "Code" -> "Download ZIP"
2. 解压到任意目录
3. 打开命令行，进入项目目录
4. 执行步骤 2-5（同上）

## 🎮 GPU 支持（可选）

### Windows GPU 安装

#### 1. 检查显卡支持

确保你有 NVIDIA 显卡：
```bash
nvidia-smi
```

如果报错，说明没有 NVIDIA 显卡或驱动未安装。

#### 2. 安装 CUDA Toolkit

- 访问 [CUDA 下载页面](https://developer.nvidia.com/cuda-downloads)
- 选择 CUDA 11.2 或 11.8（推荐 11.8）
- 下载并安装
- 重启电脑

#### 3. 安装 cuDNN

- 访问 [cuDNN 下载页面](https://developer.nvidia.com/cudnn)（需要注册 NVIDIA 账号）
- 下载与 CUDA 版本匹配的 cuDNN（例如：cuDNN 8.x for CUDA 11.8）
- 解压文件
- 将 `bin`、`include`、`lib` 文件夹复制到 CUDA 安装目录
  - 默认路径：`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\`

#### 4. 安装 PaddlePaddle GPU 版本

```bash
pip uninstall paddlepaddle  # 先卸载 CPU 版本
pip install paddlepaddle-gpu==2.5.1 -i https://mirror.baidu.com/pypi/simple
```

#### 5. 验证 GPU 安装

```python
python
>>> import paddle
>>> paddle.utils.run_check()
# 应该显示：PaddlePaddle is installed successfully!
```

### Linux GPU 安装

```bash
# 1. 安装 CUDA（以 Ubuntu 为例）
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run

# 2. 添加环境变量
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 3. 安装 cuDNN
# 从 NVIDIA 官网下载 .deb 文件
sudo dpkg -i cudnn-local-repo-ubuntu2004-8.6.0.163_1.0-1_amd64.deb
sudo apt-get update
sudo apt-get install libcudnn8

# 4. 安装 PaddlePaddle GPU
pip install paddlepaddle-gpu==2.5.1
```

## ✅ 验证安装

### 测试 1：检查依赖

```bash
python -c "import cv2; import flask; print('依赖安装成功！')"
```

### 测试 2：检查 PaddleOCR

```bash
python -c "from paddleocr import PaddleOCR; print('PaddleOCR 安装成功！')"
```

第一次运行会自动下载模型，请耐心等待。

### 测试 3：运行程序

```bash
# 先准备一个视频文件 input_video.mp4
python process_video.py
```

## 🐛 常见问题

### 问题 1：pip 安装速度慢

**解决方案**：使用国内镜像源

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2：ModuleNotFoundError: No module named 'xxx'

**解决方案**：
```bash
pip install xxx
```

### 问题 3：PaddlePaddle 安装失败

**解决方案**：
1. 确认 Python 版本 <= 3.11
2. 使用百度镜像源
3. 尝试降级到 2.4.2：
```bash
pip install paddlepaddle==2.4.2
```

### 问题 4：GPU 不工作

**解决方案**：
1. 检查 CUDA 是否安装：`nvidia-smi`
2. 检查 cuDNN 路径是否正确
3. 查看错误信息，通常会提示缺少哪个 DLL
4. 程序会自动回退到 CPU 模式，不影响使用

### 问题 5：PermissionError: [WinError 32]

**解决方案**：
- 关闭其他可能占用数据库的程序
- 删除 `names.db` 后重试

### 问题 6：中文乱码

**解决方案**：
```bash
# Windows PowerShell:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 或使用 Windows Terminal（推荐）
```

## 🔄 更新项目

```bash
cd video-ocr-extractor
git pull origin main
pip install -r requirements.txt --upgrade
```

## 📞 获取帮助

如果以上方法都无法解决你的问题：

1. 查看 [常见问题](README.md#-常见问题)
2. 搜索 [Issues](https://github.com/your-username/video-ocr-extractor/issues)
3. 提交新 Issue 并附上：
   - 完整错误信息
   - 运行环境信息
   - 你已尝试的解决方案

---

祝安装顺利！🎉

