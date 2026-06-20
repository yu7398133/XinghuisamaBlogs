# AI 写文章发布指南

## 环境

- SSH: `sshpass -p 'yu7398133' ssh -o StrictHostKeyChecking=no NAS@10.147.21.201`
- 容器: `xhblogs-manager`
- 博客目录: `/data/blog`
- 仓库: `git@github.com:yu7398133/HSBlogs.git`
- Vercel: 自动监听 `main` 分支

## 内容目录

| 类型 | 路径 | 文件名格式 |
|------|------|-----------|
| 文章 | `posts/` | `英文文件名.md` |
| 杂谈 | `chatters/` | `YYYY-MM-DD-标题.md` |
| 动态 | `moments/` | `moment-时间戳ms.md` |

## 文章模板

```markdown
---
title: "标题"
date: "YYYY-MM-DD HH:mm:ss"
description: "简介"
cover: "封面图URL，留空用默认"
tags: ["标签"]
---

## 正

正文内容...
```

## 动态模板

```markdown
---
id: "moment-{timestamp_ms}"
date: "{ISO时间}"
location: "省 市"
images:
  - '图片URL1'
  - '图片URL2'
---

动态文字内容
```

## 快速命令

```bash
# SSH 前缀（所有命令加在前面）
SSH='sshpass -p yu7398133 ssh -o StrictHostKeyChecking=no NAS@10.147.21.201'

# 创建文章
$SSH "docker exec xhblogs-manager bash -c 'cat > /data/blog/posts/xxx.md << EOF
---
title: \"标题\"
date: \"$(date +%Y-%m-%d %H:%M:%S)\"
description: \"简介\"
cover: \"\"
tags: [\"标签\"]
---

正文
EOF'"

# 推送到线上
$SSH "docker exec xhblogs-manager bash -c 'cd /data/blog && git add -A && git commit -m \"post: 标题\" && git push origin main'"
```

## 发布流程

1. 写入 `.md` 文件到对应目录
2. `git add -A && git commit && git push origin main`
3. 等待 Vercel 自动构建（2-3 分钟）
4. 线上生效: https://blog2.chenyusc.eu.org

## 注意事项

- cover 留空会使用 siteConfig.ts 中的 defaultPostCover
- 推送前确保容器内 git 状态正常（`git status`）
- 文件名用英文避免编码问题
- 动态时间戳用毫秒级 Unix 时间戳
