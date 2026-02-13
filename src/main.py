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

load_dotenv()

CONTENT_DIR = Path(__file__).parent.parent / "content"
SITE_URL = os.getenv("SITE_URL", "https://indiekit.ai")
SITE_NAME = "IndieKit"
SITE_DESC = "独立开发者的 AI 工具包 | Resources for Indie Hackers"

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
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description or SITE_DESC}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical or SITE_URL}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description or SITE_DESC}">
    
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
            <a href="/about">关于</a>
        </nav>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p>© 2026 IndieKit.ai - Built by an AI, for indie hackers</p>
    </footer>
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
        <p>这个网站本身也是用 AI 在一晚上搭建的 —— 包括 5 个工具和这个博客。</p>
    </article>
    
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
    
    content = f'''
    <article>
        <h1>{post['title']}</h1>
        <div class="meta">{post['date']} · {', '.join(post['tags']) if post['tags'] else '未分类'}</div>
        {html_content}
    </article>
    '''
    
    return render_html(post['title'], content, post['description'], f"{SITE_URL}/blog/{slug}")


@app.get("/tools", response_class=HTMLResponse)
async def tools():
    content = '''
    <h1>工具</h1>
    <p>所有工具都是免费使用的，代码开源在 GitHub。</p>
    
    <div class="tools">
        <div class="tool">
            <h3>📰 HN Digest</h3>
            <p>AI 自动抓取 Hacker News 热门文章，生成中文摘要。每天更新，帮你快速了解科技圈动态。</p>
            <p><a href="https://hn.indiekit.ai">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>📊 Uptime Ping</h3>
            <p>监控你的 API 和网站是否正常运行。支持 Telegram 告警，服务挂了第一时间通知你。</p>
            <p><a href="https://up.indiekit.ai">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>🔗 Webhook Relay</h3>
            <p>接收来自 GitHub、Stripe 等服务的 Webhook，转发到你的 Telegram。再也不用盯着后台看了。</p>
            <p><a href="https://hook.indiekit.ai">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>🔗 Tiny Link</h3>
            <p>自托管的短链接服务。支持点击统计、自定义短码。你的数据你做主。</p>
            <p><a href="https://s.indiekit.ai">→ 访问工具</a></p>
        </div>
        <div class="tool">
            <h3>📋 Quick Paste</h3>
            <p>代码分享工具，支持语法高亮、阅后即焚。分享代码片段的最佳选择。</p>
            <p><a href="https://p.indiekit.ai">→ 访问工具</a></p>
        </div>
    </div>
    '''
    
    return render_html("工具", content, "免费开源的独立开发者工具集合", f"{SITE_URL}/tools")


@app.get("/about", response_class=HTMLResponse)
async def about():
    content = '''
    <article>
        <h1>关于 IndieKit</h1>
        <p>IndieKit 是一个由 AI 驱动的独立开发者工具集合。</p>
        
        <h2>起源</h2>
        <p>2026 年 2 月 13 日凌晨，一个 AI 助手在 3 小时内构建了 5 个完整的 SaaS 工具，总计 2300+ 行代码。这就是 IndieKit 的起点。</p>
        
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
            <li>Twitter: <a href="https://twitter.com/indiekit">@indiekit</a></li>
            <li>GitHub: <a href="https://github.com/indiekit">github.com/indiekit</a></li>
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


@app.get("/robots.txt")
async def robots():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml

# AI Agents
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Perplexity
Allow: /

User-agent: anthropic-ai
Allow: /
""")


# llms.txt - AI agent friendly
@app.get("/llms.txt")
async def llms_txt():
    from fastapi.responses import PlainTextResponse
    posts = load_posts()
    
    posts_list = "\n".join([f"- {p['title']}: {SITE_URL}/blog/{p['slug']}" for p in posts])
    
    return PlainTextResponse(f"""# IndieKit.ai

> 独立开发者的 AI 工具包 - Resources for Indie Hackers

IndieKit 是一套为独立开发者打造的轻量级工具集合，由 AI 在一晚上构建完成。

## 工具

- HN Digest: AI 生成的中文 Hacker News 每日精选 - https://hn.indiekit.ai
- Uptime Ping: API 健康监控 + Telegram 告警 - https://up.indiekit.ai  
- Webhook Relay: 接收 Webhook 转发到 Telegram - https://hook.indiekit.ai
- Tiny Link: 短链接服务 + 点击统计 - https://s.indiekit.ai
- Quick Paste: 代码分享 + 语法高亮 - https://p.indiekit.ai

## 博客文章

{posts_list}

## 技术栈

- Python + FastAPI
- JSON 文件存储
- Cloudflare (DNS/CDN/SSL)
- DigitalOcean

## API 端点

所有工具都提供 REST API，返回 JSON 格式数据。

## 联系

网站: {SITE_URL}
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
