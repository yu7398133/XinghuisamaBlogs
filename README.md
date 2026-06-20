# 🌟 欢迎使用 XHBlogs！

这是一个采用 Next.js 构建的高颜值、毛玻璃（Glassmorphism）风格个人博客系统。本项目自带完善的前端展示与独立的后台控制台，支持 Markdown 沉浸式写作、草稿管理以及便捷的图床配置。

**线上体验**：[www.xinghuisama.top](https://www.xinghuisama.top)

---

## 语言

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README_en.md)
[![中文](https://img.shields.io/badge/语言-中文-red.svg)](README.md)

## 写在前面

### 更新摘要 (版本0.3.1~0.3.2)

#### 1. 新增个人关于动态
> 关于动态类贡献度及日志显示

#### 2. 修复部分富文本编辑器bug
> 修补目前存在的编辑器bug，如超链接无法显示，引用无法显示等

#### 3. 新增灵境与等级系统
> 类创意工坊功能，等级系统可在 设置->个人名片设置 中关闭

#### 4. 网易云音乐显示bug，已修复
> 已更换API，修复网易云音乐显示bug。更新即可

---

## 一、快速开始部署

### 1. 环境配置

本项目提供三种部署方式，请根据你的场景选择：

| 方式 | 适用场景 | 需要安装 |
|------|---------|----------|
| **Docker 部署** ⭐ | NAS / 服务器 / Linux | Docker + Docker Compose |
| **Web 模式** | 本地或服务器，不用 Docker | Node.js 18+、Python 3.10+、Git |
| **桌面模式** | Windows 本地使用 | Node.js 18+、Python 3.10+、Git |

---

### 2. Docker 部署（推荐）

> **适用场景**：将博客后台部署在 NAS、Linux 服务器，通过浏览器远程管理。

#### 第一步：安装 Docker

如果服务器还没有安装 Docker，执行以下命令一键安装：

```bash
# 一键安装 Docker + Docker Compose
curl -fsSL https://get.docker.com | sh

# 将当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER

# 重新登录 shell 使其生效，或执行：
newgrp docker

# 验证安装
docker --version
docker compose version
```

#### 第二步：克隆项目

```bash
git clone https://github.com/yu7398133/XinghuisamaBlogs.git
cd XinghuisamaBlogs
```

#### 第三步：启动服务

提供两种 Compose 方式，按需选择：

**方式 A：直接拉取远程镜像（推荐，开箱即用）**

```bash
docker compose up -d
```

**方式 B：本地构建镜像（适合修改了代码后自行构建）**

```bash
docker compose -f docker-compose.build.yml up -d --build
```

#### 第四步：访问

启动成功后，浏览器打开：

```
http://<你的服务器IP>:13001
```

#### 常用命令

```bash
# 查看运行日志
docker compose logs -f

# 停止服务
docker compose down

# 拉取最新镜像并重启（方式 A）
docker compose pull && docker compose up -d

# 重新构建并重启（方式 B）
docker compose -f docker-compose.build.yml up -d --build
```

**Docker 镜像地址**：`ghcr.io/yu7398133/xhblogs-manager:latest`

#### Docker 端口说明

| 端口 | 用途 |
|------|------|
| `13001` | 前端管理界面（浏览器访问） |
| `8019` | 后端 API |

#### Docker 数据卷

| 挂载 | 说明 |
|------|------|
| `./XHBlogs:/data/blog` | 博客前端源码（宿主机目录） |
| `manager_data:/data/manager_data` | 管理器数据（草稿等，持久化） |

---

### 3. Web 模式（不用 Docker）

> **适用场景**：不想用 Docker，直接在服务器或本地运行。

**环境要求**：Node.js 18+、Python 3.10+、Git

```bash
cd XinghuisamaBlogs/my-blog-manager
chmod +x Start_web.sh
./Start_web.sh
```

启动后浏览器打开：`http://<你的IP>:3000`

**自定义端口**：编辑 `my-blog-manager/web_config.json`：

```json
{
  "backend_host": "0.0.0.0",
  "backend_port": 8019,
  "frontend_host": "0.0.0.0",
  "frontend_port": 3000,
  "use_dev_mode": false
}
```

也可以通过环境变量覆盖：

```bash
FRONTEND_PORT=8080 BACKEND_PORT=8019 ./Start_web.sh
```

> **⚠️ 注意事项：**
> - Web 模式**无登录认证**，请确保仅在内网环境使用
> - 如需公网访问，建议配合 Nginx 反向代理 + 基础认证

---

### 4. 桌面模式（Windows 本地）

进入 `my-blog-manager` 文件夹（**⚠️ 请绝对不要重命名此文件夹，否则会导致环境路径解析失败！**）

双击运行 `Start.bat`，脚本会自动检测并安装依赖包，完成后自动唤起后台控制台。

---

### 5. 博客源码更新

使用更新器可以无损更新源码，不会覆盖你的文章和配置文件。

**更新步骤：**

1. 下载项目根目录下的 `update.bat` 和 `update.py` 文件
2. 将它们移动到博客项目根目录（和 `my-blog-manager`、`XHBlogs` 文件夹同级）

![目录结构](picture/333.png)

3. 双击 `update.bat` 完成更新（如果闪退，请用 cmd 运行 `update.py`）

---

### 6. 部署博客前端到 Vercel

> **提示**：Vercel 对 Next.js 有最顶级的原生支持，推荐用于部署前端展示页面。
>
> **前提**：已安装 Git，拥有 GitHub 账号。

**第一步：Git 全局配置**

```bash
git config --global user.name "你的Github用户名"
git config --global user.email "你绑定在Github的邮箱@example.com"
```

**第二步：初始化本地仓库**

进入 `XHBlogs` 文件夹，执行：

```bash
git init
git add .
git commit -m "first commit"
```

**第三步：配置物理路径**

打开后台控制台的"设置"页面，指定 `XHBlogs` 的本地物理路径：

![选择物理路径](picture/Pasted%20image%2020260427111646.png)

例如：`F:\Test2\XHBlogs`

![填入路径](picture/Pasted%20image%2020260427112311.png)

> **关键步骤**：填入路径后，务必点击 **[测试路径]** 验证连通性，通过后点击 **[保存双轨配置]**。

**第四步：在 GitHub 创建私有仓库**

登录 GitHub，新建一个 **Private（私有）** 仓库：

![创建仓库](picture/Pasted%20image%2020260427112905.png)

获取 SSH 地址，粘贴到控制台的"B线"配置中，分支填 `main`：

![复制SSH](picture/Pasted%20image%2020260427113120.png)

**第五步：配置部署密钥**

点击控制台 **[获取B线专属密钥]**：

![专属密钥](picture/98b965b5-6193-4690-a478-fe1a9abd594e.png)

进入 GitHub 仓库 → `Settings` → `Deploy keys`，粘贴密钥：

![Deploy Keys](picture/Pasted%20image%2020260427113705.png)

> **🚨 严重警告**：**Allow write access** 必须勾选！！！

**第六步：推送源码**

返回控制台，点击 **[智能初始化双轨环境]**，完成后点击 **[仅同步源码]**：

![仅同步源码](picture/Pasted%20image%2020260427121539.png)

> **此处可能出现无法推送bug**：请尝试将 SSH 地址改成如下格式再重试：
> ![img.png](picture/img.png)

**第七步：部署至 Vercel**

访问 [Vercel](https://vercel.com)，绑定 GitHub 授权，点击 `Add New...` 导入仓库：

![导入项目](picture/Pasted%20image%2020260427121939.png)

Framework Preset 选择 **Next.js**，点击 **Deploy**：

![点击Deploy](picture/Pasted%20image%2020260427122141.png)

部署成功后，Vercel 会分配一个免费二级域名：

![分配域名](picture/Pasted%20image%2020260427122553.png)

---

### 问题 1：如何绑定自己的专属域名？

以阿里云为例（其他服务商操作类似）：

1. 登录阿里云控制台 → 【域名管理】→ 点击【解析】
2. 回到 Vercel → 项目 Settings → Domains → 输入域名（如 `xinghuisama.top`）→ Add
3. Vercel 会提供 `A` 记录和 `CNAME` 记录，添加到阿里云 DNS 解析中
4. 等待几分钟 DNS 生效，点击 Vercel 页面的 **Refresh**

![输入域名](picture/afb9fe5f-bf1e-4a8a-ae6b-379938f0924d.png)

生效后即可通过专属域名访问博客（如 `www.xinghuisama.top`）。

---

## 二、更新设置及上传文件

控制台采用**"操作暂存区"**机制，修改后需主动执行"更新到本地"才能保存。

**操作示例：修改个人简介**

![修改简介](picture/Pasted%20image%2020260427125314.png)

修改后点击 **[暂存到操作队列]**：

![暂存队列](picture/Pasted%20image%2020260427125430.png)

然后点击 **[更新本地]** 保存到本地环境。

如需在前端博客页面生效，继续点击 **[同步 Blog]**：

![同步Blog](picture/Pasted%20image%2020260427125800.png)

> **💡 黄金法则**：暂存队列 → 更新本地 → 同步Blog

---

## 三、如何推送修改到线上网页？

修改并 **[同步Blog]** 后，打开控制台的同步部署页面：

![打开同步](picture/Pasted%20image%2020260427130216.png)

确认"B线"地址正确，点击 **[仅同步源码]**，等待 Vercel 自动捕获更新即可。

---

## 四、图床配置

控制台深度整合了图床上传功能，推荐使用"去不图床"（[https://7bu.top](https://7bu.top)）。

填入 API Token 后，点击 **[发送探针测试Token]** 检验接口是否畅通：

![图床配置](picture/Pasted%20image%2020260427124930.png)

---

## 五、AI 猫猫助理设置

博客内置 AI 猫猫助理（默认接入 Gemini 模型）。

1. 申请 Gemini API Key
2. 在控制台配置猫猫性格：

![猫猫设置](picture/Pasted%20image%2020260427134211.png)

3. 在 Vercel 项目设置 → Environment Variables 中添加：
   - **Key**：`GEMINI_API_KEY`
   - **Value**：你的 API 密钥

![输入API](picture/Pasted%20image%2020260427135044.png)

重新部署后，猫猫助理即可在线上生效。

---

## 六、评论系统配置

评论系统基于 GitHub Issues，需要：

1. 在 GitHub 创建一个 **Public（公开）** 仓库存储留言
2. 在控制台填入 GitHub 用户名和仓库名：

![评论设置](picture/a3b44842-696b-4764-9cdf-882cd8792729.png)

3. 配置 OAuth 授权：
   - GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
   - **Homepage URL**：你的博客首页地址（如 `https://www.xinghuisama.top`）
   - **Authorization callback URL**：你的博客域名（本地调试填 `http://localhost:3000`）
4. 将生成的 `Client ID` 和 `Client Secret` 填入控制台

---

## 七、网易云音乐挂件设置

打开网易云音乐网页版，进入歌曲详情页，URL 中的数字即为歌曲 ID：

![网易云ID](picture/Pasted%20image%2020260427141235.png)

将 ID 粘贴到控制台搜索框，即可收录进博客歌单：

![添加歌曲](picture/Pasted%20image%2020260427141356.png)

---

## 写在最后

XHBLogs 还有诸多隐藏功能，期待你在实际使用中慢慢探索。如果你是资深开发者，完全可以基于源码进行二次开发！

**如果你觉得这个项目对你有帮助，请在 GitHub 上点一颗 ⭐ Star！每颗星都是持续维护的最大动力。**

## 许可证

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

> 本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 许可协议。允许免费学习、分享和二次修改后发布（需提及原作者），但**严禁用于任何商业用途**。
