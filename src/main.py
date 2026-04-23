"""
IndieKit Site - Blog + Tools for indie hackers
"""
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import frontmatter
import markdown

import json

load_dotenv()

CONTENT_DIR = Path(__file__).parent.parent / "content"
SITE_URL = os.getenv("SITE_URL", "https://indiekit.ai")
SITE_NAME = "IndieKit"
SITE_DESC = "独立开发者的 AI 工具包 | Resources for Indie Hackers"

# Tools data for API and llms.txt
TOOLS_DATA = [
    # PostgreSQL Suite — active
    {"name": "pg-dash", "npm": "@indiekitai/pg-dash", "github": "indiekitai/pg-dash", "description": "PostgreSQL monitoring, health checks, EXPLAIN analyzer, lock monitor, migration safety — 23 MCP tools", "category": "PostgreSQL", "mcp": True},
    {"name": "pg-safe-migrate", "npm": "@indiekitai/pg-safe-migrate", "github": "indiekitai/pg-safe-migrate", "description": "Catch unsafe PostgreSQL migrations before production. JS/TS equivalent of strong_migrations (Ruby). CI-friendly, no DB required.", "category": "PostgreSQL", "mcp": True},
    # Developer Tools — active
    {"name": "env-audit", "npm": "@indiekitai/env-audit", "github": "indiekitai/env-audit", "description": "Scan codebases for env vars, generate .env.example", "category": "Developer Tools", "mcp": True},
    {"name": "llm-context", "npm": "@indiekitai/llm-context", "github": "indiekitai/llm-context", "description": "Estimate LLM context usage for codebases", "category": "Developer Tools", "mcp": True},
    {"name": "git-standup", "npm": "@indiekitai/git-standup", "github": "indiekitai/git-standup", "description": "Generate daily standup reports from git history", "category": "Developer Tools", "mcp": True},
    {"name": "clash-init", "npm": "@indiekitai/clash-init", "github": "indiekitai/clash-init", "description": "Clash/mihomo proxy config generator", "category": "Developer Tools", "mcp": True},
]

app = FastAPI(title=SITE_NAME)

# Markdown processor
md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc'])


def load_posts() -> list[dict]:
    """Load all blog posts from content/blog/"""
    posts = []
    blog_dir = CONTENT_DIR / "blog"
    
    if not blog_dir.exists():
        return posts
    
    for f in sorted(blog_dir.glob("*.md"), reverse=True):
        post = frontmatter.load(f)
        posts.append({
            "slug": f.stem,
            "title": post.get("title", f.stem),
            "date": post.get("date", ""),
            "description": post.get("description", ""),
            "tags": post.get("tags", []),
            "content": post.content,
        })
    
    return posts


def render_html(title: str, content: str, description: str = "", canonical: str = "") -> str:
    """Render HTML page with SEO meta tags."""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} | {SITE_NAME}</title>
    <meta name="description" content="{description or SITE_DESC}">
    <link rel="canonical" href="{canonical or SITE_URL}">
    <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS" href="{SITE_URL}/feed.xml">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description or SITE_DESC}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical or SITE_URL}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description or SITE_DESC}">
    
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-1QHNTKJ27T"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-1QHNTKJ27T');
    </script>
    
    <!-- Syntax Highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }}
        header {{
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        header h1 {{ margin: 0; }}
        header h1 a {{ color: #333; text-decoration: none; }}
        header nav {{ margin-top: 10px; }}
        header nav a {{ margin-right: 15px; color: #666; text-decoration: none; }}
        header nav a:hover {{ color: #000; }}
        article {{ background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        article h1 {{ margin-top: 0; }}
        article .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        article a {{ color: #0066cc; }}
        pre {{ background: #2d2d2d; color: #ccc; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #eee; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
        pre code {{ background: none; padding: 0; }}
        .post-list {{ list-style: none; padding: 0; }}
        .post-list li {{ margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .post-list h2 {{ margin: 0 0 5px; }}
        .post-list h2 a {{ color: #333; text-decoration: none; }}
        .post-list h2 a:hover {{ color: #0066cc; }}
        .post-list .meta {{ color: #666; font-size: 0.9em; }}
        .tools {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }}
        .tool {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .tool h3 {{ margin: 0 0 10px; }}
        .tool a {{ color: #0066cc; text-decoration: none; }}
        .tool-stats {{ font-size: 0.85em; color: #666; margin: 10px 0; }}
        .tool-link {{ display: inline-block; margin-top: 5px; font-weight: 500; }}
        .tool:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.15); transition: box-shadow 0.2s; }}
        .share-buttons {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }}
        .share-buttons a {{ margin-left: 10px; color: #0066cc; text-decoration: none; }}
        .share-buttons a:hover {{ text-decoration: underline; }}
        /* Article typography */
        article p {{ margin: 1.2em 0; line-height: 1.8; }}
        article h2 {{ margin-top: 2em; margin-bottom: 0.8em; padding-bottom: 0.3em; border-bottom: 1px solid #eee; }}
        article h3 {{ margin-top: 1.6em; margin-bottom: 0.6em; }}
        article h4 {{ margin-top: 1.4em; margin-bottom: 0.5em; }}
        article ul, article ol {{ padding-left: 1.5em; margin: 1em 0; }}
        article li {{ margin-bottom: 0.4em; line-height: 1.7; }}
        /* Tables */
        .table-wrapper {{ overflow-x: auto; margin: 1.5em 0; }}
        article table {{ border-collapse: collapse; width: 100%; font-size: 0.95em; }}
        article table th, article table td {{ border: 1px solid #ddd; padding: 10px 14px; text-align: left; }}
        article table th {{ background: #f5f5f5; font-weight: 600; }}
        article table tr:nth-child(even) {{ background: #fafafa; }}
        article table tr:hover {{ background: #f0f0f0; }}
        /* Blockquote */
        article blockquote {{ border-left: 4px solid #667eea; background: #f8f9fa; margin: 1.5em 0; padding: 1em 1.5em; color: #555; border-radius: 0 4px 4px 0; }}
        article blockquote p {{ margin: 0.5em 0; }}
        /* Images */
        article img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 1em 0; }}
        /* Horizontal rule */
        article hr {{ border: none; border-top: 2px solid #eee; margin: 2em 0; }}
        footer {{ text-align: center; color: #666; font-size: 0.9em; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <header>
        <h1><a href="/">🛠️ IndieKit</a></h1>
        <nav>
            <a href="/">首页</a>
            <a href="/blog">博客</a>
            <a href="/tools">工具</a>
            <a href="/mcp">MCP</a>
            <a href="/api">API</a>
            <a href="/about">关于</a>
            <a href="https://github.com/indiekitai/indiekit-site/issues/new?labels=feedback&title=Feedback:" target="_blank">💬 反馈</a>
        </nav>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p>© 2026 IndieKit.ai - Built by an AI, for indie hackers</p>
        <p>
            <a href="https://github.com/indiekitai" target="_blank">GitHub</a> · 
            <a href="https://x.com/indiekitai" target="_blank">Twitter</a> · 
            <a href="https://github.com/indiekitai/indiekit-site/issues/new?labels=feedback" target="_blank">反馈建议</a>
        </p>
    </footer>
    <script>hljs.highlightAll();</script>
</body>
</html>'''


@app.get("/", response_class=HTMLResponse)
async def home():
    posts = load_posts()[:3]
    
    posts_html = ""
    for p in posts:
        posts_html += f'''
        <li>
            <h2><a href="/blog/{p['slug']}">{p['title']}</a></h2>
            <div class="meta">{p['date']}</div>
            <p>{p['description']}</p>
        </li>
        '''
    
    content = f'''
    <article>
        <h1>独立开发者的 AI 工具包</h1>
        <p>IndieKit 是一套为独立开发者打造的轻量级工具集合。所有工具都是开源的，你可以免费使用或自行部署。</p>
        <p>这个网站本身也是用 AI 在一晚上搭建的 —— 包括 8 个工具和这个博客。</p>
    </article>

    <!-- pg-dash Landing Section -->
    <section style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #e0e0e0; border-radius: 12px; padding: 36px 32px; margin: 28px 0; box-shadow: 0 4px 24px rgba(0,0,0,0.18);">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
            <span style="font-size:2rem;">🐘</span>
            <h2 style="margin:0; color:#fff; font-size:1.7rem; letter-spacing:-0.5px;">pg-dash</h2>
            <span style="background:#4ade80; color:#14532d; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:99px; letter-spacing:0.5px;">v0.5+</span>
        </div>
        <p style="margin:0 0 6px; color:#94a3b8; font-size:0.95rem;">@indiekitai/pg-dash</p>
        <p style="margin:0 0 20px; color:#cbd5e1; font-size:1.05rem; max-width:560px;">
            PostgreSQL 全能监控工具。健康检查、EXPLAIN 分析、锁监控、迁移安全审查 —— 一条命令搞定。
        </p>

        <div style="background:#0d1117; border-radius:8px; padding:16px 20px; font-family:monospace; font-size:0.88rem; color:#c9d1d9; margin-bottom:24px; overflow-x:auto;">
            <div style="color:#6e7681; margin-bottom:8px;"># 安装</div>
            <div><span style="color:#79c0ff;">npm</span> <span style="color:#c9d1d9;">install -g @indiekitai/pg-dash</span></div>
            <div style="margin-top:12px; color:#6e7681;"># 核心命令</div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">check</span>              <span style="color:#6e7681;"># 全面健康检查</span></div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">explain</span> <span style="color:#a5d6ff;">"SELECT ..."</span>  <span style="color:#6e7681;"># EXPLAIN 可视化</span></div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">watch-locks</span>        <span style="color:#6e7681;"># 实时锁监控</span></div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">check-migration</span>    <span style="color:#6e7681;"># 迁移安全检查</span></div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">schema-diff</span>        <span style="color:#6e7681;"># Schema 对比</span></div>
            <div><span style="color:#79c0ff;">pg-dash</span> <span style="color:#ffa657;">diff-env</span>           <span style="color:#6e7681;"># 两环境 Schema 差异</span></div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-bottom:24px;">
            <div style="background:rgba(255,255,255,0.06); border-radius:8px; padding:14px 16px;">
                <div style="font-size:1.3rem; margin-bottom:4px;">📊</div>
                <div style="font-weight:600; color:#fff; margin-bottom:3px;">健康检查</div>
                <div style="font-size:0.85rem; color:#94a3b8;">缓存命中率、慢查询、连接数、未使用索引</div>
            </div>
            <div style="background:rgba(255,255,255,0.06); border-radius:8px; padding:14px 16px;">
                <div style="font-size:1.3rem; margin-bottom:4px;">🔍</div>
                <div style="font-weight:600; color:#fff; margin-bottom:3px;">EXPLAIN 分析</div>
                <div style="font-size:0.85rem; color:#94a3b8;">终端可视化执行计划，Seq Scan 一眼识别</div>
            </div>
            <div style="background:rgba(255,255,255,0.06); border-radius:8px; padding:14px 16px;">
                <div style="font-size:1.3rem; margin-bottom:4px;">🔒</div>
                <div style="font-weight:600; color:#fff; margin-bottom:3px;">锁监控</div>
                <div style="font-size:0.85rem; color:#94a3b8;">实时追踪锁等待链，定位阻塞源</div>
            </div>
            <div style="background:rgba(255,255,255,0.06); border-radius:8px; padding:14px 16px;">
                <div style="font-size:1.3rem; margin-bottom:4px;">🔌</div>
                <div style="font-weight:600; color:#fff; margin-bottom:3px;">23 个 MCP 工具</div>
                <div style="font-size:0.85rem; color:#94a3b8;">让 AI Agent 直接操作你的 PG 数据库</div>
            </div>
        </div>

        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <a href="https://github.com/indiekitai/pg-dash" target="_blank"
               style="display:inline-flex; align-items:center; gap:6px; background:#21262d; color:#c9d1d9; text-decoration:none; padding:9px 18px; border-radius:6px; font-size:0.9rem; font-weight:500; border:1px solid #30363d;">
                ⭐ GitHub
            </a>
            <a href="https://www.npmjs.com/package/@indiekitai/pg-dash" target="_blank"
               style="display:inline-flex; align-items:center; gap:6px; background:#cc3534; color:#fff; text-decoration:none; padding:9px 18px; border-radius:6px; font-size:0.9rem; font-weight:500;">
                📦 npm
            </a>
            <a href="/tools#pg-dash"
               style="display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.1); color:#cbd5e1; text-decoration:none; padding:9px 18px; border-radius:6px; font-size:0.9rem; font-weight:500;">
                → 完整文档
            </a>
        </div>
    </section>

    <h2>🔧 工具</h2>
    <div class="tools">
        <div class="tool">
            <h3>📰 HN Digest</h3>
            <p>AI 生成的中文 Hacker News 每日精选</p>
            <a href="https://hn.indiekit.ai">→ 访问</a>
        </div>
        <div class="tool">
            <h3>📊 Uptime Ping</h3>
            <p>简单的 API 健康监控 + Telegram 告警</p>
            <a href="https://up.indiekit.ai">→ 访问</a>
        </div>
        <div class="tool">
            <h3>🔗 Webhook Relay</h3>
            <p>接收 Webhook 转发到 Telegram</p>
            <a href="https://hook.indiekit.ai">→ 访问</a>
        </div>
        <div class="tool">
            <h3>🔗 Tiny Link</h3>
            <p>短链接服务 + 点击统计</p>
            <a href="https://s.indiekit.ai">→ 访问</a>
        </div>
        <div class="tool">
            <h3>📋 Quick Paste</h3>
            <p>代码分享 + 语法高亮</p>
            <a href="https://p.indiekit.ai">→ 访问</a>
        </div>
        <div class="tool">
            <h3>🤖 AI CS SaaS</h3>
            <p>多租户 AI 客服 + RAG 检索</p>
            <a href="https://cs.indiekit.ai/docs">→ API 文档</a>
        </div>
        <div class="tool" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>🔌 MCP Server</h3>
            <p>让 AI Agent 直接调用工具</p>
            <a href="/mcp" style="color: white;">→ 了解更多</a>
        </div>
        <div class="tool">
            <h3>📄 Doc2MD</h3>
            <p>PDF/Word/网页 → Markdown</p>
            <p class="tool-stats">✨ URL 前缀模式：d.indiekit.ai/https/任意网址</p>
            <a href="https://d.indiekit.ai/docs">→ API 文档</a>
        </div>
    </div>
    
    <h2>📝 最新文章</h2>
    <ul class="post-list">
        {posts_html if posts_html else '<li>暂无文章</li>'}
    </ul>
    '''
    
    return render_html("首页", content)


@app.get("/blog", response_class=HTMLResponse)
async def blog_list():
    posts = load_posts()
    
    posts_html = ""
    for p in posts:
        posts_html += f'''
        <li>
            <h2><a href="/blog/{p['slug']}">{p['title']}</a></h2>
            <div class="meta">{p['date']} · {', '.join(p['tags']) if p['tags'] else '未分类'}</div>
            <p>{p['description']}</p>
        </li>
        '''
    
    content = f'''
    <h1>博客</h1>
    <ul class="post-list">
        {posts_html if posts_html else '<li>暂无文章，敬请期待...</li>'}
    </ul>
    '''
    
    return render_html("博客", content, "独立开发者经验分享、教程、工具推荐", f"{SITE_URL}/blog")


@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(slug: str):
    posts = load_posts()
    post = next((p for p in posts if p['slug'] == slug), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    md.reset()
    html_content = md.convert(post['content'])
    
    # 阅读时间：中文 400 字/分钟，英文 200 词/分钟
    word_count = len(post['content'])
    read_time = max(1, round(word_count / 400))
    
    post_url = f"{SITE_URL}/blog/{slug}"
    share_text = post['title'].replace('"', '&quot;')
    
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post['title'],
        "datePublished": str(post['date']),
        "author": {"@type": "Organization", "name": "IndieKit"},
        "url": post_url,
    }, ensure_ascii=False)

    content = f'''
    <script type="application/ld+json">{json_ld}</script>
    <article>
        <h1>{post['title']}</h1>
        <div class="meta">{post['date']} · {read_time} 分钟阅读 · {', '.join(post['tags']) if post['tags'] else '未分类'}</div>
        {html_content}
        <div class="share-buttons">
            <span>分享到：</span>
            <a href="https://twitter.com/intent/tweet?text={share_text}&url={post_url}" target="_blank" rel="noopener">Twitter</a>
            <a href="https://www.linkedin.com/shareArticle?mini=true&url={post_url}&title={share_text}" target="_blank" rel="noopener">LinkedIn</a>
            <a href="https://news.ycombinator.com/submitlink?u={post_url}&t={share_text}" target="_blank" rel="noopener">HN</a>
        </div>
    </article>
    '''
    
    return render_html(post['title'], content, post['description'], post_url)


@app.get("/tools", response_class=HTMLResponse)
async def tools():
    content = '''
    <h1>工具</h1>
    <p>所有工具都是免费使用的。轻量、快速、无需注册。</p>
    
    <div class="tools">
        <div class="tool">
            <h3>📰 HN Digest</h3>
            <p>AI 自动抓取 Hacker News 热门文章，生成中文摘要。每天更新，帮你快速了解科技圈动态。</p>
            <p class="tool-stats">🔄 每日更新 · 📖 AI 中文摘要 · ⏱️ 节省 30 分钟/天</p>
            <p><a href="https://hn.indiekit.ai" class="tool-link">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>📊 Uptime Ping</h3>
            <p>监控你的 API 和网站是否正常运行。支持 Telegram 告警，服务挂了第一时间通知你。</p>
            <p class="tool-stats">⏱️ 1 分钟检测间隔 · 📱 Telegram 告警 · 📈 可用率统计</p>
            <p><a href="https://up.indiekit.ai" class="tool-link">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>🔔 Webhook Relay</h3>
            <p>接收来自 GitHub、Stripe 等服务的 Webhook，转发到你的 Telegram。再也不用盯着后台看了。</p>
            <p class="tool-stats">🔗 一键创建端点 · 📱 即时通知 · 📝 请求日志</p>
            <p><a href="https://hook.indiekit.ai" class="tool-link">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>🔗 Tiny Link</h3>
            <p>自托管的短链接服务。支持点击统计、自定义短码。你的数据你做主。</p>
            <p class="tool-stats">📊 点击统计 · ✏️ 自定义短码 · 🔒 数据自主</p>
            <p><a href="https://s.indiekit.ai" class="tool-link">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>📋 Quick Paste</h3>
            <p>代码分享工具，支持语法高亮、阅后即焚。分享代码片段的最佳选择。</p>
            <p class="tool-stats">🎨 语法高亮 · ⏰ 自动过期 · 📦 无需登录</p>
            <p><a href="https://p.indiekit.ai" class="tool-link">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>🤖 AI CS SaaS</h3>
            <p>多租户 AI 客服系统。上传知识库，一行代码嵌入 Widget，让你的网站拥有智能客服。</p>
            <p class="tool-stats">🧠 RAG 语义检索 · 💬 流式响应 · 🏢 多租户隔离</p>
            <p><a href="https://cs.indiekit.ai/docs" class="tool-link">→ API 文档</a></p>
        </div>
        <div class="tool" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>🔌 MCP Server</h3>
            <p>让 AI Agent 直接使用 IndieKit 工具。支持 Claude Desktop、Cursor 等 MCP 兼容客户端。</p>
            <p class="tool-stats" style="color: rgba(255,255,255,0.9);">🤖 7 个工具 · 🔗 标准协议 · ⚡ 即装即用</p>
            <p><a href="/mcp" class="tool-link" style="color: white;">→ 了解更多</a></p>
        </div>
        <div class="tool">
            <h3>📄 Doc2MD</h3>
            <p>文档转 Markdown 服务。支持 PDF、Word、HTML、网页。URL 前缀模式：<code>d.indiekit.ai/https/任意网址</code>。三层转换管道 + markdown.new fallback。</p>
            <p class="tool-stats">✨ URL 前缀 · 📑 多格式 · 🔄 自动 Fallback · ⚡ REST + MCP</p>
            <p><a href="https://d.indiekit.ai/docs" class="tool-link">→ API 文档</a></p>
        </div>
    </div>
    
    <h2>📦 npm 工具包</h2>
    <p>所有工具都有 CLI + MCP Server + JSON 输出。<code>npm install</code> 即用。</p>
    <p><strong>一键安装所有 skills：</strong> <code>pi install npm:@indiekitai/pi-skills</code></p>
    '''

    # Dynamically add npm tools grouped by category
    categories = {}
    for tool in TOOLS_DATA:
        cat = tool.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool)

    category_icons = {"PostgreSQL": "🐘", "Developer Tools": "🛠", "Terminal": "🎨", "Automation": "🤖", "Meta": "📦"}

    for cat, tools in categories.items():
        icon = category_icons.get(cat, "📦")
        content += f'<h3>{icon} {cat}</h3><div class="tools">'
        for t in tools:
            gh_link = f'<a href="https://github.com/{t["github"]}" target="_blank">GitHub</a>' if t.get("github") else ""
            npm_link = f'<code>npx {t["npm"]}</code>' if t.get("npm") else ""
            mcp_badge = ' · 🔌 MCP' if t.get("mcp") else ""
            content += f'''
        <div class="tool" id="{t['name']}">
            <h4>{t['name']}</h4>
            <p>{t['description']}</p>
            <p class="tool-stats">{npm_link}{mcp_badge}</p>
            <p>{gh_link}</p>
        </div>'''
        content += '</div>'

    content += f'''
    <h2>技术栈</h2>
    <p>Web 工具：Python + FastAPI。npm 工具包：TypeScript。全部开源。</p>
    <p>GitHub: <a href="https://github.com/indiekitai">github.com/indiekitai</a> · npm: <a href="https://www.npmjs.com/org/indiekitai">@indiekitai</a></p>
    '''

    return render_html("工具", content, "免费开源的独立开发者工具集合 — 18 个 npm 包 + Web 工具", f"{SITE_URL}/tools")


@app.get("/mcp", response_class=HTMLResponse)
async def mcp_page():
    content = '''
    <article>
        <h1>🔌 IndieKit MCP Server</h1>
        <p class="lead">让 AI Agent 直接使用 IndieKit 工具。基于 <a href="https://modelcontextprotocol.io">Model Context Protocol</a> 标准。</p>
        
        <h2>什么是 MCP？</h2>
        <p>MCP (Model Context Protocol) 是 Anthropic 推出的开放协议，定义了 AI 和外部工具之间的标准通信方式。到 2026 年初已成为事实标准，OpenAI、Google、Microsoft 全部跟进。</p>
        <p>简单说：<strong>MCP 让 AI 能直接调用你的工具，不需要人工操作界面。</strong></p>
        
        <h2>安装</h2>
        <pre><code class="language-bash"># 使用 pip
pip install indiekit-mcp

# 或使用 uv
uv pip install indiekit-mcp</code></pre>
        
        <h2>配置 Claude Desktop</h2>
        <p>编辑配置文件：</p>
        <ul>
            <li>macOS: <code>~/Library/Application Support/Claude/claude_desktop_config.json</code></li>
            <li>Windows: <code>%APPDATA%\\Claude\\claude_desktop_config.json</code></li>
        </ul>
        <pre><code class="language-json">{
  "mcpServers": {
    "indiekit": {
      "command": "indiekit-mcp"
    }
  }
}</code></pre>
        <p>重启 Claude Desktop 即可使用。</p>
        
        <h2>可用工具</h2>
        <table>
            <thead>
                <tr><th>工具</th><th>功能</th></tr>
            </thead>
            <tbody>
                <tr><td><code>hn_digest</code></td><td>获取 Hacker News 每日中文摘要</td></tr>
                <tr><td><code>uptime_check</code></td><td>检查网站/API 是否在线</td></tr>
                <tr><td><code>uptime_status</code></td><td>获取所有监控端点状态</td></tr>
                <tr><td><code>shorten_url</code></td><td>创建短链接</td></tr>
                <tr><td><code>get_link_stats</code></td><td>获取短链接点击统计</td></tr>
                <tr><td><code>create_paste</code></td><td>创建代码片段分享</td></tr>
                <tr><td><code>get_paste</code></td><td>获取代码片段内容</td></tr>
            </tbody>
        </table>
        
        <h2>使用示例</h2>
        <p>配置好后，直接对 Claude 说：</p>
        <ul>
            <li>"帮我看看今天 Hacker News 有什么热门"</li>
            <li>"检查一下 https://example.com 是否在线"</li>
            <li>"把这个链接缩短：https://very-long-url.com/..."</li>
            <li>"帮我创建一个 Python 代码片段"</li>
        </ul>
        <p>Claude 会自动调用对应的 IndieKit 工具，返回结果。</p>
        
        <h2>为什么需要 MCP？</h2>
        <blockquote>
            <p>"PC 软件为手机重做了一遍，现在轮到 Agent 了。"</p>
            <p>— <a href="https://twitter.com/dotey">@dotey</a></p>
        </blockquote>
        <p>GUI 是给人用的，Agent 需要结构化的接口。MCP 就是给 Agent 开的正门，比让 AI 模拟点击界面高效 10 倍。</p>
        
        <h2>源码</h2>
        <p><a href="https://github.com/indiekitai/indiekit-mcp">github.com/indiekitai/indiekit-mcp</a></p>
        
        <h2>其他 MCP Server</h2>
        <ul>
            <li><a href="https://github.com/indiekitai/notion-mcp">notion-mcp</a> - 让 Agent 管理你的 Notion</li>
            <li><a href="https://github.com/indiekitai/doc2md">doc2md</a> - 文档转 Markdown（含 MCP Server）</li>
        </ul>
    </article>
    '''
    
    return render_html("MCP Server", content, "IndieKit MCP Server - 让 AI Agent 直接使用 IndieKit 工具", f"{SITE_URL}/mcp")


@app.get("/membership", response_class=HTMLResponse)
async def membership():
    """会员页面"""
    membership_file = CONTENT_DIR / "membership.md"
    if not membership_file.exists():
        raise HTTPException(status_code=404, detail="页面不存在")
    
    content_raw = membership_file.read_text()
    
    # 解析 frontmatter
    if content_raw.startswith('---'):
        parts = content_raw.split('---', 2)
        if len(parts) >= 3:
            content_body = parts[2].strip()
        else:
            content_body = content_raw
    else:
        content_body = content_raw
    
    md.reset()
    html_content = md.convert(content_body)
    
    content = f'''
    <article>
        {html_content}
        <div id="subscribe" style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
            <h3>🚀 即将上线</h3>
            <p>IndieKit 会员正在准备中，敬请期待！</p>
            <p>想第一时间知道？关注我们的 <a href="https://twitter.com/indiekitai">Twitter</a></p>
        </div>
    </article>
    '''
    
    return render_html("IndieKit 会员", content, "每日 AI 开发精选 + 独家工具模板", f"{SITE_URL}/membership")


@app.get("/api", response_class=HTMLResponse)
async def api_docs():
    """API 文档页面"""
    api_file = Path("/root/source/side-projects/API.md")
    if not api_file.exists():
        raise HTTPException(status_code=404, detail="API 文档不存在")
    
    content_raw = api_file.read_text()
    md.reset()
    html_content = md.convert(content_raw)
    
    content = f'''
    <article>
        {html_content}
    </article>
    '''
    
    return render_html("API Reference", content, "IndieKit API 文档 - 所有服务的 JSON API 接口", f"{SITE_URL}/api")


@app.get("/about", response_class=HTMLResponse)
async def about():
    content = '''
    <article>
        <h1>关于 IndieKit</h1>
        <p>IndieKit 是一个由 AI 驱动的独立开发者工具集合。</p>
        
        <h2>起源</h2>
        <p>2026 年 2 月 13 日，一个 AI 助手用一天时间构建了 8 个完整的工具，总计 7000+ 行代码，全部开源并发布到 PyPI。这就是 IndieKit。</p>
        
        <h2>理念</h2>
        <ul>
            <li><strong>轻量</strong>：每个工具都尽可能简单，只做一件事</li>
            <li><strong>自托管</strong>：所有工具都可以自己部署，数据完全掌控</li>
            <li><strong>开源</strong>：代码公开，随意修改</li>
        </ul>
        
        <h2>技术栈</h2>
        <ul>
            <li>Python + FastAPI</li>
            <li>JSON 文件存储（无需数据库）</li>
            <li>Cloudflare（DNS + CDN + SSL）</li>
            <li>DigitalOcean（服务器）</li>
        </ul>
        
        <h2>联系</h2>
        <p>有问题或建议？欢迎通过以下方式联系：</p>
        <ul>
            <li>Twitter: <a href="https://twitter.com/indiekitai">@indiekitai</a></li>
            <li>GitHub: <a href="https://github.com/indiekitai">github.com/indiekitai</a></li>
        </ul>
    </article>
    '''
    
    return render_html("关于", content, "关于 IndieKit - 独立开发者的 AI 工具包", f"{SITE_URL}/about")


@app.get("/health")
async def health():
    return {"status": "ok"}


# Sitemap for SEO
@app.get("/sitemap.xml")
async def sitemap():
    posts = load_posts()
    
    urls = [
        f"<url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>",
        f"<url><loc>{SITE_URL}/blog</loc><changefreq>daily</changefreq><priority>0.8</priority></url>",
        f"<url><loc>{SITE_URL}/tools</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>",
        f"<url><loc>{SITE_URL}/mcp</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>",
        f"<url><loc>{SITE_URL}/about</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>",
    ]
    
    for p in posts:
        urls.append(f"<url><loc>{SITE_URL}/blog/{p['slug']}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>")
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>'''
    
    from fastapi.responses import Response
    return Response(content=xml, media_type="application/xml")


# RSS Feed
@app.get("/feed.xml")
@app.get("/rss.xml")
async def rss_feed():
    from fastapi.responses import Response
    posts = load_posts()
    
    items = []
    for p in posts[:20]:  # Last 20 posts
        pub_date = ""
        if p.get("date"):
            try:
                d = p["date"]
                if isinstance(d, str):
                    d = datetime.strptime(d, "%Y-%m-%d")
                pub_date = d.strftime("%a, %d %b %Y 00:00:00 GMT")
            except:
                pub_date = ""
        
        # Escape XML special chars
        title = str(p.get("title", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        desc = str(p.get("description", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        items.append(f"""
    <item>
      <title>{title}</title>
      <link>{SITE_URL}/blog/{p['slug']}</link>
      <description>{desc}</description>
      <guid>{SITE_URL}/blog/{p['slug']}</guid>
      {f'<pubDate>{pub_date}</pubDate>' if pub_date else ''}
    </item>""")
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_DESC}</description>
    <language>zh-CN</language>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    {''.join(items)}
  </channel>
</rss>"""
    
    return Response(content=xml, media_type="application/xml")


@app.get("/robots.txt")
async def robots():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
""")


# llms.txt - AI agent friendly (llmstxt.org standard)
@app.get("/llms.txt")
async def llms_txt():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("""# IndieKit

> Open-source developer tools that make developers' lives easier.

## Tools

### PostgreSQL Suite
- [pg-inspect](https://indiekit.ai/tools#pg-inspect): PostgreSQL schema inspection — tables, indexes, functions, enums, constraints. `npx @indiekitai/pg-inspect --url postgres://...`
- [pg-diff](https://indiekit.ai/tools#pg-diff): Compare two PostgreSQL schemas, generate migration SQL. `npx @indiekitai/pg-diff --from db1 --to db2`
- [pg-top](https://indiekit.ai/tools#pg-top): Real-time PostgreSQL activity — running queries, locks, blocking chains. `npx @indiekitai/pg-top --url postgres://...`
- [pg-toolkit](https://indiekit.ai/tools#pg-toolkit): Unified CLI for all PG tools above. `npx @indiekitai/pg-toolkit health|inspect|diff|top`
- [pgcomplete](https://indiekit.ai/tools#pgcomplete): Context-aware SQL auto-completion — knows your tables, columns, functions. `npx @indiekitai/pgcomplete --url postgres://...`
- [pg2ts](https://indiekit.ai/tools#pg2ts): Generate TypeScript interfaces from PostgreSQL schemas. `python pg2ts.py --url postgres://... -o types.ts`

### Developer Tools
- [env-audit](https://indiekit.ai/tools#env-audit): Scan codebases for env var usage across Python/Node/Go/Rust/Shell/Docker, generate .env.example. `python env_audit.py . --json`
- [throttled](https://indiekit.ai/tools#throttled): Rate limiting library — fixed window, sliding window, token bucket, leaky bucket, GCRA. `npm i @indiekitai/throttled`
- [just](https://indiekit.ai/tools#just): Task runner using Justfile format (like make but better). `npx @indiekitai/just-ts build`
- [llm-context](https://indiekit.ai/tools#llm-context): Estimate how many tokens a codebase takes in LLM context. `npx @indiekitai/llm-context . --limit 128000`
- [git-standup](https://indiekit.ai/tools#git-standup): Generate daily standup reports from git commits. `npx @indiekitai/git-standup --since "2 days ago" --markdown`
- [clash-init](https://indiekit.ai/tools#clash-init): Generate Clash/mihomo proxy configs for SS/VMess/VLESS/Trojan/Hysteria2. `npx @indiekitai/clash-init --ss --server 1.2.3.4 --port 443`

### Terminal Rendering
- [glamour](https://indiekit.ai/tools#glamour): Render Markdown in terminals with 7 themes (dark, dracula, tokyo-night...). `npx @indiekitai/glamour README.md --style dark`
- [lipgloss](https://indiekit.ai/tools#lipgloss): CSS-like terminal text styling — colors, borders, padding, alignment. `npm i @indiekitai/lipgloss`
- [rich-inspect](https://indiekit.ai/tools#rich-inspect): Inspect any JS/TS object with colorful formatted output. `npx @indiekitai/rich-inspect data.json`

### Automation
- [trello-autopilot](https://indiekit.ai/tools#trello-autopilot): Scan Trello bug cards → invoke Claude Code to fix → move card to Done. Full pipeline: `npx @indiekitai/trello-autopilot --board MyProject --list Bugs --repo ./code`. Supports dry-run, custom agents, MCP Server with scan_bugs/fix_bug/move_card tools.
- [pi-skills](https://indiekit.ai/tools#pi-skills): All 16 tools as Pi/Claude Code skills. One install: `pi install npm:@indiekitai/pi-skills`

## MCP Server

One config, all tools:
```json
{"mcpServers":{"indiekit":{"command":"npx","args":["@indiekitai/mcp"]}}}
```

## API

All tools available as npm packages under @indiekitai/* scope.
npm: https://www.npmjs.com/org/indiekitai
GitHub: https://github.com/indiekitai

## Blog

Latest posts at https://indiekit.ai/blog
""")


# llms-full.txt - 完整内容给 AI 抓取
@app.get("/llms-full.txt")
async def llms_full():
    from fastapi.responses import PlainTextResponse
    posts = load_posts()
    
    content = f"""# IndieKit.ai - 完整内容

> 独立开发者的 AI 工具包

## 所有博客文章

"""
    for p in posts:
        content += f"""
### {p['title']}

日期: {p['date']}
标签: {', '.join(p['tags']) if p['tags'] else '无'}
链接: {SITE_URL}/blog/{p['slug']}

{p['content']}

---
"""
    
    return PlainTextResponse(content)


# --- AI Agent friendly APIs ---

@app.get("/api/tools")
async def api_tools():
    return {"tools": TOOLS_DATA}


@app.get("/api/blog")
async def api_blog():
    posts = load_posts()
    return {"posts": [
        {"slug": p["slug"], "title": p["title"], "date": str(p["date"]), "tags": p["tags"], "url": f"{SITE_URL}/blog/{p['slug']}"}
        for p in posts
    ]}


@app.get("/api/blog/{slug}")
async def api_blog_post(slug: str):
    posts = load_posts()
    post = next((p for p in posts if p["slug"] == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "slug": post["slug"],
        "title": post["title"],
        "date": str(post["date"]),
        "tags": post["tags"],
        "description": post["description"],
        "content_markdown": post["content"],
        "url": f"{SITE_URL}/blog/{slug}",
    }


@app.get("/.well-known/ai-plugin.json")
async def ai_plugin():
    return {
        "schema_version": "v1",
        "name": "IndieKit",
        "description": "Open-source developer tools with MCP support",
        "api": {"url": f"{SITE_URL}/api"},
        "logo_url": f"{SITE_URL}/logo.png",
        "contact_email": "hello@indiekit.ai",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
