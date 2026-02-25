#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows环境下的KataGo HTTP服务器测试脚本
"""

import os
import sys
import subprocess
import time
import requests
import json

def check_dependencies():
    """
    检查依赖是否满足
    """
    print("检查Python依赖...")
    
    try:
        import flask
        print(f"✅ Flask版本: {flask.__version__}")
    except ImportError:
        print("❌ Flask未安装，请运行: pip install flask")
        return False
    
    try:
        import requests
        print(f"✅ Requests可用")
    except ImportError:
        print("❌ Requests未安装，请运行: pip install requests")
        return False
    
    # 检查KataGo文件
    if os.path.exists('katago_eigen'):
        print("✅ 找到katago_eigen二进制文件")
    else:
        print("❌ 未找到katago_eigen文件")
        return False
    
    # 检查模型文件
    model_file = 'g170e-b10c128-s1141046784-d204142634.bin.gz'
    if os.path.exists(model_file):
        print(f"✅ 找到模型文件: {model_file}")
    else:
        print(f"❌ 未找到模型文件: {model_file}")
        return False
    
    return True

def install_dependencies():
    """
    安装Python依赖
    """
    print("安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def test_katago_binary():
    """
    测试KataGo二进制文件是否可以运行
    """
    print("测试KataGo二进制文件...")
    
    # 在Windows上，可能需要WSL或者Linux兼容层
    try:
        # 尝试直接运行
        result = subprocess.run(['./katago_eigen', 'version'], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ KataGo二进制文件可以运行")
            print(f"版本信息: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ KataGo运行失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ 无法运行KataGo二进制文件 (可能需要WSL或Linux环境)")
        return False
    except subprocess.TimeoutExpired:
        print("❌ KataGo运行超时")
        return False
    except Exception as e:
        print(f"❌ 运行KataGo时出错: {e}")
        return False

def start_server_process():
    """
    启动服务器进程
    """
    print("启动KataGo HTTP服务器...")
    
    try:
        # 使用katago_server_eigen.py，因为它使用CPU版本
        process = subprocess.Popen([sys.executable, 'katago_server_eigen.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待服务器启动
        print("等待服务器启动...")
        for i in range(30):  # 等待30秒
            try:
                response = requests.get('http://localhost:2818', timeout=2)
                print("✅ 服务器已启动")
                return process
            except:
                time.sleep(1)
                if i % 5 == 0:
                    print(f"等待中... ({i}/30秒)")
        
        print("❌ 服务器启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return None

def test_api(base_url="http://localhost:2818"):
    """
    测试API功能
    """
    print(f"测试API: {base_url}")
    
    test_data = {
        "board_size": 19,
        "moves": ["R4", "D16"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # 测试获取走法
        print("测试获取最佳走法...")
        response = requests.post(
            f"{base_url}/select-move/katago_gtp_bot",
            data=json.dumps(test_data),
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API测试成功!")
            print(f"推荐走法: {result.get('move', 'N/A')}")
            print(f"胜率: {result.get('win_prob', 'N/A')}")
            return True
        else:
            print(f"❌ API测试失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API测试出错: {e}")
        return False

def main():
    print("KataGo HTTP服务器 Windows测试工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n尝试安装依赖...")
        if not install_dependencies():
            print("\n❌ 无法安装依赖，请手动安装")
            return False
    
    # 测试KataGo二进制
    if not test_katago_binary():
        print("\n⚠️  KataGo二进制文件无法在Windows上直接运行")
        print("建议使用以下方案之一:")
        print("1. 使用WSL (Windows Subsystem for Linux)")
        print("2. 使用Docker (推荐)")
        print("3. 在Linux虚拟机中运行")
        return False
    
    # 启动服务器
    server_process = start_server_process()
    if not server_process:
        return False
    
    try:
        # 测试API
        if test_api():
            print("\n🎉 所有测试通过!")
            return True
        else:
            return False
    finally:
        # 清理
        if server_process:
            print("\n停止服务器...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)