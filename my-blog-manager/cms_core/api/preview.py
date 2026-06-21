import os
import re
import yaml
import markdown
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BLOG_ROOT = os.path.join(PROJECT_ROOT, "..", "..", "data", "blog")
# 如果 /data/blog 不存在，回退到 /app
if not os.path.exists(BLOG_ROOT):
    BLOG_ROOT = "/data/blog"


def parse_md_file(filepath):
    """解析 markdown 文件，返回 frontmatter + HTML content"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    meta = {}
    body = raw

    if raw.strip().startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].strip()

    html_body = markdown.markdown(body, extensions=["fenced_code", "tables", "nl2br", "codehilite"])

    slug = os.path.splitext(os.path.basename(filepath))[0]
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "date": str(meta.get("date", "")),
        "tags": meta.get("tags", []),
        "cover": meta.get("cover", ""),
        "description": meta.get("description", ""),
        "mood": meta.get("mood", ""),
        "content_html": html_body,
    }


def list_md_files(directory):
    """列出目录下所有 .md 文件并解析"""
    files = []
    if not os.path.exists(directory):
        return files
    for name in os.listdir(directory):
        if name.endswith(".md"):
            filepath = os.path.join(directory, name)
            try:
                files.append(parse_md_file(filepath))
            except Exception:
                continue
    files.sort(key=lambda x: x.get("date", ""), reverse=True)
    return files


# ============ HTML 模板 ============

BASE_CSS = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; min-height: 100vh; }
.container { max-width: 800px; margin: 0 auto; padding: 20px; }
.header { text-align: center; padding: 40px 0 30px; border-bottom: 1px solid #e2e8f0; margin-bottom: 30px; }
.header h1 { font-size: 24px; font-weight: 800; color: #0f172a; }
.header p { color: #64748b; margin-top: 8px; font-size: 14px; }
.header .badge { display: inline-block; background: #6366f1; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 12px; }
.post-card { background: white; border-radius: 16px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #f1f5f9; transition: box-shadow 0.2s; }
.post-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.post-card h2 { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.post-card h2 a { color: #0f172a; text-decoration: none; }
.post-card h2 a:hover { color: #6366f1; }
.post-card .meta { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.post-card .desc { font-size: 14px; color: #64748b; line-height: 1.6; }
.post-card .tags { margin-top: 10px; }
.post-card .tag { display: inline-block; background: #f1f5f9; color: #6366f1; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-right: 6px; }
.post-detail { background: white; border-radius: 16px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #f1f5f9; }
.post-detail h1 { font-size: 28px; font-weight: 900; margin-bottom: 12px; color: #0f172a; }
.post-detail .meta { font-size: 14px; color: #94a3b8; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #f1f5f9; }
.post-detail .content { font-size: 15px; line-height: 1.8; color: #334155; }
.post-detail .content h2 { font-size: 20px; font-weight: 800; margin: 24px 0 12px; color: #0f172a; }
.post-detail .content h3 { font-size: 17px; font-weight: 700; margin: 20px 0 10px; color: #0f172a; }
.post-detail .content p { margin-bottom: 12px; }
.post-detail .content code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #6366f1; }
.post-detail .content pre { background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }
.post-detail .content pre code { background: none; color: inherit; padding: 0; }
.post-detail .content blockquote { border-left: 4px solid #6366f1; padding: 12px 16px; margin: 12px 0; background: #f8fafc; border-radius: 0 8px 8px 0; color: #64748b; font-style: italic; }
.post-detail .content ul, .post-detail .content ol { padding-left: 24px; margin: 12px 0; }
.post-detail .content li { margin-bottom: 6px; }
.post-detail .content img { max-width: 100%; border-radius: 8px; margin: 12px 0; }
.back-btn { display: inline-block; color: #6366f1; text-decoration: none; font-weight: 600; font-size: 14px; margin-bottom: 20px; }
.back-btn:hover { text-decoration: underline; }
.nav { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.nav a { padding: 8px 16px; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 14px; transition: all 0.2s; }
.nav a.active { background: #6366f1; color: white; }
.nav a:not(.active) { background: white; color: #64748b; border: 1px solid #e2e8f0; }
.nav a:not(.active):hover { background: #f1f5f9; color: #0f172a; }
.section-title { font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
</style>
"""


def layout(title, nav_html, content_html):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - 预览</title>
{BASE_CSS}
</head>
<body>
<div class="container">
  <div class="header">
    <h1>XHBlogs 本地预览</h1>
    <p>实时查看博客内容，无需 rebuild</p>
    <span class="badge">⚡ 实时预览</span>
  </div>
  {nav_html}
  {content_html}
</div>
</body>
</html>"""


# ============ 路由 ============

@router.get("/", response_class=HTMLResponse)
async def preview_home():
    """首页：列出所有文章、杂谈、动态"""
    posts = list_md_files(os.path.join(BLOG_ROOT, "posts"))
    chatters = list_md_files(os.path.join(BLOG_ROOT, "chatters"))
    moments = list_md_files(os.path.join(BLOG_ROOT, "moments"))

    nav = """<div class="nav">
      <a href="/preview/" class="active">首页</a>
      <a href="/preview/posts">文章</a>
      <a href="/preview/chatters">杂谈</a>
      <a href="/preview/moments">动态</a>
    </div>"""

    html = '<div class="section-title">最新文章</div>'
    for p in posts[:5]:
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in p.get("tags", []))
        html += f"""<div class="post-card">
          <h2><a href="/preview/posts/{p['slug']}">{p['title']}</a></h2>
          <div class="meta">{p['date']}</div>
          <div class="desc">{p.get('description', '')}</div>
          <div class="tags">{tags_html}</div>
        </div>"""

    if chatters:
        html += '<div class="section-title" style="margin-top:24px">最新杂谈</div>'
        for c in chatters[:3]:
            html += f"""<div class="post-card">
              <h2><a href="/preview/chatters/{c['slug']}">{c['title']}</a></h2>
              <div class="meta">{c['date']}</div>
            </div>"""

    return layout("首页", nav, html)


@router.get("/posts", response_class=HTMLResponse)
async def preview_posts_list():
    """文章列表"""
    posts = list_md_files(os.path.join(BLOG_ROOT, "posts"))

    nav = """<div class="nav">
      <a href="/preview/">首页</a>
      <a href="/preview/posts" class="active">文章</a>
      <a href="/preview/chatters">杂谈</a>
      <a href="/preview/moments">动态</a>
    </div>"""

    html = '<div class="section-title">全部文章</div>'
    for p in posts:
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in p.get("tags", []))
        html += f"""<div class="post-card">
          <h2><a href="/preview/posts/{p['slug']}">{p['title']}</a></h2>
          <div class="meta">{p['date']}</div>
          <div class="desc">{p.get('description', '')}</div>
          <div class="tags">{tags_html}</div>
        </div>"""

    return layout("文章列表", nav, html)


@router.get("/posts/{slug}", response_class=HTMLResponse)
async def preview_post_detail(slug: str):
    """单篇文章详情"""
    filepath = os.path.join(BLOG_ROOT, "posts", f"{slug}.md")
    if not os.path.exists(filepath):
        return layout("404", "", "<p>文章不存在</p>")

    post = parse_md_file(filepath)

    nav = """<div class="nav">
      <a href="/preview/">首页</a>
      <a href="/preview/posts" class="active">文章</a>
      <a href="/preview/chatters">杂谈</a>
      <a href="/preview/moments">动态</a>
    </div>"""

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in post.get("tags", []))

    html = f"""<a href="/preview/posts" class="back-btn">← 返回文章列表</a>
    <div class="post-detail">
      <h1>{post['title']}</h1>
      <div class="meta">{post['date']} {tags_html}</div>
      <div class="content">{post['content_html']}</div>
    </div>"""

    return layout(post["title"], nav, html)


@router.get("/chatters", response_class=HTMLResponse)
async def preview_chatters_list():
    """杂谈列表"""
    chatters = list_md_files(os.path.join(BLOG_ROOT, "chatters"))

    nav = """<div class="nav">
      <a href="/preview/">首页</a>
      <a href="/preview/posts">文章</a>
      <a href="/preview/chatters" class="active">杂谈</a>
      <a href="/preview/moments">动态</a>
    </div>"""

    html = '<div class="section-title">全部杂谈</div>'
    for c in chatters:
        html += f"""<div class="post-card">
          <h2><a href="/preview/chatters/{c['slug']}">{c['title']}</a></h2>
          <div class="meta">{c['date']}</div>
        </div>"""

    return layout("杂谈列表", nav, html)


@router.get("/chatters/{slug}", response_class=HTMLResponse)
async def preview_chatter_detail(slug: str):
    """单条杂谈详情"""
    filepath = os.path.join(BLOG_ROOT, "chatters", f"{slug}.md")
    if not os.path.exists(filepath):
        return layout("404", "", "<p>杂谈不存在</p>")

    post = parse_md_file(filepath)

    nav = """<div class="nav">
      <a href="/preview/">首页</a>
      <a href="/preview/posts">文章</a>
      <a href="/preview/chatters" class="active">杂谈</a>
      <a href="/preview/moments">动态</a>
    </div>"""

    html = f"""<a href="/preview/chatters" class="back-btn">← 返回杂谈列表</a>
    <div class="post-detail">
      <h1>{post['title']}</h1>
      <div class="meta">{post['date']}</div>
      <div class="content">{post['content_html']}</div>
    </div>"""

    return layout(post["title"], nav, html)


@router.get("/moments", response_class=HTMLResponse)
async def preview_moments_list():
    """动态列表"""
    moments = list_md_files(os.path.join(BLOG_ROOT, "moments"))

    nav = """<div class="nav">
      <a href="/preview/">首页</a>
      <a href="/preview/posts">文章</a>
      <a href="/preview/chatters">杂谈</a>
      <a href="/preview/moments" class="active">动态</a>
    </div>"""

    html = '<div class="section-title">全部动态</div>'
    for m in moments:
        html += f"""<div class="post-card">
          <h2>{m['title']}</h2>
          <div class="meta">{m['date']}</div>
          <div class="desc">{m.get('description', m.get('content_html', '')[:100])}</div>
        </div>"""

    return layout("动态列表", nav, html)
