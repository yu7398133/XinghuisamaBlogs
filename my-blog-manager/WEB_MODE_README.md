# 🌐 Web 模式 - 远程管理后台

将原本只能在 Windows 本地通过 `Start.bat` + `pywebview` 桌面窗口使用的后台管理，改为可通过浏览器远程访问。

## 与原版的区别

| 特性 | 原版 (桌面模式) | Web 模式 |
|------|----------------|----------|
| 启动方式 | `Start.bat` | `Start_web.bat` / `Start_web.sh` |
| 访问方式 | 本地桌面窗口 (pywebview) | 浏览器访问 |
| 网络绑定 | 127.0.0.1 (仅本机) | 0.0.0.0 (局域网/公网) |
| 依赖要求 | 需要 pywebview | 不需要 pywebview |
| 适用场景 | Windows 本地使用 | NAS / 服务器 / 远程管理 |

## 快速开始

### Windows
```bat
Start_web.bat
```

### Linux / NAS
```bash
chmod +x Start_web.sh
./Start_web.sh
```

### Python 直接启动
```bash
python start_web.py
# 或
python run_me.py --web
```

启动后在浏览器打开：`http://<你的IP>:3000`

## 配置文件

编辑 `web_config.json` 自定义端口和绑定地址：

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
BACKEND_PORT=8019 FRONTEND_PORT=3000 python start_web.py
```

## 注意事项

- ⚠️ Web 模式**无登录认证**，请确保仅在内网环境使用
- ⚠️ 如需公网访问，建议配合 Nginx 反向代理 + 基础认证
- 原版 `Start.bat` 仍然可用，会自动检测 pywebview 是否安装
- 生产模式需要先 `npm run build` 构建前端
