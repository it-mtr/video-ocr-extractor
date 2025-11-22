import cv2
import sqlite3
import datetime
from paddleocr import PaddleOCR
import os

# =================配置区域=================
VIDEO_PATH = 'input_video.mp4'  # 你的视频文件名
DB_PATH = 'names.db'            # 数据库文件名
SKIP_FRAMES = 120                # 每隔多少帧识别一次（假设视频24帧/秒，设为24即每秒识别一次）
CONFIDENCE_THRESHOLD = 0.8      # 置信度阈值，低于这个可信度的文字丢弃
# ==========================================

def init_db():
    """初始化数据库"""
    # 注意：这里会删除旧库重建，如果你想保留旧数据，请注释掉下面两行
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            print("警告: 无法删除旧数据库文件，可能是被占用了。将尝试直接写入。")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. 创建记录表 (包含 created_at)
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  timestamp_seconds REAL,
                  timestamp_str TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. 创建进度表 (只存一行数据)
    c.execute('''CREATE TABLE IF NOT EXISTS video_progress
                 (id INTEGER PRIMARY KEY,
                  total_frames INTEGER,
                  current_frame INTEGER,
                  fps REAL,
                  status TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                  
    # 初始化进度记录
    c.execute("INSERT OR IGNORE INTO video_progress (id, total_frames, current_frame, fps, status) VALUES (1, 0, 0, 0, 'ready')")
    
    conn.commit()
    return conn

def update_progress(conn, total_frames, current_frame, fps, status='running'):
    """更新进度表"""
    c = conn.cursor()
    c.execute("""UPDATE video_progress 
                 SET total_frames=?, current_frame=?, fps=?, status=?, updated_at=CURRENT_TIMESTAMP 
                 WHERE id=1""", 
              (total_frames, current_frame, fps, status))
    conn.commit()

def format_time(seconds):
    """将秒数转换为 MM:SS 格式"""
    return str(datetime.timedelta(seconds=int(seconds)))

import traceback

# ... (imports)

def process_video():
    # 1. 初始化 OCR
    print("正在初始化 OCR 模型...")
    print(">>> 正在尝试使用 GPU 加速 (RTX 4060) <<<")
    
    ocr = None
    gpu_available = False
    
    # 尝试 GPU 模式
    try:
        import numpy as np
        print("[尝试] 正在初始化 GPU 模式...")
        ocr = PaddleOCR(use_textline_orientation=True, lang="ch", use_gpu=True)
        
        # 测试 GPU 是否真的可用（用一个小图片测试）
        print("[测试] 正在测试 GPU 是否可用...")
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _ = ocr.ocr(test_img)
        
        print("[成功] GPU 模式可用！")
        gpu_available = True
    except Exception as e:
        print("\n" + "="*50)
        print("[警告] GPU 模式不可用！")
        print("="*50)
        if "cudnn" in str(e).lower():
            print("原因: 缺少 CUDNN 库 (cudnn64_8.dll)")
            print("说明: 需要安装与 CUDA 版本匹配的 CUDNN")
        else:
            print(f"原因: {str(e)[:200]}")
        print("="*50 + "\n")
        print("[切换] 正在切换到 CPU 模式...")
        
        try:
            ocr = PaddleOCR(use_textline_orientation=True, lang="ch", use_gpu=False)
            print("[成功] CPU 模式初始化成功！(速度会较慢)")
        except Exception as e2:
            print(f"[失败] CPU 模式也失败了: {e2}")
            traceback.print_exc()
            return
    
    if ocr is None:
        print("[失败] OCR 初始化失败")
        return

    # 2. 打开视频
    if not os.path.exists(VIDEO_PATH):
        print(f"错误: 找不到视频文件 {VIDEO_PATH}")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"视频加载成功: FPS={fps}, 总帧数={total_frames}")

    conn = init_db()
    c = conn.cursor()
    
    # 更新初始进度
    update_progress(conn, total_frames, 0, fps, 'running')

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 按照设定的间隔处理帧
        if frame_count % SKIP_FRAMES == 0:
            current_seconds = frame_count / fps
            time_str = format_time(current_seconds)
            
            print(f"正在处理: {time_str} ({frame_count}/{total_frames}) ...")
            
            # 实时更新进度 (每处理一帧更新一次)
            update_progress(conn, total_frames, frame_count, fps, 'running')

            # OCR 识别
            result = ocr.ocr(frame)
            
            # PaddleOCR 新版 (PaddleX pipeline) 返回结果解析
            if result and len(result) > 0 and isinstance(result[0], dict):
                data = result[0]
                texts = data.get('rec_texts', [])
                scores = data.get('rec_scores', [])
                
                for text, confidence in zip(texts, scores):
                    text = text.strip()
                    if confidence > CONFIDENCE_THRESHOLD and len(text) > 1:
                        print(f"  -> 发现: {text}")
                        # 使用 datetime.datetime.now() 显式插入时间
                        now = datetime.datetime.now()
                        c.execute("INSERT INTO records (name, timestamp_seconds, timestamp_str, created_at) VALUES (?, ?, ?, ?)",
                                  (text, current_seconds, time_str, now))
                conn.commit()
            
            # 兼容旧版结构
            elif result and isinstance(result[0], list):
                for line in result[0]:
                    if len(line) >= 2 and len(line[1]) >= 2:
                        text = line[1][0].strip()
                        confidence = line[1][1]
                        if confidence > CONFIDENCE_THRESHOLD and len(text) > 1:
                            print(f"  -> 发现: {text}")
                            now = datetime.datetime.now()
                            c.execute("INSERT INTO records (name, timestamp_seconds, timestamp_str, created_at) VALUES (?, ?, ?, ?)",
                                      (text, current_seconds, time_str, now))
                conn.commit()

        frame_count += 1

    # 完成
    update_progress(conn, total_frames, total_frames, fps, 'completed')
    cap.release()
    conn.close()
    print("处理完成！数据已存入数据库。")

if __name__ == "__main__":
    process_video()
