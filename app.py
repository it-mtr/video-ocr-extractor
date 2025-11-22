from flask import Flask, render_template, request, g, jsonify
import sqlite3
import math
import datetime

app = Flask(__name__)
DB_PATH = 'names.db'
ITEMS_PER_PAGE = 100  # 每页显示的条数
OFFSET_SECONDS = 19 * 60 + 20  # 偏移量：19分20秒

@app.template_filter('format_real_time')
def format_real_time_filter(seconds):
    """将录屏时间秒数加上偏移量，并格式化为 MM:SS"""
    if seconds is None:
        return ""
    total_seconds = int(seconds) + OFFSET_SECONDS
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        # 让查询结果像字典一样访问
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    total_count = 0
    is_limited = False
    
    if query:
        db = get_db()
        cursor = db.cursor()
        
        # 先获取总数
        cursor.execute("SELECT COUNT(*) FROM records WHERE name LIKE ?", ('%' + query + '%',))
        total_count = cursor.fetchone()[0]
        
        # 限制最多返回200条结果
        cursor.execute("SELECT name, timestamp_str, timestamp_seconds FROM records WHERE name LIKE ? ORDER BY timestamp_seconds LIMIT 200", ('%' + query + '%',))
        results = cursor.fetchall()
        
        # 判断是否被限制
        is_limited = total_count > 200
    
    return render_template('index.html', results=results, query=query, total_count=total_count, is_limited=is_limited)

@app.route('/all')
def all_names():
    page = request.args.get('page', 1, type=int)
    db = get_db()
    cursor = db.cursor()

    # 1. 获取总记录数
    cursor.execute("SELECT COUNT(*) FROM records")
    total_count = cursor.fetchone()[0]
    
    # 2. 计算总页数
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    
    # 3. 获取当前页的数据
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute("SELECT name, timestamp_seconds FROM records ORDER BY timestamp_seconds ASC LIMIT ? OFFSET ?", (ITEMS_PER_PAGE, offset))
    results = cursor.fetchall()

    return render_template('all_names.html', results=results, page=page, total_pages=total_pages, total_count=total_count)

# === 新增进度展示路由 ===

@app.route('/progress')
def progress_page():
    return render_template('progress.html')

@app.route('/api/progress')
def api_progress():
    db = get_db()
    cursor = db.cursor()
    
    # 获取进度信息
    progress_data = {}
    try:
        cursor.execute("SELECT * FROM video_progress WHERE id=1")
        row = cursor.fetchone()
        if row:
            progress_data = dict(row)
            
            # 计算百分比
            if progress_data['total_frames'] > 0:
                progress_data['percent'] = round((progress_data['current_frame'] / progress_data['total_frames']) * 100, 2)
                # 估算剩余时间 (简单版)
                # 实际应用中可以用 created_at 和当前时间计算速率，这里简化处理
                progress_data['current_time_str'] = str(datetime.timedelta(seconds=int(progress_data['current_frame'] / (progress_data['fps'] or 24))))
            else:
                progress_data['percent'] = 0
    except sqlite3.OperationalError:
        # 表可能还没创建
        progress_data = {'status': 'not_started', 'percent': 0}

    # 获取已识别名字总数
    try:
        cursor.execute("SELECT COUNT(*) FROM records")
        count = cursor.fetchone()[0]
        progress_data['records_count'] = count
    except:
        progress_data['records_count'] = 0

    return jsonify(progress_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
