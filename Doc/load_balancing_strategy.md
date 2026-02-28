# KataGo 负载均衡与并发架构指南

当分析任务增加，单个 KataGo 容器（即便有强大的 GPU）也可能因为请求积压而导致响应变慢。为了充分利用 GPU 算力并处理高并发，我们可以部署多个 KataGo 引擎，并通过负载均衡器（Load Balancer）进行分发。

## 核心挑战：Sticky Session (会话保持)

 KataGo 内部有 MCTS（蒙特卡洛树搜索）缓存，如果一盘棋的不同步骤随机发给不同的实例，它们无法重用上一回合的思考树，会导致大量算力浪费。
因此，**同一个客户或同一盘对局的分析必须一直路由到同一个 KataGo Engine（即会话保持 / Sticky Session）**。

## 方案一：Nginx 反向代理与 IP Hash 负载均衡 (推荐)

这是最轻量、也最标准的解决方案。通过 Nginx 作为统一入口，将流量分发给后端的多个 KataGo 容器。

### 1. 架构示意
```
          (请求统一入口)
          http://IP:8080/analyze
                   |
                [Nginx] (使用 IP Hash 会话保持)
                /     \
    (来自IP A) /       \ (来自IP B)
              /         \
    [Engine 1: 8081]  [Engine 2: 8082]
    (处理局A的对弈)    (处理局B的对弈)
```

### 2. Nginx 配置示例 (`nginx.conf`)
新建一个 `nginx.conf`，利用 `ip_hash` 保证来自相同 IP 的请求始终落在同一个容器上。

```nginx
events {
    worker_connections 1024;
}

http {
    upstream katago_backend {
        ip_hash;              # 开启基于客户端 IP 的 Sticky Session
        server host.docker.internal:8081;  # Engine 1
        server host.docker.internal:8082;  # Engine 2
    }

    server {
        listen 8080;          # 发布对外的统一端口

        location / {
            proxy_pass http://katago_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # 对于较长时间的深度分析，建议增加超时时间
            proxy_read_timeout 120s;
        }
    }
}
```

## 方案二：应用层调度器 (Router)

如果你的所有请求都来自同一个后端（比如你写了一个 Python / Node.js 服务器，网关 IP 全是一样的），那么 IP Hash 就会失效（全打到一台机器上）。这时你应该在代码里自己调度。

### 调度逻辑：
1. **维护映射表**: 服务端维护一个字典，记录 `{ GameID: Engine_URL }` 的映射。
2. **处理新请求**: 
   - 提取请求里的 `GameID` (对局标识)。
   - `target_url = dict.get(GameID)`。
   - 如果不存在，则查询所有引擎的 `/queue/status` (或者自定义的负载指标)，挑选一个**当前最闲的引擎**，然后将 `GameID` 与它绑定，存入字典。
3. **转发并返回**: 把后续关于这个 `GameID` 的所有 HTTP 请求全都转发给 `target_url`。

对于 AI 对弈或分析，应用层转发其实更精细且防错，能保证绝对完美地错峰分发！

---
建议将多实例的启动命令写入一段单独的 `docker-compose-workers.yml` 中统一管理，以便根据服务器显存规模（如 8GB 建议 2-3 个实例）快速伸缩。
