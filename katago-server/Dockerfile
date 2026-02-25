# Dockerfile for KataGo HTTP Server (Ubuntu 22.04 with GPU support)
# 支持多后端：CUDA/OpenCL/CPU
ARG USE_BACKEND=EIGEN
ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE} AS builder

# 设置环境变量避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# 构建参数
ARG USE_BACKEND=EIGEN
ARG USE_TCMALLOC=1
ARG USE_AVX2=1
ARG BUILD_DISTRIBUTED=0

# 安装基础构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    pkg-config \
    python3 \
    python3-pip \
    python3-dev \
    libboost-all-dev \
    libzip-dev \
    zlib1g-dev \
    libeigen3-dev \
    libssl-dev \
    libgoogle-perftools-dev \
    curl \
    wget \
    file \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 条件安装CUDA支持（仅在需要时）
RUN if [ "$USE_BACKEND" = "CUDA" ] || [ "$USE_BACKEND" = "TENSORRT" ]; then \
        apt-get update && apt-get install -y \
        software-properties-common \
        && wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb \
        && dpkg -i cuda-keyring_1.1-1_all.deb \
        && apt-get update \
        && apt-get install -y \
        cuda-toolkit-12-9 \
        && rm -rf /var/lib/apt/lists/* \
        && rm cuda-keyring_1.1-1_all.deb; \
    fi

# 条件安装cuDNN（仅在CUDA后端时）
RUN if [ "$USE_BACKEND" = "CUDA" ] || [ "$USE_BACKEND" = "TENSORRT" ]; then \
        wget https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/linux-x86_64/cudnn-linux-x86_64-9.6.0.74_cuda12-archive.tar.xz \
        && tar -xf cudnn-linux-x86_64-9.6.0.74_cuda12-archive.tar.xz \
        && cp cudnn-linux-x86_64-9.6.0.74_cuda12-archive/include/cudnn*.h /usr/local/cuda/include/ \
        && cp cudnn-linux-x86_64-9.6.0.74_cuda12-archive/lib/libcudnn* /usr/local/cuda/lib64/ \
        && chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn* \
        && rm -rf cudnn-linux-x86_64-9.6.0.74_cuda12-archive* \
        && echo '/usr/local/cuda/lib64' >> /etc/ld.so.conf.d/cuda.conf \
        && ldconfig; \
    fi

# 升级pip以支持较新的Python包
RUN python3 -m pip install --upgrade pip

# 设置工作目录
WORKDIR /app

# 克隆最新的 KataGo 源码（如果没有本地源码）
# 注意：在实际使用中，建议将源码作为构建上下文的一部分
RUN git clone https://github.com/lightvector/KataGo.git katago-source || echo "Using local source"

# 复制 KataGo 源码（如果有本地源码）
COPY KataGo-BlackRice/cpp/ /app/katago-source/cpp/ 2>/dev/null || echo "No local KataGo source found, using git clone"

# 编译 KataGo
WORKDIR /app/katago-source/cpp

# 设置CUDA环境变量（如果使用CUDA）
RUN if [ "$USE_BACKEND" = "CUDA" ] || [ "$USE_BACKEND" = "TENSORRT" ]; then \
        export PATH=/usr/local/cuda/bin:$PATH \
        && export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH; \
    fi

# 条件编译：根据后端类型进行编译
RUN if [ "$USE_BACKEND" = "CUDA" ] || [ "$USE_BACKEND" = "TENSORRT" ]; then \
        export PATH=/usr/local/cuda/bin:$PATH \
        && export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH \
        && cmake . \
            -G Ninja \
            -DUSE_BACKEND=${USE_BACKEND} \
            -DUSE_TCMALLOC=${USE_TCMALLOC} \
            -DUSE_AVX2=${USE_AVX2} \
            -DBUILD_DISTRIBUTED=${BUILD_DISTRIBUTED} \
            -DCMAKE_BUILD_TYPE=Release \
            -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda \
            -DCUDNN_INCLUDE_DIR=/usr/local/cuda/include \
            -DCUDNN_LIBRARY=/usr/local/cuda/lib64/libcudnn.so \
        && ninja; \
    else \
        cmake . \
            -G Ninja \
            -DUSE_BACKEND=${USE_BACKEND} \
            -DUSE_TCMALLOC=${USE_TCMALLOC} \
            -DUSE_AVX2=${USE_AVX2} \
            -DBUILD_DISTRIBUTED=${BUILD_DISTRIBUTED} \
            -DCMAKE_BUILD_TYPE=Release \
        && ninja; \
    fi

# 运行阶段
ARG USE_BACKEND=EIGEN
ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE} AS runtime

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# 传递构建参数到运行时
ARG USE_BACKEND=EIGEN

# 安装基础运行时依赖
RUN apt-get update && apt-get install -y \
    libzip4 \
    zlib1g \
    libssl3 \
    libgoogle-perftools4 \
    curl \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# CUDA运行时已包含在基础镜像中（当USE_BACKEND=CUDA时）
# 确保CUDA库路径正确配置
RUN if [ "$USE_BACKEND" = "CUDA" ] || [ "$USE_BACKEND" = "TENSORRT" ]; then \
        echo '/usr/local/cuda/lib64' >> /etc/ld.so.conf.d/cuda.conf \
        && ldconfig; \
    fi

# 设置工作目录
WORKDIR /app

# 从构建阶段复制编译好的 KataGo 可执行文件
COPY --from=builder /app/katago-source/cpp/katago /usr/local/bin/katago

# 复制 HTTP 服务器代码
COPY . /app/

# 升级pip并安装Python依赖
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

# 检查 KataGo 二进制文件
RUN echo "=== KataGo binary info ===" && \
    file /usr/local/bin/katago && \
    echo "=== KataGo version ===" && \
    katago version && \
    echo "=== KataGo help ===" && \
    katago help || echo "KataGo binary ready"

# 创建必要的目录
RUN mkdir -p /app/logs /app/models /app/configs

# 创建现代化的配置文件
RUN echo '# KataGo HTTP Server Configuration\n\
# 基本设置\n\
logDir = /app/logs\n\
logAllRequests = true\n\
logAllResponses = false\n\
logTimeStamp = true\n\
\n\
# 搜索设置\n\
maxVisits = 1000\n\
maxPlayouts = 10000\n\
maxTime = 10.0\n\
numSearchThreads = 8\n\
\n\
# 神经网络设置\n\
nnMaxBatchSize = 32\n\
nnCacheSizePowerOfTwo = 20\n\
nnRandomize = true\n\
nnPolicyTemperature = 1.0\n\
\n\
# 搜索参数\n\
cpuctExploration = 1.0\n\
cpuctExplorationLog = 0.45\n\
fpuReductionMax = 0.2\n\
rootFpuReductionMax = 0.1\n\
valueWeightExponent = 0.5\n\
\n\
# 性能优化\n\
reportAnalysisWinratesAs = BLACK' > /app/configs/katago_gtp.cfg

# 创建健康检查脚本
RUN echo '#!/bin/bash\n\
curl -f http://localhost:8080/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# 暴露端口（统一使用8080）
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# 启动服务器（使用升级后的服务器脚本）
CMD ["python3", "katago_server.py"]