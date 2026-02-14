---
title: "FastAPI 速成：30 分钟从零到部署"
slug: fastapi-quick-start
date: 2026-02-08
description: "不讲废话的 FastAPI 入门教程。从安装到部署，只保留你真正需要的内容。"
tags: ["FastAPI", "Python", "教程", "后端"]
---

# FastAPI 速成：30 分钟从零到部署

FastAPI 是我现在写后端的默认选择。快、简单、类型安全。

这篇不讲历史、不比较框架，直接上手。

## 安装

```bash
# 用 uv（推荐，比 pip 快 10 倍）
uv init my-api
cd my-api
uv add fastapi uvicorn

# 或者用 pip
pip install fastapi uvicorn
```

## 最小可运行代码

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

运行：

```bash
uvicorn main:app --reload
```

打开 http://localhost:8000 就能看到结果。

**自动文档**：http://localhost:8000/docs（Swagger UI）

## 请求体和数据验证

FastAPI 用 Pydantic 做数据验证，自动的：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int | None = None

@app.post("/users")
def create_user(user: User):
    # user 已经被验证过了
    return {"created": user.name}
```

发送无效数据？FastAPI 自动返回 422 + 详细错误信息。

## 查询参数

```python
@app.get("/search")
def search(q: str, limit: int = 10, skip: int = 0):
    return {"query": q, "limit": limit, "skip": skip}
```

请求：`/search?q=python&limit=20`

## 异步支持

FastAPI 原生支持 async/await：

```python
import httpx

@app.get("/fetch")
async def fetch_external():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.github.com")
        return r.json()
```

**什么时候用 async？**
- 调用外部 API
- 数据库查询（用异步驱动）
- 文件 I/O

CPU 密集任务不需要 async。

## 错误处理

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

## 中间件和 CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境要限制
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 静态文件和模板

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 响应
@app.get("/page", response_class=HTMLResponse)
def page():
    return "<h1>Hello</h1>"
```

## 部署

### 开发环境

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境（systemd）

```ini
# /etc/systemd/system/myapi.service
[Unit]
Description=My API
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/project
ExecStart=/path/to/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable myapi
sudo systemctl start myapi
```

### Nginx 反代

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 项目结构（推荐）

小项目：

```
my-api/
├── main.py
├── pyproject.toml
└── .env
```

中型项目：

```
my-api/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── users.py
│   │   └── items.py
│   └── utils.py
├── tests/
├── pyproject.toml
└── .env
```

## 常见坑

### 1. 路由顺序

```python
# ❌ 错误：/users/me 永远不会被匹配
@app.get("/users/{user_id}")
def get_user(user_id: str): ...

@app.get("/users/me")
def get_me(): ...

# ✅ 正确：具体路由放前面
@app.get("/users/me")
def get_me(): ...

@app.get("/users/{user_id}")
def get_user(user_id: str): ...
```

### 2. 同步 vs 异步混用

```python
# ❌ 在 async 函数里用同步阻塞调用
@app.get("/bad")
async def bad():
    import requests  # 阻塞！
    return requests.get("...").json()

# ✅ 用异步库
@app.get("/good")
async def good():
    async with httpx.AsyncClient() as client:
        return (await client.get("...")).json()
```

### 3. 忘记 await

```python
# ❌ 返回的是 coroutine 对象，不是结果
@app.get("/oops")
async def oops():
    return some_async_function()  # 少了 await

# ✅ 
@app.get("/ok")
async def ok():
    return await some_async_function()
```

## 下一步

- [官方文档](https://fastapi.tiangolo.com/) - 写得很好
- [SQLModel](https://sqlmodel.tiangolo.com/) - FastAPI 作者的 ORM
- [Pydantic V2](https://docs.pydantic.dev/) - 数据验证细节

---

*IndieKit 的所有后端都是 FastAPI 写的，欢迎参考源码。*
