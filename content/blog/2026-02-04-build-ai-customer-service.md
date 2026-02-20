---
title: "从零构建多租户 AI 客服系统：RAG + WebSocket + 可嵌入 Widget"
slug: build-ai-customer-service
date: 2026-02-04
description: "完整的 AI 客服 SaaS 架构解析：多租户隔离、RAG 语义检索、流式响应、一行代码嵌入。附带 3000 行开源代码。"
tags: ["AI", "RAG", "SaaS", "架构", "开源"]
---


AI 客服是最直接的 LLM 落地场景之一。

这篇文章分享我做的一个多租户 AI 客服 SaaS：**3000 行代码**，支持 RAG 检索、流式响应、可嵌入 Widget。

## 为什么自己做

现成的方案（Intercom、Zendesk AI）要么贵，要么不够灵活。

我需要的是：
- 多租户 —— 一套系统服务多个客户
- 自定义知识库 —— 不是通用 GPT，是特定业务的专家
- 可嵌入 —— 一行代码加到任何网站
- 便宜 —— 用开源 LLM 或便宜的 API

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户网站                              │
│  <script src="cs.indiekit.ai/widget.js?key=xxx"></script>  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI CS SaaS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Widget   │  │ WebSocket│  │   RAG    │  │   LLM    │   │
│  │ Iframe   │──│ 流式响应  │──│ pgvector │──│ 多模型   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                      │                                      │
│                      ▼                                      │
│              ┌──────────────┐                              │
│              │  PostgreSQL  │                              │
│              │  + pgvector  │                              │
│              └──────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 后端 | FastAPI | 异步、WebSocket 原生支持 |
| 数据库 | PostgreSQL + pgvector | 向量检索 + 关系数据一体化 |
| LLM | Gemini / DeepSeek / Qwen | 便宜、效果好 |
| 嵌入模型 | text-embedding-3-small | 便宜、够用 |
| 前端 Widget | 纯 JS + Shadow DOM | 不污染宿主页面样式 |

## 多租户设计

### 数据模型

```python
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID, primary_key=True)
    name = Column(String(100))
    slug = Column(String(50), unique=True)  # my-company
    api_key = Column(String(64), unique=True)  # sk-xxx
    
    # 配置
    llm_provider = Column(String(20))  # gemini / deepseek / qwen
    llm_model = Column(String(50))
    system_prompt = Column(Text)
    
    # 限制
    monthly_quota = Column(Integer, default=10000)
    used_this_month = Column(Integer, default=0)
```

### 数据隔离

所有查询都带 `tenant_id` 过滤：

```python
# 获取当前租户的文档
docs = db.query(Document).filter(
    Document.tenant_id == current_tenant.id,
    Document.is_active == True
).all()
```

中间件自动注入租户上下文：

```python
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key:
        tenant = get_tenant_by_api_key(api_key)
        request.state.tenant = tenant
    return await call_next(request)
```

## RAG 实现

### 文档入库

```python
async def ingest_document(tenant_id: str, content: str, metadata: dict):
    # 1. 分块
    chunks = split_into_chunks(content, chunk_size=500, overlap=50)
    
    # 2. 向量化
    embeddings = await embed_texts(chunks)
    
    # 3. 存储
    for chunk, embedding in zip(chunks, embeddings):
        db.add(DocumentChunk(
            tenant_id=tenant_id,
            content=chunk,
            embedding=embedding,  # pgvector 自动处理
            metadata=metadata
        ))
    db.commit()
```

### 检索

```python
async def retrieve(tenant_id: str, query: str, top_k: int = 5):
    query_embedding = await embed_text(query)
    
    # pgvector 相似度搜索
    results = db.execute(text("""
        SELECT content, metadata,
               1 - (embedding <=> :query_vec) AS similarity
        FROM document_chunks
        WHERE tenant_id = :tenant_id
        ORDER BY embedding <=> :query_vec
        LIMIT :top_k
    """), {
        "query_vec": query_embedding,
        "tenant_id": tenant_id,
        "top_k": top_k
    })
    
    return results.fetchall()
```

### 带检索的对话

```python
async def chat(tenant_id: str, message: str, history: list):
    # 1. 检索相关文档
    docs = await retrieve(tenant_id, message, top_k=3)
    
    # 2. 构建上下文
    context = "\n\n".join([d.content for d in docs])
    
    # 3. 调用 LLM
    prompt = f"""你是一个客服助手。根据以下知识库内容回答用户问题。

知识库：
{context}

用户问题：{message}

如果知识库中没有相关信息，请诚实地说不知道。"""

    response = await llm.chat(prompt, history)
    return response
```

## WebSocket 流式响应

用户体验的关键：**打字机效果**。

```python
@app.websocket("/ws/chat/{api_key}")
async def websocket_chat(websocket: WebSocket, api_key: str):
    tenant = get_tenant_by_api_key(api_key)
    if not tenant:
        await websocket.close(code=4001)
        return
    
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data["message"]
            history = data.get("history", [])
            
            # 流式响应
            async for chunk in chat_stream(tenant.id, message, history):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
            
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
```

## 可嵌入 Widget

### 嵌入代码

用户只需要一行：

```html
<script src="https://cs.indiekit.ai/widget.js?key=sk-xxx"></script>
```

### Widget 实现

```javascript
// widget.js
(function() {
  const apiKey = new URL(document.currentScript.src).searchParams.get('key');
  
  // 创建 Shadow DOM 隔离样式
  const host = document.createElement('div');
  const shadow = host.attachShadow({ mode: 'closed' });
  
  // 注入 Widget HTML + CSS
  shadow.innerHTML = `
    <style>
      .cs-widget { position: fixed; bottom: 20px; right: 20px; ... }
      .cs-chat { ... }
    </style>
    <div class="cs-widget">
      <button class="cs-trigger">💬</button>
      <div class="cs-chat" style="display: none">
        <div class="cs-messages"></div>
        <input class="cs-input" placeholder="输入问题...">
      </div>
    </div>
  `;
  
  document.body.appendChild(host);
  
  // WebSocket 连接
  const ws = new WebSocket(`wss://cs.indiekit.ai/ws/chat/${apiKey}`);
  
  // 处理消息...
})();
```

Shadow DOM 的好处：Widget 样式完全隔离，不会被宿主页面影响。

## 用量统计

按租户按日统计，方便计费：

```python
class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    tenant_id = Column(UUID)
    date = Column(Date)
    message_count = Column(Integer)
    token_count = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'date'),
    )

async def log_usage(tenant_id: str, tokens: int):
    today = date.today()
    
    # UPSERT
    db.execute(text("""
        INSERT INTO usage_logs (tenant_id, date, message_count, token_count)
        VALUES (:tenant_id, :date, 1, :tokens)
        ON CONFLICT (tenant_id, date) 
        DO UPDATE SET 
            message_count = usage_logs.message_count + 1,
            token_count = usage_logs.token_count + :tokens
    """), {"tenant_id": tenant_id, "date": today, "tokens": tokens})
```

## 部署

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/ai_cs
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db

  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: ai_cs
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### 成本估算

| 项目 | 月成本 |
|------|--------|
| 服务器（1C2G） | $5 |
| LLM API（10k 次对话） | $3-10 |
| 向量嵌入 | $1 |
| **总计** | **~$10-20/月** |

对比 Intercom：$74/月起步。

## 开源

完整代码已开源：[GitHub: ai-cs-saas](https://github.com/indiekit/ai-cs-saas)

3000 行代码，MIT 协议，随便用。

---

*有问题欢迎讨论。下一篇会写语音 AI 客服的实现。*
