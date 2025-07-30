# Pythontest 目录

这个目录包含了开发过程中创建的各种Python测试脚本和工具。这些文件不是项目的核心组件，但可能在开发和调试时有用。

## 📁 文件说明

### 🔧 服务器相关
- `katago_integrated_server.py` - 整合版服务器（已被katago_analysis_server.py替代）
- `katago_score_interface_test.py` - 评分接口测试

### 🧪 测试工具
- `test_integrated_server.py` - 完整的HTTP API测试套件
- `test_api_fix.py` - API修复测试
- `test_server_fix.py` - 服务器修复测试
- `test_user_sgf.py` - 用户SGF测试

### 📋 SGF分析工具
- `demo_sgf_tester.py` - 自动化SGF测试演示
- `sgf_http_tester.py` - 交互式SGF HTTP测试工具
- `demo_user_sgf.py` - 用户SGF演示

### 🚀 客户端示例
- `example_client.py` - HTTP API客户端示例
- `claude_quickest1.py` - 快速测试脚本1
- `claude_quicktest2.py` - 快速测试脚本2
- `simpy_test.py` - 简单测试脚本

## 🔧 使用方法

从项目根目录运行这些脚本：

```bash
# 运行完整测试套件
python Pythontest/test_integrated_server.py

# 运行SGF测试工具
python Pythontest/sgf_http_tester.py

# 运行自动化演示
python Pythontest/demo_sgf_tester.py

# 运行客户端示例
python Pythontest/example_client.py
```

## ⚠️ 注意事项

1. 这些脚本中的路径引用已经更新，可以从项目根目录正常运行
2. 某些脚本可能依赖特定的服务器配置或环境
3. 建议优先使用项目根目录的核心文件：
   - `katago_analysis_server.py` - 主服务器
   - `http_test.py` - 主测试工具

## 🗂️ 文件状态

- ✅ 路径已更新，可正常运行
- 📦 保留用于开发和调试
- 🔄 部分功能可能与核心文件重复