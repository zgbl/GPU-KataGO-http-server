#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo 整合版 HTTP Server 客户端示例
演示如何使用 HTTP API 进行围棋分析
"""

import requests
import json
import time
from typing import List, Dict, Optional

class KataGoClient:
    """KataGo HTTP API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KataGo-Client/1.0'
        })
    
    def health_check(self) -> Dict:
        """检查服务器健康状态"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_server_info(self) -> Dict:
        """获取服务器信息"""
        response = self.session.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()
    
    def select_move(self, 
                   moves: List[str], 
                   board_size: int = 19,
                   config: Optional[Dict] = None) -> Dict:
        """获取最佳走法
        
        Args:
            moves: 已下棋子的列表，如 ["R4", "D16"]
            board_size: 棋盘大小，默认19
            config: 额外配置参数
            
        Returns:
            包含推荐走法和诊断信息的字典
        """
        if config is None:
            config = {}
            
        payload = {
            "board_size": board_size,
            "moves": moves,
            "config": config
        }
        
        response = self.session.post(
            f"{self.base_url}/select-move/katago_gtp_bot",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def score_position(self, 
                      moves: List[str], 
                      board_size: int = 19,
                      config: Optional[Dict] = None) -> Dict:
        """评估局面
        
        Args:
            moves: 已下棋子的列表
            board_size: 棋盘大小，默认19
            config: 额外配置参数
            
        Returns:
            包含局面评估和诊断信息的字典
        """
        if config is None:
            config = {}
            
        payload = {
            "board_size": board_size,
            "moves": moves,
            "config": config
        }
        
        response = self.session.post(
            f"{self.base_url}/score/katago_gtp_bot",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

def format_move_sequence(moves: List[str]) -> str:
    """格式化走法序列显示"""
    if not moves:
        return "空棋盘"
    
    formatted = []
    for i, move in enumerate(moves):
        color = "黑" if i % 2 == 0 else "白"
        formatted.append(f"{color}{move}")
    
    return " → ".join(formatted)

def print_analysis_result(result: Dict, moves: List[str]):
    """打印分析结果"""
    print(f"\n📋 局面: {format_move_sequence(moves)}")
    
    if 'bot_move' in result:
        print(f"🎯 推荐走法: {result['bot_move']}")
    
    if 'probs' in result:
        probs = result['probs']
        print(f"📊 评估数据点: {len(probs)}")
    
    diagnostics = result.get('diagnostics', {})
    if diagnostics:
        win_prob = diagnostics.get('win_prob')
        score = diagnostics.get('score')
        
        if win_prob is not None:
            win_percent = win_prob * 100 if isinstance(win_prob, float) else win_prob
            print(f"📈 胜率: {win_percent:.1f}%")
        
        if score is not None:
            print(f"📊 得分: {score:.1f}")
    
    timestamp = result.get('timestamp')
    if timestamp:
        print(f"⏰ 时间: {timestamp}")

def demo_basic_usage():
    """基本使用演示"""
    print("🎮 KataGo 整合版 HTTP Server 客户端演示")
    print("=" * 50)
    
    # 创建客户端
    client = KataGoClient()
    
    try:
        # 1. 健康检查
        print("\n1️⃣ 健康检查...")
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"📅 版本: {health.get('version', 'N/A')}")
        
        # 2. 服务器信息
        print("\n2️⃣ 获取服务器信息...")
        info = client.get_server_info()
        print(f"🏷️  服务名称: {info['name']}")
        print(f"📦 版本: {info['version']}")
        print(f"🧠 模型文件: {info['model_file']}")
        
        # 3. 空棋盘走法
        print("\n3️⃣ 空棋盘最佳开局...")
        start_time = time.time()
        result = client.select_move([], config={"request_id": "demo_empty"})
        elapsed = time.time() - start_time
        print(f"⏱️  耗时: {elapsed:.2f}秒")
        print_analysis_result(result, [])
        
        # 4. 有棋子的局面
        print("\n4️⃣ 分析开局局面...")
        moves = ["R4", "D16", "Q16"]
        start_time = time.time()
        result = client.select_move(moves, config={"request_id": "demo_opening"})
        elapsed = time.time() - start_time
        print(f"⏱️  耗时: {elapsed:.2f}秒")
        print_analysis_result(result, moves)
        
        # 5. 局面评估
        print("\n5️⃣ 局面评估...")
        moves = ["R4", "D16", "Q16", "D4"]
        start_time = time.time()
        result = client.score_position(moves, config={"request_id": "demo_score"})
        elapsed = time.time() - start_time
        print(f"⏱️  耗时: {elapsed:.2f}秒")
        print_analysis_result(result, moves)
        
        print("\n🎉 演示完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保 KataGo HTTP 服务器正在运行")
        print("💡 启动命令: ./build_and_run.ps1 run")
    except requests.exceptions.Timeout:
        print("⏰ 请求超时: KataGo 可能正在处理复杂计算")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def demo_game_analysis():
    """对局分析演示"""
    print("\n🏁 对局分析演示")
    print("=" * 30)
    
    # 模拟一个简单的对局开始
    game_moves = [
        "R4",   # 黑1: 右下小目
        "D16",  # 白2: 左上星位
        "Q16",  # 黑3: 右上星位
        "D4",   # 白4: 左下星位
        "C3",   # 黑5: 左下小目
        "R16",  # 白6: 右上小目
    ]
    
    client = KataGoClient()
    
    print("📝 分析每一步的局面...")
    
    for i in range(0, len(game_moves) + 1, 2):  # 每两步分析一次
        current_moves = game_moves[:i]
        move_num = i + 1
        
        try:
            print(f"\n--- 第 {move_num} 手后 ---")
            result = client.select_move(
                current_moves, 
                config={"request_id": f"game_analysis_{move_num}"}
            )
            print_analysis_result(result, current_moves)
            
            # 短暂延迟避免请求过于频繁
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ 分析第 {move_num} 手时出错: {e}")
            break

def interactive_mode():
    """交互模式"""
    print("\n🎮 交互模式")
    print("输入走法序列，用空格分隔，如: R4 D16 Q16")
    print("输入 'quit' 退出")
    print("=" * 40)
    
    client = KataGoClient()
    
    while True:
        try:
            user_input = input("\n请输入走法序列: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not user_input:
                moves = []
            else:
                moves = user_input.split()
            
            print("🔄 分析中...")
            result = client.select_move(moves, config={"request_id": "interactive"})
            print_analysis_result(result, moves)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KataGo 整合版 HTTP Server 客户端演示')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='服务器URL (默认: http://localhost:8080)')
    parser.add_argument('--mode', choices=['demo', 'game', 'interactive'], 
                       default='demo', help='运行模式')
    
    args = parser.parse_args()
    
    # 更新客户端URL
    global client
    
    if args.mode == 'demo':
        demo_basic_usage()
    elif args.mode == 'game':
        demo_game_analysis()
    elif args.mode == 'interactive':
        interactive_mode()

if __name__ == '__main__':
    main()