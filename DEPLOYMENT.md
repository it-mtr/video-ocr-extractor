# 🚀 服务器部署指南

本文档详细说明如何将项目部署到生产服务器。

---

## 📋 目录

1. [服务器要求](#服务器要求)
2. [部署方案选择](#部署方案选择)
3. [Linux 服务器部署（推荐）](#linux-服务器部署推荐)
4. [Docker 部署](#docker-部署)
5. [常见问题](#常见问题)

---

## 服务器要求

### 最低配置
- **CPU**: 1 核
- **内存**: 1GB RAM
- **存储**: 5GB 可用空间
- **系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+

### 推荐配置
- **CPU**: 2 核
- **内存**: 2GB RAM
- **存储**: 10GB 可用空间
- **带宽**: 1Mbps+

---

## 部署方案选择

| 方案 | 适用场景 | 难度 | 推荐度 |
|------|---------|------|--------|
| Nginx + Gunicorn | 生产环境 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Docker | 容器化部署 | ⭐⭐ | ⭐⭐⭐⭐ |
| Apache + mod_wsgi | 传统部署 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 宝塔面板 | 快速部署 | ⭐ | ⭐⭐⭐⭐ |

---

## Linux 服务器部署（推荐）

### Nginx + Gunicorn（生产推荐）

#### 1. 连接服务器并更新系统

```bash
# SSH 连接到服务器
ssh root@your-server-ip

# 更新系统
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y                       # CentOS
```

#### 2. 安装必要软件

```bash
# 安装 Python 和 Git
sudo apt install -y python3 python3-pip python3-venv git nginx

# 安装 supervisor（进程管理）
sudo apt install -y supervisor
```

#### 3. 创建项目用户（安全考虑）

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash appuser

# 切换到该用户
sudo su - appuser
```

#### 4. 克隆项目代码

```bash
# 克隆项目
cd ~
git clone https://github.com/it-mtr/video-ocr-extractor.git
cd video-ocr-extractor
```

#### 5. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install paddlepaddle==2.5.1
pip install -r requirements.txt

# 安装生产服务器
pip install gunicorn
```

#### 6. 配置应用

编辑 `app.py`，修改为生产模式：

```python
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

#### 7. 测试 Gunicorn

```bash
# 测试运行
gunicorn -w 2 -b 127.0.0.1:5000 app:app

# 如果成功，按 Ctrl+C 停止
```

#### 8. 配置 Supervisor（进程管理）

退出到 root 用户：

```bash
exit  # 退出 appuser
```

创建 Supervisor 配置：

```bash
sudo nano /etc/supervisor/conf.d/video-ocr.conf
```

添加以下内容：

```ini
[program:video-ocr]
command=/home/appuser/video-ocr-extractor/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
directory=/home/appuser/video-ocr-extractor
user=appuser
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/video-ocr/err.log
stdout_logfile=/var/log/video-ocr/out.log
environment=PATH="/home/appuser/video-ocr-extractor/venv/bin"
```

创建日志目录：

```bash
sudo mkdir -p /var/log/video-ocr
sudo chown appuser:appuser /var/log/video-ocr
```

启动 Supervisor：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start video-ocr
```

#### 9. 配置 Nginx

创建 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/video-ocr
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或 IP

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /home/appuser/video-ocr-extractor/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点并重启 Nginx：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/video-ocr /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 10. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# CentOS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

#### 11. 配置 SSL/HTTPS（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 自动配置 SSL
sudo certbot --nginx -d your-domain.com

# 自动续期（Certbot 会自动添加 cron 任务）
```

---

## Docker 部署

### 构建和运行

```bash
# 构建镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

---

## 性能优化建议

### 1. Gunicorn 工作进程数

```bash
# 推荐公式：(2 × CPU 核心数) + 1
# 例如 2 核 CPU：
gunicorn -w 5 -b 127.0.0.1:5000 app:app
```

### 2. 数据库优化

```python
# 在 app.py 中添加连接池配置
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
```

### 3. 静态文件缓存

Nginx 配置中已包含静态文件缓存设置。

### 4. 启用 Gzip 压缩

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

---

## 常用命令

### Supervisor 管理

```bash
# 查看状态
sudo supervisorctl status

# 重启应用
sudo supervisorctl restart video-ocr

# 停止应用
sudo supervisorctl stop video-ocr

# 启动应用
sudo supervisorctl start video-ocr

# 查看日志
sudo tail -f /var/log/video-ocr/out.log
sudo tail -f /var/log/video-ocr/err.log
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重启
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 更新代码

```bash
# 切换到项目用户
sudo su - appuser
cd ~/video-ocr-extractor

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖（如有变化）
pip install -r requirements.txt

# 退出
exit

# 重启应用
sudo supervisorctl restart video-ocr
```

---

## 常见问题

### Q1: 502 Bad Gateway

**原因**：Gunicorn 未启动或端口不对

**解决**：
```bash
sudo supervisorctl status video-ocr
sudo supervisorctl restart video-ocr
```

### Q2: 权限错误

**解决**：
```bash
sudo chown -R appuser:appuser /home/appuser/video-ocr-extractor
```

### Q3: 数据库锁定

**原因**：SQLite 不支持高并发

**解决**：考虑迁移到 PostgreSQL 或 MySQL

### Q4: 内存不足

**解决**：减少 Gunicorn 工作进程数或增加服务器内存

### Q5: 无法访问

**检查**：
```bash
# 检查防火墙
sudo ufw status

# 检查端口监听
sudo netstat -tlnp | grep 5000

# 检查 Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 安全建议

1. **使用 HTTPS**：通过 Let's Encrypt 启用 SSL
2. **禁用 Debug 模式**：生产环境必须设置 `debug=False`
3. **限制访问**：使用防火墙规则
4. **定期更新**：保持系统和依赖包更新
5. **备份数据**：定期备份 `names.db` 数据库
6. **使用专用用户**：不要用 root 运行应用
7. **日志监控**：定期检查日志文件

---

## 监控和维护

### 设置监控

```bash
# 安装 htop 监控系统资源
sudo apt install htop

# 查看应用日志
tail -f /var/log/video-ocr/out.log
```

### 自动备份脚本

创建 `/home/appuser/backup.sh`：

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/appuser/backups"
mkdir -p $BACKUP_DIR

# 备份数据库
cp /home/appuser/video-ocr-extractor/names.db $BACKUP_DIR/names_$DATE.db

# 保留最近30天的备份
find $BACKUP_DIR -name "names_*.db" -mtime +30 -delete
```

添加到 crontab：

```bash
# 每天凌晨2点备份
0 2 * * * /home/appuser/backup.sh
```

---

## 需要帮助？

- 📖 查看 [README.md](README.md)
- 🐛 提交 [Issue](https://github.com/it-mtr/video-ocr-extractor/issues)
- 💬 项目讨论区

---

**祝部署顺利！** 🎉

