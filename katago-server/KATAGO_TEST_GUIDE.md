# KataGo HTTP服务器检查和测试指南

## 🚀 快速检查服务器状态

### 1. 检查Docker容器状态
```bash
# 查看容器运行状态
docker ps

# 查看容器日志（最近20行）
docker logs --tail 20 katago-http-server

# 实时查看日志
docker logs -f katago-http-server
```

### 2. 检查KataGo是否正常启动
在容器日志中查找以下关键信息：
- ✅ `Loaded neural net with nnXLen 19 nnYLen 19` - 神经网络加载成功
- ✅ `Loaded config gtp_ahn_eigen.cfg` - 配置文件加载成功
- ✅ `Loaded model g170e-b10c128-s1141046784-d204142634.bin.gz` - 模型文件加载成功
- ✅ `GTP ready, beginning main protocol loop` - KataGo引擎准备就绪

## 🧪 HTTP API测试

### 方法1: 使用PowerShell测试

#### 测试获取最佳走法API
```powershell
Invoke-RestMethod -Uri "http://localhost:2818/select-move/katago_gtp_bot" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"board_size": 19, "moves": ["R4", "D16"]}'
```

#### 测试局面评估API
```powershell
Invoke-RestMethod -Uri "http://localhost:2818/score/katago_gtp_bot" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"board_size": 19, "moves": ["R4", "D16", "Q16"]}'
```

### 方法2: 使用Python测试脚本
```bash
# 运行完整测试套件
python test_server.py http://localhost:2818
```

### 方法3: 使用curl (在WSL或Linux环境)
```bash
# 测试获取走法
curl -X POST http://localhost:2818/select-move/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{"board_size": 19, "moves": ["R4", "D16"]}'

# 测试局面评估
curl -X POST http://localhost:2818/score/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{"board_size": 19, "moves": ["R4", "D16", "Q16"]}'
```

## 📊 API响应格式

### select-move API响应示例
```json
{
  "bot_move": "Q16",
  "diagnostics": {
    "best_ten": [
      {"move": "Q16", "visits": 512, "winrate": 0.52},
      {"move": "D4", "visits": 256, "winrate": 0.51}
    ],
    "score": -0.7,
    "winrate": 0.52
  }
}
```

### score API响应示例
```json
{
  "diagnostics": {
    "score": -0.796368,
    "winrate": 0.48,
    "best_ten": [...]
  }
}
```

## 🔧 常见问题排查

### 问题1: 容器显示"unhealthy"状态
**原因**: 健康检查失败，通常是因为服务器还在启动中
**解决**: 等待1-2分钟让KataGo完全加载，或查看日志确认启动状态

### 问题2: API返回404错误
**原因**: 端口或路径错误
**解决**: 确认使用正确的端口2818和API路径

### 问题3: API响应超时
**原因**: KataGo计算时间较长
**解决**: 增加请求超时时间，或在配置文件中减少`maxPlayouts`参数

### 问题4: 容器无法启动
**原因**: 可能是依赖库缺失
**解决**: 重新构建Docker镜像
```bash
docker-compose down
docker-compose up --build -d
```

## ⚙️ 性能调优

### 修改KataGo配置
编辑 `gtp_ahn_eigen.cfg` 文件：
- `numSearchThreads = 12` - 搜索线程数（根据CPU核心数调整）
- `maxPlayouts = 1024` - 最大模拟次数（影响计算时间和强度）
- `ponderingEnabled = false` - 是否启用思考模式

### 监控资源使用
```bash
# 查看容器资源使用情况
docker stats katago-http-server

# 查看系统资源
top
htop
```

## 🌐 在浏览器中测试

可以使用浏览器开发者工具或Postman等工具发送POST请求到：
- `http://localhost:2818/select-move/katago_gtp_bot`
- `http://localhost:2818/score/katago_gtp_bot`

## 📝 日志分析

### 正常运行的日志特征
- 没有错误信息
- 定期的HTTP请求日志
- KataGo响应时间合理（通常几秒内）

### 异常日志特征
- `error while loading shared libraries` - 依赖库缺失
- `Katago died. Resurrecting.` - KataGo进程崩溃
- 长时间无响应 - 可能是计算复杂度过高

## 🎯 测试建议

1. **基础测试**: 先用简单的2-3手棋局面测试
2. **复杂测试**: 逐步增加棋局复杂度
3. **压力测试**: 并发发送多个请求测试性能
4. **边界测试**: 测试异常输入（如无效走法、超大棋盘等）

## 📞 获取帮助

如果遇到问题，请：
1. 查看容器日志获取详细错误信息
2. 检查网络连接和端口占用
3. 确认Docker和相关依赖正确安装
4. 参考项目README和配置文件说明