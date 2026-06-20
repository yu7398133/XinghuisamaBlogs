FROM node:18-slim

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git openssh-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 先复制依赖清单，利用 Docker 缓存层
COPY my-blog-manager/package.json my-blog-manager/package-lock.json ./

# 安装 Node.js 依赖
RUN npm install --production=false

# 复制 Python 依赖清单并安装
COPY my-blog-manager/requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 复制全部源码
COPY my-blog-manager/ .

# 创建数据目录
RUN mkdir -p /data/blog /data/manager_data

# 软链接数据目录，保持原有目录结构
RUN ln -sf /data/manager_data /app/manager_data

# 暴露端口
EXPOSE 3000 8019

# 启动
CMD ["python3", "launcher_web.py"]
