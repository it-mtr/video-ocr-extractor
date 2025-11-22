#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本
运行此脚本检查所有依赖是否正确安装
"""

import sys
import platform

def print_header(text):
    """打印标题"""
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50)

def check_python_version():
    """检查 Python 版本"""
    print("\n[检查] Python 版本...")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"  Python 版本: {version_str}")
    
    if version.major == 3 and 8 <= version.minor <= 11:
        print("  ✅ Python 版本符合要求 (3.8-3.11)")
        return True
    else:
        print("  ⚠️  建议使用 Python 3.8-3.11")
        return False

def check_module(module_name, import_name=None, extra_info=None):
    """检查模块是否安装"""
    if import_name is None:
        import_name = module_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', '未知')
        print(f"  ✅ {module_name}: {version}")
        if extra_info:
            extra_info(module)
        return True
    except ImportError:
        print(f"  ❌ {module_name}: 未安装")
        return False

def check_paddle_device(paddle):
    """检查 PaddlePaddle 设备支持"""
    try:
        if paddle.is_compiled_with_cuda():
            print(f"     GPU 支持: ✅ (CUDA 可用)")
        else:
            print(f"     GPU 支持: ⚠️  (仅 CPU)")
    except:
        pass

def check_opencv():
    """检查 OpenCV"""
    try:
        import cv2
        version = cv2.__version__
        print(f"  ✅ opencv-python: {version}")
        return True
    except ImportError:
        print(f"  ❌ opencv-python: 未安装")
        return False

def check_files():
    """检查必需文件"""
    import os
    print("\n[检查] 必需文件...")
    
    files = {
        'app.py': 'Web 服务主程序',
        'process_video.py': '视频处理程序',
        'requirements.txt': '依赖清单',
        'templates/index.html': '搜索页面模板',
        'templates/progress.html': '进度页面模板',
        'templates/all_names.html': '列表页面模板',
    }
    
    all_ok = True
    for file, desc in files.items():
        if os.path.exists(file):
            print(f"  ✅ {file} ({desc})")
        else:
            print(f"  ❌ {file} ({desc}) - 缺失")
            all_ok = False
    
    return all_ok

def check_video_file():
    """检查视频文件"""
    import os
    print("\n[检查] 视频文件...")
    
    if os.path.exists('input_video.mp4'):
        size_mb = os.path.getsize('input_video.mp4') / (1024*1024)
        print(f"  ✅ input_video.mp4 存在 ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ⚠️  input_video.mp4 不存在")
        print(f"     请将视频文件放入项目目录并命名为 input_video.mp4")
        return False

def main():
    """主函数"""
    print_header("视频 OCR 提取系统 - 环境检查")
    
    print(f"\n[系统信息]")
    print(f"  操作系统: {platform.system()} {platform.release()}")
    print(f"  处理器: {platform.processor()}")
    
    # 检查 Python 版本
    python_ok = check_python_version()
    
    # 检查必需模块
    print("\n[检查] Python 依赖包...")
    modules_ok = True
    modules_ok &= check_module("Flask", "flask")
    modules_ok &= check_opencv()
    modules_ok &= check_module("PaddleOCR", "paddleocr")
    modules_ok &= check_module("PaddlePaddle", "paddle", check_paddle_device)
    modules_ok &= check_module("NumPy", "numpy")
    modules_ok &= check_module("Pillow", "PIL")
    
    # 检查文件
    files_ok = check_files()
    
    # 检查视频文件
    video_ok = check_video_file()
    
    # 总结
    print_header("检查结果")
    
    if python_ok and modules_ok and files_ok:
        print("\n✅ 所有必需依赖已安装，可以开始使用！")
        print("\n[下一步]")
        print("  1. 确保 input_video.mp4 存在")
        print("  2. 运行: python app.py (启动 Web 服务)")
        print("  3. 运行: python process_video.py (处理视频)")
        print("  4. 访问: http://127.0.0.1:5000")
    else:
        print("\n⚠️  发现一些问题，请先解决：")
        if not modules_ok:
            print("\n[安装依赖]")
            print("  pip install -r requirements.txt")
        if not files_ok:
            print("\n[文件缺失]")
            print("  请确保从完整的项目仓库克隆/下载")
        if not video_ok:
            print("\n[准备视频]")
            print("  将视频文件放入项目目录并命名为 input_video.mp4")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()

