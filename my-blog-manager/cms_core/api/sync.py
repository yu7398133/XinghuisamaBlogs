import os
import shutil
import subprocess
import threading
from fastapi import APIRouter, Request

router = APIRouter()

# 动态定位 Manager 根目录
CURRENT_API_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_API_DIR, "..", ".."))

# 需要镜像覆盖的文件夹 (先清空目标，再全量复制)
SYNC_DIRS = ["posts", "chatters", "moments"]
# 需要精确覆盖的单文件
SYNC_FILES = [
    "app/about/about.md",
    "data/albums.ts",
    "data/friends.ts",
    "data/projects.ts",
    "siteConfig.ts"
]


def is_safe_blog_dir(target_path):
    """防呆检测：只有包含 package.json 的才被认为是安全的博客目录"""
    return os.path.exists(os.path.join(target_path, "package.json"))


def trigger_rebuild(blog_path):
    """后台触发 Next.js 重建并重启前端"""
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def _rebuild():
        try:
            print("[Rebuild] Starting npm run build in /app...")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=app_dir,
                timeout=300,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"[Rebuild] Build failed: {result.stderr[:500]}")
                return

            print("[Rebuild] Done! Restarting container...")
            # 同步执行 restart
            os.system("docker restart xhblogs-manager")
        except Exception as e:
            print(f"[Rebuild] Failed: {e}")

    threading.Thread(target=_rebuild, daemon=True).start()


@router.post("/check")
async def check_blog_path(request: Request):
    """检测目标路径是否合法且具备基本结构"""
    try:
        payload = await request.json()
        target_path = payload.get("blogPath", "").strip()

        if not target_path or not os.path.exists(target_path):
            return {"success": False, "message": "🚫 目标物理路径不存在，请检查输入！"}

        if not is_safe_blog_dir(target_path):
            return {"success": False,
                    "message": "⚠️ 危险！目标路径未检测到 package.json，似乎不是一个有效的前端项目，已拦截操作。"}

        missing = []
        for d in ["posts", "data", "app"]:
            if not os.path.exists(os.path.join(target_path, d)):
                missing.append(d)

        if missing:
            return {"success": True,
                    "message": f"✅ 路径安全。但目标缺失以下文件夹：{', '.join(missing)}。同步时将自动创建。"}

        return {"success": True, "message": "✅ 路径校验通过，目录结构完美！"}
    except Exception as e:
        return {"success": False, "message": f"校验异常: {str(e)}"}


@router.post("/execute")
async def execute_sync(request: Request):
    """执行物理覆盖同步"""
    try:
        payload = await request.json()
        target_path = payload.get("blogPath", "").strip()

        if not is_safe_blog_dir(target_path):
            return {"success": False, "message": "安全拦截：目标路径不合法！"}

        # 1. 同步文件夹 (先彻底删除目标文件夹，再把 Manager 的复制过去)
        for d in SYNC_DIRS:
            src_dir = os.path.join(PROJECT_ROOT, d)
            dst_dir = os.path.join(target_path, d)

            if os.path.exists(src_dir):
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)

        # 2. 同步单个文件 (直接覆盖或过滤)
        for f in SYNC_FILES:
            src_file = os.path.join(PROJECT_ROOT, f.replace("/", os.sep))
            dst_file = os.path.join(target_path, f.replace("/", os.sep))

            if os.path.exists(src_file):
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                if f == "siteConfig.ts":
                    with open(src_file, "r", encoding="utf-8") as file_in:
                        lines = file_in.readlines()

                    with open(dst_file, "w", encoding="utf-8") as file_out:
                        for line in lines:
                            if "picBedName:" in line or "picBedUrl:" in line or "picBedToken:" in line or "图床核心配置" in line:
                                continue
                            file_out.write(line)
                else:
                    shutil.copy2(src_file, dst_file)

        # 3. 触发后台 rebuild
        trigger_rebuild(target_path)

        return {"success": True, "message": "🎉 同步完成！前端正在后台重建，约 1-2 分钟后自动生效。"}
    except Exception as e:
        return {"success": False, "message": f"同步过程中发生致命错误: {str(e)}"}
