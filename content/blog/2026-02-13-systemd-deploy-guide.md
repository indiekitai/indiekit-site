---
title: "用 systemd 部署 Python 服务：最简单的生产方案"
slug: systemd-deploy-guide
date: 2026-02-13
description: "不需要 Docker，不需要 K8s。一个 systemd unit 文件就能让你的 Python 服务稳定运行。"
tags: ["部署", "systemd", "Python", "Linux"]
---

# 用 systemd 部署 Python 服务：最简单的生产方案

很多人一上来就想用 Docker、K8s。

但对于独立开发者的小项目？**一个 systemd unit 文件就够了。**

## 为什么选 systemd

- ✅ Linux 自带，不需要额外安装
- ✅ 自动重启崩溃的服务
- ✅ 开机自启动
- ✅ 日志集中管理（journalctl）
- ✅ 资源限制
- ✅ 简单到几行配置

## 准备工作

假设你有一个 FastAPI 项目：

```
/root/source/my-api/
├── src/
│   └── main.py
├── .venv/
└── pyproject.toml
```

确保手动运行没问题：

```bash
cd /root/source/my-api
source .venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

## 创建 systemd 服务

### 1. 编写 unit 文件

```bash
sudo nano /etc/systemd/system/my-api.service
```

内容：

```ini
[Unit]
Description=My API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/source/my-api
ExecStart=/root/source/my-api/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

# 环境变量（可选）
Environment="ENV=production"
Environment="SECRET_KEY=xxx"

# 或者用 env 文件
# EnvironmentFile=/root/source/my-api/.env

[Install]
WantedBy=multi-user.target
```

### 2. 启用并启动

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable my-api

# 启动服务
sudo systemctl start my-api

# 查看状态
sudo systemctl status my-api
```

## 常用命令

```bash
# 启动/停止/重启
sudo systemctl start my-api
sudo systemctl stop my-api
sudo systemctl restart my-api

# 查看状态
sudo systemctl status my-api

# 查看日志
journalctl -u my-api -f          # 实时日志
journalctl -u my-api --since today  # 今天的日志
journalctl -u my-api -n 100      # 最近 100 行

# 开机自启
sudo systemctl enable my-api     # 启用
sudo systemctl disable my-api    # 禁用
```

## 进阶配置

### 1. 多实例运行

用模板 unit 文件运行多个实例：

```bash
sudo nano /etc/systemd/system/my-api@.service
```

```ini
[Unit]
Description=My API Instance %i
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/source/my-api
ExecStart=/root/source/my-api/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port %i
Restart=always

[Install]
WantedBy=multi-user.target
```

启动多个实例：

```bash
sudo systemctl start my-api@8001
sudo systemctl start my-api@8002
sudo systemctl start my-api@8003
```

配合 Nginx 负载均衡。

### 2. 资源限制

```ini
[Service]
# 内存限制
MemoryMax=512M

# CPU 限制（百分比）
CPUQuota=50%

# 文件描述符限制
LimitNOFILE=65536
```

### 3. 安全加固

```ini
[Service]
# 只读文件系统（除了指定目录）
ReadOnlyPaths=/
ReadWritePaths=/root/source/my-api/data

# 禁止网络访问（如果不需要的话）
# PrivateNetwork=true

# 禁止获取新权限
NoNewPrivileges=true

# 私有 tmp 目录
PrivateTmp=true
```

### 4. 优雅关闭

```ini
[Service]
# 发送 SIGTERM，等待 30 秒后 SIGKILL
TimeoutStopSec=30
KillSignal=SIGTERM
```

Python 代码处理信号：

```python
import signal
import sys

def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    # 清理工作
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
```

## 配合 Nginx

```nginx
# /etc/nginx/sites-available/my-api
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/my-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 自动部署脚本

```bash
#!/bin/bash
# deploy.sh

set -e

cd /root/source/my-api

echo "Pulling latest code..."
git pull

echo "Installing dependencies..."
.venv/bin/pip install -e .

echo "Restarting service..."
sudo systemctl restart my-api

echo "Checking status..."
sleep 2
sudo systemctl status my-api --no-pager

echo "Done!"
```

## 常见问题

### 服务启动失败

```bash
# 查看详细错误
journalctl -u my-api -n 50 --no-pager
```

常见原因：
- 路径错误（WorkingDirectory、ExecStart）
- 环境变量缺失
- 端口被占用
- Python 虚拟环境路径错

### 修改配置后不生效

```bash
# 一定要执行这个
sudo systemctl daemon-reload
sudo systemctl restart my-api
```

### 权限问题

如果用非 root 用户运行：

```ini
[Service]
User=deploy
Group=deploy
```

确保该用户有代码目录的读取权限。

## IndieKit 的部署

IndieKit 的 5 个工具全是 systemd 部署：

```bash
# /etc/systemd/system/hn-digest.service
# /etc/systemd/system/uptime-ping.service
# /etc/systemd/system/webhook-relay.service
# ...
```

每个工具一个 service 文件，互不影响。

总配置行数：**~100 行**。

简单、稳定、够用。

---

*不是所有项目都需要 Docker。选择合适的工具，不是最流行的工具。*
