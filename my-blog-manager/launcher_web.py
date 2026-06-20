"""
launcher_web.py - Web 模式启动器
去掉 pywebview 桌面窗口，改为纯 Web 访问，支持 0.0.0.0 绑定
适用于 NAS、服务器、远程管理等场景
"""
import sys
import os
import signal

# 🌟 路径定位逻辑
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

import threading
import uvicorn
import time
import socket
import json
import subprocess
import traceback
from cms_core.main import app

frontend_process = None

# ============================================================
# 配置：可通过环境变量或 config 文件覆盖
# ============================================================
def get_config():
    """读取 web_config.json，不存在则用默认值"""
    config_file = os.path.join(EXE_DIR, 'web_config.json')
    defaults = {
        "backend_host": "0.0.0.0",
        "backend_port": 8019,
        "frontend_host": "0.0.0.0",
        "frontend_port": 3000,
        "use_dev_mode": False,
        "blog_path": ""
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_cfg = json.load(f)
                defaults.update(user_cfg)
        except Exception:
            pass
    # 环境变量优先
    defaults["backend_port"] = int(os.environ.get("BACKEND_PORT", defaults["backend_port"]))
    defaults["frontend_port"] = int(os.environ.get("FRONTEND_PORT", defaults["frontend_port"]))
    defaults["backend_host"] = os.environ.get("BACKEND_HOST", defaults["backend_host"])
    defaults["frontend_host"] = os.environ.get("FRONTEND_HOST", defaults["frontend_host"])
    defaults["blog_path"] = os.environ.get("BLOG_PATH", defaults["blog_path"])
    return defaults


def auto_config_blog_path(blog_path):
    """Docker 环境下自动写入 deploy_config.json，省去手动配置"""
    if not blog_path:
        return
    deploy_config_file = os.path.join(EXE_DIR, 'data', 'deploy_config.json')
    os.makedirs(os.path.dirname(deploy_config_file), exist_ok=True)
    existing = {}
    if os.path.exists(deploy_config_file):
        try:
            with open(deploy_config_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            pass
    if not existing.get('blogPath'):
        existing['blogPath'] = blog_path
        with open(deploy_config_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        print(f"  📝 已自动配置博客路径: {blog_path}")


def write_port_config(backend_port):
    """写入 backend_config.json 供前端读取 API 端口"""
    public_dir = os.path.join(BASE_DIR, 'public')
    os.makedirs(public_dir, exist_ok=True)
    with open(os.path.join(public_dir, 'backend_config.json'), 'w', encoding='utf-8') as f:
        json.dump({"api_port": backend_port}, f)

    standalone_public = os.path.join(BASE_DIR, '.next', 'standalone', 'public')
    if os.path.exists(os.path.join(BASE_DIR, '.next', 'standalone')):
        os.makedirs(standalone_public, exist_ok=True)
        with open(os.path.join(standalone_public, 'backend_config.json'), 'w', encoding='utf-8') as f:
            json.dump({"api_port": backend_port}, f)


def wait_for_port(port, host='127.0.0.1', timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(1)
    return False


def release_port(port):
    """跨平台释放端口（仅 Windows 用 netstat+taskkill）"""
    if os.name == 'nt':
        try:
            command = f'netstat -ano | findstr :{port}'
            result = subprocess.check_output(command, shell=True).decode()
            lines = result.strip().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5 and parts[3] == 'LISTENING':
                    pid = parts[-1]
                    subprocess.run(f'taskkill /PID {pid} /F /T', shell=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(0.5)
        except Exception:
            pass
    # Linux/Mac: 一般不需要手动释放，进程退出时自动释放


def run_api(host, port):
    """启动 FastAPI 后端"""
    os.chdir(EXE_DIR)
    print(f"🟢 [后端] 工作路径已锁定: {EXE_DIR}")
    print(f"🟢 [后端] 监听地址: {host}:{port}")
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception:
        print("❌ [后端] 崩溃报错：")
        traceback.print_exc()


def cleanup(frontend_proc, backend_port, frontend_port):
    """清理所有子进程"""
    if frontend_proc:
        try:
            frontend_proc.terminate()
            frontend_proc.wait(timeout=5)
        except Exception:
            try:
                frontend_proc.kill()
            except Exception:
                pass
    release_port(backend_port)
    release_port(frontend_port)


def main():
    global frontend_process

    cfg = get_config()
    backend_host = cfg["backend_host"]
    backend_port = cfg["backend_port"]
    frontend_host = cfg["frontend_host"]
    frontend_port = cfg["frontend_port"]
    use_dev_mode = cfg["use_dev_mode"]

    print("=" * 60)
    print("🌟 星辉云端·控制台 (Web 模式)")
    print("=" * 60)
    print(f"  后端地址: {backend_host}:{backend_port}")
    print(f"  前端地址: {frontend_host}:{frontend_port}")
    print(f"  运行模式: {'开发模式' if use_dev_mode else '生产模式'}")
    if cfg.get('blog_path'):
        print(f"  博客路径: {cfg['blog_path']}")
        auto_config_blog_path(cfg['blog_path'])
    print("=" * 60)

    env_vars = os.environ.copy()
    env_vars["PORT"] = str(frontend_port)
    env_vars["HOSTNAME"] = frontend_host

    standalone_dir = os.path.join(BASE_DIR, '.next', 'standalone')
    server_js = os.path.join(standalone_dir, 'server.js')

    # 判断生产模式 vs 开发模式
    if use_dev_mode or not os.path.exists(server_js):
        print("🛠️ [前端] 开发模式启动...")
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=BASE_DIR,
            env=env_vars,
            shell=(os.name == 'nt')
        )
    else:
        print("🚀 [前端] 生产模式启动...")
        frontend_process = subprocess.Popen(
            ["node", "server.js"],
            cwd=standalone_dir,
            env=env_vars,
            shell=(os.name == 'nt')
        )

    # 写入端口配置
    write_port_config(backend_port)

    # 启动后端 (daemon 线程)
    api_thread = threading.Thread(
        target=run_api, args=(backend_host, backend_port), daemon=True
    )
    api_thread.start()

    # 等待端口就绪
    print("⏳ 等待服务启动...")
    if not wait_for_port(backend_port):
        print(f"❌ 后端端口 {backend_port} 启动超时！")
        cleanup(frontend_process, backend_port, frontend_port)
        sys.exit(1)
    print(f"  ✅ 后端已就绪: http://{backend_host}:{backend_port}")

    if not wait_for_port(frontend_port, frontend_host):
        print(f"❌ 前端端口 {frontend_port} 启动超时！")
        cleanup(frontend_process, backend_port, frontend_port)
        sys.exit(1)
    print(f"  ✅ 前端已就绪: http://{frontend_host}:{frontend_port}")

    print()
    print("🎉 启动完成！请在浏览器中打开：")
    print(f"   👉 http://localhost:{frontend_port}")
    print(f"   👉 http://0.0.0.0:{frontend_port} (局域网)")
    print()
    print("按 Ctrl+C 停止服务...")

    # 注册信号处理
    def signal_handler(sig, frame):
        print("\n🛑 正在停止服务...")
        cleanup(frontend_process, backend_port, frontend_port)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 保持主线程存活
    try:
        while True:
            time.sleep(1)
            # 检查前端进程是否意外退出
            if frontend_process and frontend_process.poll() is not None:
                print("❌ 前端进程意外退出！")
                cleanup(frontend_process, backend_port, frontend_port)
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        cleanup(frontend_process, backend_port, frontend_port)


if __name__ == "__main__":
    main()
