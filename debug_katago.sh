#!/bin/bash

echo "=== KataGo 调试信息 ==="

echo "1. 检查 GPU 状态:"
nvidia-smi

echo -e "\n2. 检查文件存在性:"
ls -la /app/bin/katago
ls -la /app/models/
ls -la /app/configs/katago_gtp.cfg

echo -e "\n3. 测试 KataGo 版本:"
/app/bin/katago version

echo -e "\n4. 测试 KataGo 基本功能:"
echo "quit" | timeout 30 /app/bin/katago gtp -model /app/models/model.bin.gz -config /app/configs/katago_gtp.cfg

echo -e "\n5. 检查配置文件内容:"
head -20 /app/configs/katago_gtp.cfg

echo -e "\n6. 检查进程状态:"
ps aux | grep katago

echo -e "\n7. 检查内存使用:"
free -h

echo -e "\n8. 检查磁盘空间:"
df -h

echo -e "\n=== 调试完成 ==="