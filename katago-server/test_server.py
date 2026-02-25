#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试KataGo HTTP服务器的脚本
"""

import requests
import json
import time
import sys

def test_katago_server(base_url="http://localhost:2718"):
    """
    测试KataGo服务器的基本功能
    """
    print(f"正在测试KataGo服务器: {base_url}")
    
    # 测试数据：一个简单的围棋局面
    test_data = {
        "board_size": 19,
        "moves": ["R4", "D16"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # 测试1: 获取最佳走法
        print("\n=== 测试1: 获取最佳走法 ===")
        response = requests.post(
            f"{base_url}/select-move/katago_gtp_bot",
            data=json.dumps(test_data),
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取走法成功!")
            print(f"推荐走法: {result.get('move', 'N/A')}")
            print(f"胜率: {result.get('win_prob', 'N/A')}")
            print(f"分数估计: {result.get('score', 'N/A')}")
            if 'best_moves' in result:
                print(f"前几个最佳走法: {result['best_moves'][:3]}")
        else:
            print(f"❌ 获取走法失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
        # 测试2: 获取局面评估
        print("\n=== 测试2: 获取局面评估 ===")
        response = requests.post(
            f"{base_url}/score/katago_gtp_bot",
            data=json.dumps(test_data),
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取评估成功!")
            print(f"胜率: {result.get('win_prob', 'N/A')}")
            print(f"分数: {result.get('score', 'N/A')}")
            if 'ownership' in result:
                print("✅ 包含领域信息")
        else:
            print(f"❌ 获取评估失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
        print("\n🎉 所有测试通过! KataGo HTTP服务器运行正常.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        print("请确保服务器正在运行并且端口2718可访问")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def wait_for_server(base_url="http://localhost:2718", max_wait=60):
    """
    等待服务器启动
    """
    print(f"等待服务器启动 (最多等待{max_wait}秒)...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print("✅ 服务器已启动!")
            return True
        except:
            if i % 10 == 0:
                print(f"等待中... ({i}/{max_wait}秒)")
            time.sleep(1)
    
    print("❌ 服务器启动超时")
    return False

if __name__ == "__main__":
    base_url = "http://localhost:2718"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print("KataGo HTTP服务器测试工具")
    print("=" * 40)
    
    # 等待服务器启动
    if wait_for_server(base_url):
        # 运行测试
        success = test_katago_server(base_url)
        sys.exit(0 if success else 1)
    else:
        print("无法连接到服务器")
        sys.exit(1)