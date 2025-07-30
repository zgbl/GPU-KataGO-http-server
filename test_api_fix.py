#!/usr/bin/env python3
"""
测试API修复 - 模拟KataGo响应来验证moves格式转换是否正确
"""

import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

# 创建模拟KataGo服务器
app = Flask(__name__)
CORS(app)

@app.route('/select-move/katago_gtp_bot', methods=['POST'])
def mock_select_move():
    """模拟KataGo的select_move API"""
    try:
        content = request.get_json()
        board_size = content.get('board_size', 19)
        moves = content.get('moves', [])
        config = content.get('config', {})
        
        print(f"\n=== 模拟KataGo API接收到的数据 ===")
        print(f"board_size: {board_size}")
        print(f"moves: {moves}")
        print(f"moves类型: {type(moves)}")
        if moves:
            print(f"第一个move: {moves[0]}, 类型: {type(moves[0])}")
        print(f"config: {config}")
        
        # 验证moves格式
        if moves and isinstance(moves[0], list):
            print("❌ 错误：接收到的moves仍然是二维列表格式！")
            print(f"   示例: {moves[0]}")
        elif moves and isinstance(moves[0], str):
            print("✅ 正确：接收到的moves是字符串列表格式！")
            print(f"   示例: {moves[0]}")
        else:
            print("ℹ️  空moves列表")
        
        # 根据moves数量返回不同的响应，模拟真实的KataGo行为
        move_count = len(moves)
        if move_count == 0:
            bot_move = "D4"
            score = 0.0
            win_prob = 0.5
        elif move_count == 1:
            bot_move = "Q16"
            score = -0.2
            win_prob = 0.48
        elif move_count == 2:
            bot_move = "D16"
            score = 0.1
            win_prob = 0.52
        else:
            bot_move = "Q4"
            score = -0.1 * move_count
            win_prob = 0.5 - 0.01 * move_count
        
        response = {
            'bot_move': bot_move,
            'diagnostics': {
                'score': score,
                'win_prob': win_prob,
                'last_move_color': 'b' if move_count % 2 == 0 else 'w',
                'best_ten': [
                    {'move': bot_move, 'score': score, 'visits': 1000}
                ]
            },
            'request_id': config.get('request_id', ''),
            'timestamp': '2025-01-30 17:30:00'
        }
        
        print(f"\n=== 模拟KataGo响应 ===")
        print(f"推荐走法: {bot_move}")
        print(f"分数: {score}")
        print(f"胜率: {win_prob}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ 模拟API错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': '模拟KataGo服务器运行正常'})

def start_mock_server():
    """启动模拟服务器"""
    print("🚀 启动模拟KataGo服务器在端口8081...")
    app.run(host='0.0.0.0', port=8081, debug=False)

def test_api_fix():
    """测试API修复"""
    print("\n🧪 测试API修复 - moves格式转换")
    print("=" * 60)
    
    # 等待服务器启动
    time.sleep(2)
    
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
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {test_case['name']}")
        print(f"发送moves: {test_case['moves']}")
        
        try:
            response = requests.post(
                'http://localhost:8081/select-move/katago_gtp_bot',
                json={
                    'board_size': 19,
                    'moves': test_case['moves'],
                    'config': {'request_id': f'test_{i}'}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 推荐走法: {data['bot_move']}")
                print(f"   分数: {data['diagnostics']['score']}")
                print(f"   胜率: {data['diagnostics']['win_prob']}")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        print("-" * 40)
    
    print("\n🎯 测试完成！")
    print("如果看到'✅ 正确：接收到的moves是字符串列表格式！'，说明修复成功！")

if __name__ == '__main__':
    # 在后台启动模拟服务器
    server_thread = threading.Thread(target=start_mock_server, daemon=True)
    server_thread.start()
    
    # 运行测试
    test_api_fix()