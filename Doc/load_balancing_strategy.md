# KataGo 并发架构与负载均衡指南 (基于棋谱 Hash 的会话保持)

当分析任务增加时，部署多个 KataGo 引擎能充分利用 GPU。但是传统负载均衡遇到了特殊挑战。

## 核心痛点：为什么不能用 IP Hash？
1. 所有的分析请求很可能全部来自于你自己的同一个后端业务服务（比如同一个 Node.js/Python 进程发出的 HTTP 请求），这时来源 IP 永远只有一个。IP Hash 就会把所有流量全打爆在一个 KataGo 容器上，另一个完全闲置。
2. KataGo 内部有 MCTS（蒙特卡洛树搜索）缓存。**同一个棋谱（对局）的连续步数分析，必须始终路由到同一个 KataGo Engine。**如果打乱分发，它们无法重用上一回合的思考树，会导致大量算力浪费。

**真正的需求是：基于棋谱 Hash 的 Sticky Session（会话保持）。**

---

## 方案一：Nginx 一致性哈希 (基于棋谱前 50 步的 Header) —— 【性能最高，推荐】

最优雅且解耦的高并发方案是： **让发送请求的前端在 HTTP Header 中带上一个 `X-Game-Hash`。**
- **Hash 生成规则：** 提取棋谱的**前 50 步**（如果不足 50 步则取当前所有步数），拼成字符串后计算一个 Hash (如 MD5)。
- Nginx 会根据这个 Header 计算 Hash 并一致性地分配到同一个后端容器。

### 1. 架构流转
```
      POST /analyze
      Header: X-Game-Hash: <前50步算出的一致性Hash>
               |
            [Nginx 代理层: 8060端口] (使用 hash $http_x_game_hash consistent 算法)
           /        \
 (Hash: game_001_id) \
         /            \
 [Engine 1: 8081]  [Engine 2: 8082]
```

### 2. Nginx 配置示例 (`nginx.conf`)
新建一个 `nginx.conf`，利用 `hash ... consistent` 指令实现真正的棋谱绑定路由：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream katago_backend {
        # 【核心配置】根据请求头 X-Game-Hash 的值进行一致性哈希路由
        hash $http_x_game_hash consistent;
        
        server host.docker.internal:8081;  # Engine 1
        server host.docker.internal:8082;  # Engine 2
        # 可以随时加 Engine 3, Engine 4... consistent 参数保证加机器时缓存抖动最小
    }

    server {
        listen 8080;          # 发布对外的统一入口

        location / {
            proxy_pass http://katago_backend;
            
            # 对于较长时间的深度分析，建议增加超时时间
            proxy_read_timeout 120s;
        }
    }
}
```

---

## 方案二：自建 API Router / 调度中台 (基于 Request Body 解析)

如果不想改动“原本发请求的代码（即不想强行塞一个 HTTP Header）”，或者想要做复杂的动态调度（如：当某台引擎崩了自动剔除重试，或依据引擎 GPU 占用率进行智能摘除），你可以用 Python/Node写一个几十行代码的 API Router 层。

### 1. 架构流转
不需要加任何 Header。客户端只管发送原始的 JSON 给 Router，Router 拆解出 JSON 里面的 `moves` 数组并计算 Hash 分发。
```
          [ Python FastAPI / Node.js Router (网关层) ]
                   |
    1. 解析 POST 请求体: payload = await request.json()
    2. 计算哈希: hash_id = hash(str(payload['moves'])) % len(engines)
    3. 代理转发: 转发给 engines[hash_id] 并透传返回值
```

### 2. Python (FastAPI/requests) 伪代码实现示例：
```python
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 可用后端的列表配置
ENGINES = ["http://localhost:8081", "http://localhost:8082"]

@app.route('/analyze', methods=['POST'])
def proxy_analyze():
    req_data = request.json
    moves = req_data.get('moves', [])
    
    # 核心：根据前几十步的 moves 阵列计算 MD5 哈希作为粘性标识
    moves_str = str(moves).encode('utf-8')
    game_hash_val = int(hashlib.md5(moves_str).hexdigest(), 16)
    
    # 取模分配到具体的引擎
    target_idx = game_hash_val % len(ENGINES)
    target_url = ENGINES[target_idx]
    
    # 透传请求给对应的 KataGo Engine
    resp = requests.post(f"{target_url}/analyze", json=req_data)
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(port=8080)
```
**优点**：不需要客户端做任何改造，网关直接接管、智能调度。甚至可以定制“只拿前2步落子算Hash”的深度逻辑。
**缺点**：增加了一个自己写的服务组件需要维护。
