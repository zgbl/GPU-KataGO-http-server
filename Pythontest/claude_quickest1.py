#!/usr/bin/env python3
import requests
import json
import time

def test_different_configs():
    """测试不同的配置参数组合"""
    base_url = "http://localhost:8080"
    
    # 固定测试局面
    test_moves = [["B", "R16"], ["W", "C4"], ["B", "Q3"]]
    
    print("=" * 70)
    print("KataGo HTTP Server 配置参数测试")
    print("=" * 70)
    
    # 不同配置组合
    config_tests = [
        {
            "name": "基础配置",
            "config": {
                "request_id": "test_basic",
                "max_visits": 100
            }
        },
        {
            "name": "高访问次数",
            "config": {
                "request_id": "test_high_visits",
                "max_visits": 5000
            }
        },
        {
            "name": "包含所有分析选项",
            "config": {
                "request_id": "test_all_options",
                "max_visits": 1000,
                "include_ownership": True,
                "include_policy": True,
                "include_pv": True,
                "include_moves_ownership": True,
                "include_moves_ownership_stdev": True
            }
        },
        {
            "name": "仅启用PV",
            "config": {
                "request_id": "test_pv_only",
                "max_visits": 1000,
                "include_pv": True
            }
        },
        {
            "name": "仅启用Policy",
            "config": {
                "request_id": "test_policy_only", 
                "max_visits": 1000,
                "include_policy": True
            }
        },
        {
            "name": "启用分析深度",
            "config": {
                "request_id": "test_analysis_depth",
                "max_visits": 1000,
                "analyze_turns": 5,
                "include_pv": True,
                "include_policy": True
            }
        },
        {
            "name": "添加komi和规则",
            "config": {
                "request_id": "test_komi_rules",
                "max_visits": 1000,
                "komi": 7.5,
                "rules": "Chinese",
                "include_pv": True
            }
        },
        {
            "name": "最大配置",
            "config": {
                "request_id": "test_max_config",
                "max_visits": 3000,
                "komi": 7.5,
                "rules": "Chinese", 
                "include_ownership": True,
                "include_policy": True,
                "include_pv": True,
                "include_moves_ownership": True,
                "include_moves_ownership_stdev": True,
                "analyze_turns": 10,
                "priority": "high"
            }
        }
    ]
    
    for i, test in enumerate(config_tests):
        print(f"\n[测试 {i+1}] {test['name']}")
        print(f"配置: {json.dumps(test['config'], indent=2)}")
        
        payload = {
            "board_size": 19,
            "moves": test_moves,
            "config": test['config']
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/select-move/katago_gtp_bot",
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                diagnostics = data.get('diagnostics', {})
                
                print(f"✅ 响应成功 (耗时: {elapsed:.2f}s)")
                print(f"  bot_move (外层): {data.get('bot_move')}")
                print(f"  bot_move (内层): {diagnostics.get('bot_move')}")
                print(f"  score: {diagnostics.get('score')}")
                print(f"  winprob: {diagnostics.get('winprob')}")
                print(f"  visits: {diagnostics.get('visits')}")
                print(f"  last_move_color: {diagnostics.get('last_move_color')}")
                
                best_ten = diagnostics.get('best_ten', [])
                print(f"  best_ten数量: {len(best_ten)}")
                
                if best_ten:
                    print("  前3个最佳走法:")
                    for j, move_info in enumerate(best_ten[:3]):
                        print(f"    {j+1}. {move_info}")
                
                # 检查其他可能的字段
                other_fields = ['ownership', 'policy', 'pv', 'moves_ownership']
                for field in other_fields:
                    if field in diagnostics:
                        value = diagnostics[field]
                        if isinstance(value, list):
                            print(f"  {field}: 列表长度={len(value)}")
                        else:
                            print(f"  {field}: {value}")
                
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"  错误内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 50)
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 70)
    print("🎯 分析总结:")
    print("1. 查看哪个配置能返回 best_ten 数据")
    print("2. 确认哪些参数真正生效")
    print("3. 找到获取胜率信息的正确方式")
    print("=" * 70)

if __name__ == "__main__":
    test_different_configs()