# Multi-stage build for KataGo OpenCL

# Stage 1: Build
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    pkg-config \
    libzip-dev \
    zlib1g-dev \
    libeigen3-dev \
    libssl-dev \
    libgoogle-perftools-dev \
    ocl-icd-opencl-dev \
    opencl-headers \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY KataGo-BlackRice /app/KataGo-BlackRice

# Compile KataGo with OpenCL backend
WORKDIR /app/KataGo-BlackRice/cpp
RUN cmake . \
    -G Ninja \
    -DUSE_BACKEND=OPENCL \
    -DUSE_TCMALLOC=1 \
    -DNO_GIT_REVISION=1 \
    -DCMAKE_BUILD_TYPE=Release \
    && ninja

# Stage 2: Runtime
FROM ubuntu:22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libzip4 \
    zlib1g \
    libssl3 \
    libgoogle-perftools4 \
    ocl-icd-libopencl1 \
    clinfo \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# NVIDIA OpenCL support
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

WORKDIR /app

# Copy compiled binary from builder
COPY --from=builder /app/KataGo-BlackRice/cpp/katago /usr/local/bin/katago

# Copy HTTP server code and requirements
COPY katago-server /app/katago-server
COPY katago_analysis_server.py /app/
COPY katago-server/requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt && \
    pip3 install --no-cache-dir flask-cors

# Create necessary directories
RUN mkdir -p /app/models /app/logs /app/configs

# Copy weights and config
COPY Weights/kata1-b18c384nbt-s9996604416-d4316597426.bin.gz /app/models/model.bin.gz
COPY configs/katago_opencl.cfg /app/configs/katago_opencl.cfg

# Create server_config.json for internal use
RUN echo '{"katago_binary": "/usr/local/bin/katago", "model_file": "/app/models/model.bin.gz", "config_file": "/app/configs/katago_opencl.cfg", "port": 8086, "max_variations": 15}' > /app/server_config.json

# Health check script
RUN echo '#!/bin/bash' > /app/health_check.sh && \
    echo 'curl -f http://localhost:8086/health || exit 1' >> /app/health_check.sh && \
    chmod +x /app/health_check.sh

# Expose port 8086 as requested
EXPOSE 8086

HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
    CMD /app/health_check.sh

# Start the analysis server
CMD ["python3", "/app/katago_analysis_server.py"]
