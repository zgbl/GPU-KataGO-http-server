# KataGo-BlackRice vs katago-server 版本差异分析

## 📊 总体差异概览

| 项目 | KataGo-BlackRice | katago-server |
|------|------------------|---------------|
| **基础镜像** | Ubuntu 22.04 / CUDA 12.9.1 | Ubuntu 18.04 |
| **Python版本** | Python 3.10+ | Python 3.6+ |
| **CUDA支持** | CUDA 12.9.1 + cuDNN 9.6.0 | 无GPU支持 |
| **KataGo版本** | 最新源码编译 | 预编译二进制(旧版) |
| **HTTP端口** | 8080/8081 | 2718/2818 |
| **架构** | 多后端支持 | 仅CPU(Eigen) |

## 🐳 Docker 配置差异

### 基础镜像

**KataGo-BlackRice:**
```dockerfile
# 支持多种基础镜像
ARG BASE_IMAGE=ubuntu:22.04
# GPU版本使用
nvidia/cuda:12.9.1-cudnn-devel-ubuntu22.04
```

**katago-server:**
```dockerfile
# 固定使用旧版本
FROM ubuntu:18.04
```

### 系统依赖

**KataGo-BlackRice:**
- Ubuntu 22.04 现代包管理
- CUDA 12.9.1 工具链
- cuDNN 9.6.0
- 现代 CMake + Ninja 构建
- 多后端编译支持

**katago-server:**
- Ubuntu 18.04 (已过时)
- 仅基础 Python 依赖
- 预编译二进制文件
- 无GPU支持

## 🐍 Python 环境差异

### Python 版本支持

**KataGo-BlackRice:**
- Python 3.10+ (Ubuntu 22.04 默认)
- 现代包管理和依赖解析

**katago-server:**
- Python 3.6+ (Ubuntu 18.04 默认)
- 旧版本包依赖

### Python 依赖对比

**KataGo-BlackRice HTTP服务:**
```python
# 现代版本
requests
flask>=2.0
gunicorn>=20.1
numpy>=1.20
psutil
prometheus-client
```

**katago-server:**
```python
# 固定旧版本
click==7.1.2
Flask==1.1.2
gunicorn==20.0.4
itsdangerous==1.1.0
Jinja2==2.11.2
MarkupSafe==1.1.1
Werkzeug==1.0.1
```

## ⚙️ KataGo 引擎差异

### 编译方式

**KataGo-BlackRice:**
- 从最新源码编译
- 支持多后端: CUDA, OpenCL, Eigen
- 优化编译参数
- 支持分布式训练

**katago-server:**
- 使用预编译二进制 `katago_eigen`
- 仅支持 CPU (Eigen 后端)
- 版本较旧，功能受限

### 性能对比

| 特性 | KataGo-BlackRice | katago-server |
|------|------------------|---------------|
| **GPU加速** | ✅ CUDA 12.9.1 | ❌ 仅CPU |
| **多线程** | ✅ 优化支持 | ⚠️ 基础支持 |
| **内存优化** | ✅ tcmalloc | ⚠️ 系统默认 |
| **AVX2指令** | ✅ 支持 | ❓ 未知 |
| **最新算法** | ✅ 最新源码 | ❌ 旧版本 |

## 🌐 HTTP 服务差异

### 端口配置

**KataGo-BlackRice:**
- 主端口: 8080
- 备用端口: 8081
- 标准HTTP服务端口

**katago-server:**
- 主端口: 2718
- 备用端口: 2818
- 自定义端口范围

### API 架构

**KataGo-BlackRice:**
- 基于 KataGo 原生 HTTP 服务
- 直接使用 `katago http` 模式
- 更好的性能和稳定性

**katago-server:**
- Flask 包装的 GTP 接口
- 通过 subprocess 调用 KataGo
- 额外的进程开销

## 🔧 配置文件差异

### KataGo 配置

**KataGo-BlackRice (`katago_http.cfg`):**
```ini
# 现代配置格式
maxVisits = 1000
maxTime = 10.0
numSearchThreads = 8
nnMaxBatchSize = 32
logDir = /app/logs
```

**katago-server (`gtp_*.cfg`):**
```ini
# 旧版GTP配置格式
# 配置选项较少
# 性能参数受限
```

## 🚀 部署差异

### Docker Compose 对比

**KataGo-BlackRice:**
```yaml
# 多服务架构
services:
  katago-cpu:     # CPU版本
  katago-gpu:     # GPU版本
  katago-opencl:  # OpenCL版本
  katago-http-server: # HTTP服务
  katago-dev:     # 开发环境
```

**katago-server:**
```yaml
# 单一服务
services:
  katago-server:  # 仅HTTP服务
```

### 资源需求

| 资源 | KataGo-BlackRice | katago-server |
|------|------------------|---------------|
| **内存** | 4GB+ (GPU版本) | 1GB+ |
| **GPU** | NVIDIA GPU推荐 | 不需要 |
| **存储** | 2GB+ | 500MB+ |
| **CPU** | 4核+ | 2核+ |

## ⚠️ 兼容性问题

### 主要不兼容点

1. **Python版本不兼容**
   - KataGo-BlackRice: Python 3.10+
   - katago-server: Python 3.6+
   - 需要升级所有Python依赖

2. **Flask版本冲突**
   - 新版本: Flask 2.x
   - 旧版本: Flask 1.1.2
   - API接口可能有变化

3. **系统库差异**
   - Ubuntu 22.04 vs 18.04
   - 不同的系统库版本
   - 可能的ABI不兼容

4. **端口冲突**
   - 不同的默认端口
   - 需要调整客户端配置

## 🔄 升级路径建议

### 阶段1: 环境升级
1. ✅ 升级基础镜像: Ubuntu 18.04 → 22.04
2. ✅ 升级Python: 3.6 → 3.10+
3. ✅ 升级系统依赖

### 阶段2: 依赖升级
1. ✅ 升级Flask: 1.1.2 → 2.x
2. ✅ 升级其他Python包
3. ✅ 解决依赖冲突

### 阶段3: KataGo升级
1. ✅ 替换预编译二进制为源码编译
2. ✅ 添加GPU支持
3. ✅ 优化配置文件

### 阶段4: 服务整合
1. ✅ 统一端口配置
2. ✅ 整合HTTP服务
3. ✅ 添加监控和健康检查

## 📋 升级检查清单

### 必须解决的问题
- [ ] **基础镜像升级**: Ubuntu 18.04 → 22.04
- [ ] **Python环境升级**: 3.6 → 3.10+
- [ ] **Flask版本升级**: 1.1.2 → 2.x
- [ ] **KataGo引擎升级**: 预编译 → 源码编译
- [ ] **GPU支持添加**: CPU-only → CUDA 12.9.1
- [ ] **端口标准化**: 2718 → 8080
- [ ] **配置文件迁移**: GTP → HTTP格式

### 可选优化项目
- [ ] **性能优化**: 添加tcmalloc
- [ ] **监控添加**: Prometheus指标
- [ ] **日志改进**: 结构化日志
- [ ] **健康检查**: 完善的健康检查
- [ ] **安全加固**: 非root用户运行

## 🎯 下一步行动计划

1. **立即执行**: 升级katago-server的基础环境
2. **优先级高**: 解决Python依赖冲突
3. **中期目标**: 整合GPU支持
4. **长期目标**: 完全迁移到KataGo-BlackRice架构

---

**总结**: katago-server项目需要进行全面的现代化升级，主要包括基础环境、Python依赖、KataGo引擎和GPU支持等方面。建议采用渐进式升级策略，确保每个阶段的稳定性。