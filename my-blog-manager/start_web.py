"""
start_web.py - Web 模式启动入口
适用于 NAS、服务器、远程管理场景
不需要 pywebview，纯 Web 访问
"""
import os
import sys
import subprocess
import importlib.util

# 1. 后端 Python 依赖清单（去掉了 pywebview）
PYTHON_PACKAGES = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "multipart": "python-multipart",
    "requests": "requests",
    "yaml": "PyYAML",
    "markdown": "markdown",
    "markdownify": "markdownify",
    "httpx": "httpx",
}


def check_node_environment():
    """检查前端环境：是否存在 node_modules，不存在则自动安装"""
    print("🔍 正在检查前端依赖 (Node.js)...")
    if not os.path.exists("node_modules"):
        print("📦 发现缺失前端依赖，正在尝试运行 npm install (请稍候)...")
        try:
            subprocess.check_call(["npm", "install"], shell=(os.name == 'nt'))
            print("✅ 前端依赖安装成功！")
        except Exception as e:
            print(f"❌ 前端安装失败！请确保已安装 Node.js。错误: {e}")
            return False
    else:
        print("✅ 前端依赖已就绪。")
    return True


def check_python_environment():
    """检查后端 Python 环境"""
    print("🔍 正在检查后端依赖 (Python)...")
    python_exe = sys.executable
    for import_name, install_name in PYTHON_PACKAGES.items():
        if importlib.util.find_spec(import_name) is None:
            print(f"📦 正在自动安装 Python 库: {install_name}...")
            subprocess.check_call([python_exe, "-m", "pip", "install", install_name])
    print("✅ 后端依赖已就绪。")
    return True


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("🌟 --- 星辉云端控制台 · Web 模式 --- 🌟")
    print()

    if check_node_environment() and check_python_environment():
        print("\n🚀 所有环境准备就绪，正在启动 Web 服务...")
        print()
        # 直接调用 launcher_web.py（不创建新窗口）
        subprocess.call([sys.executable, "launcher_web.py"])
    else:
        print("\n⚠️ 环境检查未通过，请根据报错信息手动处理。")
        if os.name == 'nt':
            input("按回车键退出...")
        sys.exit(1)
