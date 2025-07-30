#!/usr/bin/env python3
import requests
import json
import time

def deep_response_analysis():
    """深度分析KataGo HTTP服务器的响应结构"""
    base_url = "http://localhost:8080"
    
    print("=" * 80)
    print("KataGo HTTP Server 深度响应分析")
    print("=" * 80)
    
    # 测试不同的endpoint和参数组合
    test_cases = [
        {
            "name": "标准 select-move 接口",
            "endpoint": "/select-move/katago_gtp_bot",
            "payload": {
                "board_size": 19,
                "moves": [["B", "R16"], ["W", "C4"], ["B", "Q3"]],
                "config": {
                    "request_id": "deep_analysis_1",
                    "max_visits": 1000,
                    "include_ownership": True,
                    "include_policy": True,
                    "include_pv": True,
                    "komi": 7.5,
                    "rules": "Chinese"
                }
            }
        },
        {
            "name": "尝试 analyze 接口",
            "endpoint": "/analyze/katago_gtp_bot", 
            "payload": {
                "board_size": 19,
                "moves": [["B", "R16"], ["W", "C4"], ["B", "Q3"]],
                "config": {
                    "request_id": "deep_analysis_2",
                    "max_visits": 1000,
                    "include_ownership": True,
                    "include_policy": True,
                    "include_pv": True
                }
            }
        },
        {
            "name": "尝试 query 接口",
            "endpoint": "/query/katago_gtp_bot",
            "payload": {
                "board_size": 19,
                "moves": [["B", "R16"], ["W", "C4"], ["B", "Q3"]],
                "config": {
                    "request_id": "deep_analysis_3",
                    "max_visits": 1000
                }
            }
        },
        {
            "name": "测试空局面",
            "endpoint": "/select-move/katago_gtp_bot",
            "payload": {
                "board_size": 19,
                "moves": [],
                "config": {
                    "request_id": "empty_board",
                    "max_visits": 1000,
                    "include_policy": True,
                    "include_pv": True
                }
            }
        },
        {
            "name": "测试单步局面",
            "endpoint": "/select-move/katago_gtp_bot", 
            "payload": {
                "board_size": 19,
                "moves": [["B", "D4"]],
                "config": {
                    "request_id": "single_move",
                    "max_visits": 2000,
                    "include_policy": True,
                    "include_pv": True,
                    "include_ownership": True
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[测试 {i+1}] {test_case['name']}")
        print(f"Endpoint: {test_case['endpoint']}")
        print("-" * 60)
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}{test_case['endpoint']}",
                json=test_case['payload'],
                timeout=30
            )
            elapsed = time.time() - start_time
            
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {elapsed:.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ JSON解析成功")
                    
                    # 打印完整的响应结构
                    print(f"\n完整响应结构:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # 分析响应的关键字段
                    print(f"\n关键字段分析:")
                    print(f"  顶层键: {list(data.keys())}")
                    
                    if 'diagnostics' in data:
                        diag = data['diagnostics']
                        print(f"  diagnostics键: {list(diag.keys())}")
                        
                        # 检查是否有我们期望的数据
                        expected_fields = ['bot_move', 'score', 'winprob', 'visits', 'best_ten', 'policy', 'ownership', 'pv']
                        for field in expected_fields:
                            if field in diag:
                                value = diag[field]
                                if isinstance(value, list):
                                    print(f"    {field}: 列表 (长度={len(value)})")
                                    if len(value) > 0:
                                        print(f"      第一个元素: {value[0]}")
                                elif isinstance(value, dict):
                                    print(f"    {field}: 字典 (键={list(value.keys())})")
                                else:
                                    print(f"    {field}: {value} (类型={type(value)})")
                            else:
                                print(f"    {field}: ❌ 缺失")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"原始响应内容: {response.text[:500]}...")
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"错误内容: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误 - 请确认服务器是否运行")
        except Exception as e:
            print(f"❌ 其他异常: {e}")
        
        print("=" * 60)
        time.sleep(1)

def test_gtp_commands():
    """测试直接的GTP命令格式"""
    print("\n" + "=" * 80)
    print("测试GTP命令格式")
    print("=" * 80)
    
    base_url = "http://localhost:8080"
    
    # 尝试发送GTP风格的命令
    gtp_tests = [
        {
            "name": "GTP analyze命令",
            "payload": {
                "command": "analyze",
                "args": ["B", "W", "interval", "1000"],
                "board_size": 19,
                "moves": [["B", "R16"], ["W", "C4"]]
            }
        },
        {
            "name": "GTP lz-analyze命令",
            "payload": {
                "command": "lz-analyze", 
                "args": ["1000"],
                "board_size": 19,
                "moves": [["B", "R16"], ["W", "C4"]]
            }
        }
    ]
    
    for test in gtp_tests:
        print(f"\n[GTP测试] {test['name']}")
        try:
            response = requests.post(
                f"{base_url}/gtp",
                json=test['payload'],
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("响应:", json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"错误: {response.text}")
                
        except Exception as e:
            print(f"异常: {e}")
            
        print("-" * 40)

def check_server_info():
    """检查服务器信息和可用接口"""
    print("\n" + "=" * 80) 
    print("服务器信息检查")
    print("=" * 80)
    
    base_url = "http://localhost:8080"
    
    # 尝试获取服务器信息
    info_endpoints = [
        "/",
        "/info", 
        "/status",
        "/health",
        "/api",
        "/help"
    ]
    
    for endpoint in info_endpoints:
        print(f"\n检查: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  JSON响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                except:
                    print(f"  文本响应: {response.text[:200]}...")
            else:
                print(f"  错误: {response.text[:100]}...")
        except Exception as e:
            print(f"  异常: {e}")

if __name__ == "__main__":
    # 执行所有测试
    deep_response_analysis()
    test_gtp_commands() 
    check_server_info()
    
    print("\n" + "=" * 80)
    print("🔍 诊断建议:")
    print("1. 检查服务器是否正确配置了分析参数")
    print("2. 确认KataGo引擎版本和配置文件")
    print("3. 查看服务器日志了解内部处理情况")
    print("4. 尝试不同的API接口和参数组合")
    print("=" * 80)