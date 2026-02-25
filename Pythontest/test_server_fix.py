#!/usr/bin/env python3
"""
测试服务器修复 - 直接测试moves格式转换逻辑
"""

def test_moves_conversion():
    """直接测试moves格式转换逻辑"""
    print("\n🧪 测试moves格式转换逻辑")
    print("=" * 50)
    
    test_cases = [
        {
            'name': '空局面',
            'moves': []
        },
        {
            'name': '第1手 - 黑R16',
            'moves': [['B', 'R16']]
        },
        {
            'name': '第2手 - 白C4',
            'moves': [['B', 'R16'], ['W', 'C4']]
        },
        {
            'name': '第3手 - 黑Q3',
            'moves': [['B', 'R16'], ['W', 'C4'], ['B', 'Q3']]
        },
        {
            'name': '已经是字符串格式',
            'moves': ['R16', 'C4', 'Q3']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {test_case['name']}")
        moves = test_case['moves']
        print(f"原始moves: {moves}")
        print(f"moves类型: {type(moves)}")
        if moves:
            print(f"第一个元素: {moves[0]}, 类型: {type(moves[0])}")
        
        # 应用转换逻辑（从katago_integrated_server.py复制）
        if moves and isinstance(moves[0], list) and len(moves[0]) == 2:
            # 如果moves是包含颜色信息的格式，提取位置信息
            position_moves = [move[1] for move in moves]
            print(f"✅ 转换后: {position_moves} (从二维列表转换为字符串列表)")
            
            # 验证转换结果
            if all(isinstance(move, str) for move in position_moves):
                print("✅ 转换成功：所有元素都是字符串")
            else:
                print("❌ 转换失败：仍有非字符串元素")
                
        else:
            # 如果moves已经是位置字符串列表，直接使用
            position_moves = moves
            if not moves:
                print("ℹ️  空列表，无需转换")
            elif isinstance(moves[0], str):
                print(f"ℹ️  已是字符串列表: {position_moves}")
            else:
                print(f"⚠️  未知格式: {position_moves}")
        
        print("-" * 40)
    
    print("\n🎯 转换逻辑测试完成！")
    print("\n现在测试实际的API调用...")
    
    # 测试实际API调用
    test_api_calls()

def test_api_calls():
    """测试实际的API调用"""
    import requests
    import json
    
    print("\n🌐 测试实际API调用")
    print("=" * 50)
    
    # 首先检查服务器是否运行
    try:
        health_response = requests.get('http://localhost:8080/health', timeout=2)
        if health_response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"⚠️  服务器响应异常: {health_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请先启动katago_integrated_server.py")
        return
    
    test_cases = [
        {
            'name': '空局面',
            'moves': []
        },
        {
            'name': '第1手 - 黑R16',
            'moves': [['B', 'R16']]
        },
        {
            'name': '第2手 - 白C4',
            'moves': [['B', 'R16'], ['W', 'C4']]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[API测试 {i}] {test_case['name']}")
        print(f"发送moves: {test_case['moves']}")
        
        try:
            response = requests.post(
                'http://localhost:8080/select-move/katago_gtp_bot',
                json={
                    'board_size': 19,
                    'moves': test_case['moves'],
                    'config': {'request_id': f'test_{i}'}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API调用成功")
                print(f"   推荐走法: {data.get('bot_move')}")
                if 'diagnostics' in data:
                    diag = data['diagnostics']
                    print(f"   分数: {diag.get('score')}")
                    print(f"   胜率: {diag.get('win_prob')}")
                    print(f"   best_ten数量: {len(diag.get('best_ten', []))}")
            else:
                print(f"❌ API调用失败 - 状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ API请求失败: {e}")
        
        print("-" * 40)

if __name__ == '__main__':
    test_moves_conversion()