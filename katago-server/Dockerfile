# Dockerfile for KataGo HTTP Server (Ubuntu 18.04)
FROM ubuntu:18.04

# 避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libboost-all-dev \
    libzip4 \
    libzip-dev \
    curl \
    file \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 升级pip以支持较新的Python包
RUN python3 -m pip install --upgrade pip

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip3 install -r requirements.txt

# 确保KataGo二进制文件有执行权限
RUN chmod +x katago_eigen

# 检查二进制文件类型和依赖
RUN echo "=== Binary file info ===" && \
    file katago_eigen && \
    echo "=== Binary dependencies ===" && \
    ldd katago_eigen && \
    echo "=== Available boost libraries ===" && \
    ls -la /usr/lib/x86_64-linux-gnu/libboost* | head -10

# 暴露端口
EXPOSE 2718

# 启动服务器
CMD ["python3", "katago_server_eigen.py"]