#!/usr/bin/env python3
import requests
import json

def test_katago_api():
    """简单测试KataGo API的不同局面"""
    base_url = "http://localhost:8080"
    
    test_cases = [
        {
            "name": "空局面",
            "moves": []
        },
        {
            "name": "第1手 - 黑R16",
            "moves": [["B", "R16"]]
        },
        {
            "name": "第2手 - 白C4",
            "moves": [["B", "R16"], ["W", "C4"]]
        },
        {
            "name": "第3手 - 黑Q3",
            "moves": [["B", "R16"], ["W", "C4"], ["B", "Q3"]]
        },
        {
            "name": "第4手 - 白D17",
            "moves": [["B", "R16"], ["W", "C4"], ["B", "Q3"], ["W", "D17"]]
        },
        {
            "name": "完全不同的开局",
            "moves": [["B", "D4"], ["W", "Q16"], ["B", "D16"]]
        }
    ]
    
    print("=" * 60)
    print("KataGo API 测试 - 验证是否有缓存问题")
    print("=" * 60)
    
    for i, test in enumerate(test_cases):
        print(f"\n[测试 {i+1}] {test['name']}")
        print(f"着法: {test['moves']}")
        
        payload = {
            "board_size": 19,
            "moves": test["moves"],
            "config": {
                "request_id": f"test_{i+1}",
                "max_visits": 500
            }
        }
        
        try:
            response = requests.post(
                f"{base_url}/select-move/katago_gtp_bot",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                diagnostics = data.get('diagnostics', {})
                
                print(f"  推荐走法: {diagnostics.get('bot_move', 'N/A')}")
                print(f"  分数: {diagnostics.get('score', 'N/A')}")
                print(f"  胜率: {diagnostics.get('winprob', 'N/A')}")
                print(f"  最后手颜色: {diagnostics.get('last_move_color', 'N/A')}")
                print(f"  best_ten数量: {len(diagnostics.get('best_ten', []))}")
                
                # 如果有best_ten，显示第一个
                best_ten = diagnostics.get('best_ten', [])
                if best_ten:
                    first = best_ten[0]
                    print(f"  最佳走法详情: {first.get('move', 'N/A')} (胜率: {first.get('winrate', 'N/A')}, 访问: {first.get('visits', 'N/A')})")
                
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"  错误信息: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
        
        print("-" * 40)
    
    print("\n🔍 分析结果:")
    print("如果所有测试返回相同的 bot_move、score、last_move_color，")
    print("那么确认是服务器端的缓存或状态管理问题！")

if __name__ == "__main__":
    test_katago_api()