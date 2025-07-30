# 快速开始指南 - 当前版本

## 🚀 一键启动

```bash
# 1. 启动服务器
docker-compose -f docker-compose.integrated.yml up --build -d

# 2. 检查状态
docker ps

# 3. 测试分析
python sgf_test_claude.py
```

## 📁 关键文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `katago_analysis_server.py` | **主服务器** | ✅ 正常工作 |
| `sgf_test_claude.py` | **测试工具** | ✅ 推荐使用 |
| `docker-compose.integrated.yml` | Docker配置 | ✅ 当前使用 |
| `CURRENT_STATUS.md` | 详细文档 | 📋 完整说明 |

## 🧪 测试步骤

### 1. 基本测试
```bash
# 健康检查
curl http://localhost:8080/health

# 应该返回: {"status": "healthy"}
```

### 2. SGF分析测试
```bash
python sgf_test_claude.py
```

选择选项：
- `2` - 使用示例SGF
- 输入分析范围 (如: `1-5`)
- 选择详细模式 (`y`)

### 3. API直接测试
```bash
# PowerShell
$body = @{
    board_size = 19
    moves = @(@("B", "Q16"), @("W", "D16"))
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8080/select-move/katago_gtp_bot" -Method Post -Body $body -ContentType "application/json"
```

## 📊 预期结果

成功的分析应该返回：
```json
{
    "bot_move": "D4",
    "winrate": 0.359,
    "score": -0.87,
    "visits": 118,
    "analysis": [
        {
            "move": "D4",
            "winrate": 0.359,
            "visits": 118,
            "scoreLead": -0.87
        }
    ]
}
```

## 🔧 故障排除

### 容器问题
```bash
# 查看日志
docker logs katago-integrated-server2

# 重启容器
docker-compose -f docker-compose.integrated.yml restart
```

### 端口问题
```bash
# 检查端口占用
netstat -an | findstr :8080
```

### 测试失败
1. 确认容器状态为 `healthy`
2. 检查 `docker logs` 输出
3. 验证端口8080可访问

## ✅ 验证清单

- [ ] Docker容器运行正常
- [ ] 健康检查返回 `healthy`
- [ ] SGF测试工具能正常分析
- [ ] API返回完整分析数据
- [ ] 胜率、分数、访问次数都有数值

---

**如果遇到问题，请查看 `CURRENT_STATUS.md` 获取详细信息**