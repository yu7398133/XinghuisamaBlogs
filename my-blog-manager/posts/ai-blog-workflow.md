---
title: "AI 写文章发布全流程：让 AI 助手帮你管理博客"
date: "2026-06-20 18:00:00"
description: "如何用 AI 助手通过 SSH 直接写文章、发布到博客，省去手动操作"
cover: "https://bu.dusays.com/2026/03/24/69c1e38b346cb.jpg"
tags: ["AI", "博客", "教程", "自动化"]
---

## 为什么让 AI 帮你写博客？

传统写博客流程：打开编辑器 → 写 Markdown → 复制到后台 → 保存 → 同步 → 推送 → 等部署。

AI 辅助流程：告诉 AI 你想写什么 → AI 自动完成全部操作 → 你只需要审核。

本文介绍如何配置 AI 助手（如 MiMoCode、Claude 等）通过 SSH 直接操作服务器，完成从写作到发布的全流程。

## 环境准备

你需要：

1. 一台能 SSH 访问的服务器（NAS / VPS / 云服务器）
2. Docker 运行的 XHBlogs 管理后台（端口 13001）
3. GitHub 仓库 + Vercel 部署
4. 一个能执行 SSH 命令的 AI 助手

## 核心概念

博客有三种内容类型：

| 类型 | 目录 | 用途 |
|------|------|------|
| 文章 | `posts/` | 正式博客文章 |
| 杂谈 | `chatters/` | 随笔、碎片记录 |
| 动态 | `moments/` | 类似朋友圈 |

## 文章格式

每篇文章都是一个 Markdown 文件，头部用 YAML frontmatter 定义元信息：

```markdown
---
title: "文章标题"
date: "2026-06-20 12:00:00"
description: "一句话简介"
cover: "封面图URL"
tags: ["标签1", "标签2"]
---

## 正文标题

正文内容，支持标准 Markdown 语法。
```

## AI 操作全流程

### 第一步：SSH 写入文章

AI 助手通过 SSH 连接服务器，直接在容器内创建 Markdown 文件：

```bash
sshpass -p '密码' ssh -o StrictHostKeyChecking=no NAS@10.147.21.201 \
  "docker exec xhblogs-manager bash -c 'cat > /data/blog/posts/my-article.md << EOF
---
title: \"文章标题\"
date: \"2026-06-20 18:00:00\"
description: \"简介\"
cover: \"\"
tags: [\"标签\"]
---

正文内容...'
EOF"
```

### 第二步：Git 推送到 GitHub

```bash
sshpass -p '密码' ssh -o StrictHostKeyChecking=no NAS@10.147.21.201 \
  "docker exec xhblogs-manager bash -c 'cd /data/blog && \
    git add -A && \
    git commit -m \"post: 文章标题\" && \
    git push origin main'"
```

### 第三步：等待 Vercel 自动部署

推送到 GitHub 的 `main` 分支后，Vercel 会自动触发构建。通常 2-3 分钟后，线上博客就会更新。

## 完整命令模板

把下面的模板保存下来，AI 助手可以直接复用：

```bash
# SSH 连接前缀
export SSH="sshpass -p 'yu7398133' ssh -o StrictHostKeyChecking=no NAS@10.147.21.201"

# 创建文章（先写本地，再 docker cp 进去）
cat > /tmp/article.md << 'ARTICLE_EOF'
---
title: "标题"
date: "2026-06-20 18:00:00"
description: "简介"
cover: ""
tags: ["标签"]
---

正文内容
ARTICLE_EOF

# 复制到容器并推送
$SSH "docker cp /tmp/article.md xhblogs-manager:/data/blog/posts/文章文件名.md"
$SSH "docker exec xhblogs-manager bash -c 'cd /data/blog && git add -A && git commit -m \"post: 标题\" && git push origin main'"
```

## 动态（朋友圈）格式

动态的时间戳用毫秒级 Unix 时间戳，文件名格式为 `moment-{时间戳}.md`：

```markdown
---
id: "moment-1777128883968"
date: "2026-04-25T14:54:43.968Z"
location: "省 市"
images:
  - '图片URL1'
  - '图片URL2'
---

动态文字内容
```

## 实际使用场景

### 场景 1：随手记录灵感

对 AI 说："帮我写一条动态，今天在实验室跑完了 GROMACS 模拟，结果不错"

AI 会自动：
1. 生成动态内容
2. SSH 写入 `moments/` 目录
3. Git 推送
4. 线上生效

### 场景 2：写技术文章

对 AI 说："帮我写一篇关于 Next.js 部署到 Vercel 的教程"

AI 会自动：
1. 生成完整的 Markdown 教程
2. SSH 写入 `posts/` 目录
3. Git 推送
4. 线上生效

### 场景 3：批量整理笔记

对 AI 说："把我的这些笔记整理成博客文章"

AI 会自动：
1. 解析笔记内容
2. 格式化为标准博客文章
3. 批量写入 `posts/` 目录
4. 一次性 Git 推送

## 注意事项

1. **文件名用英文**：避免编码问题，如 `my-first-post.md`
2. **cover 留空用默认**：不填则使用 siteConfig.ts 中的 defaultPostCover
3. **推送前检查状态**：确保 `git status` 正常
4. **Vercel 构建需要时间**：推送后等 2-3 分钟再查看线上效果
5. **本地不会热更新**：Docker 容器内的前端是编译产物，改源文件不会立即生效

## 总结

通过 SSH + Git 的组合，AI 助手可以完全替代手动操作，实现：

- **写文章**：AI 生成内容，自动写入文件
- **发布**：自动 Git 推送，Vercel 自动部署
- **管理**：批量操作、格式转换、内容整理

整个过程无需打开浏览器，无需手动复制粘贴，真正实现"告诉 AI 你想写什么，剩下的交给它"。
