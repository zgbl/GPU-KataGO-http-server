#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo 整合版 HTTP Server 测试脚本
测试HTTP API的各种功能
"""

import requests
import json
import time
import sys
from datetime import datetime

class KataGoHTTPTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KataGo-Integrated-Tester/1.0'
        })
    
    def print_status(self, message, status="INFO"):
        """打印带状态的消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        status_symbols = {
            'INFO': '🔵',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️'
        }
        symbol = status_symbols.get(status, '🔵')
        print(f"[{timestamp}] {symbol} {message}")
    
    def test_health_check(self):
        """测试健康检查端点"""
        self.print_status("测试健康检查端点...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_status(f"健康检查通过: {data.get('status')}", "SUCCESS")
                return True
            else:
                self.print_status(f"健康检查失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"健康检查异常: {str(e)}", "ERROR")
            return False
    
    def test_server_info(self):
        """测试服务器信息端点"""
        self.print_status("测试服务器信息端点...")
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_status(f"服务器信息: {data.get('name')} v{data.get('version')}", "SUCCESS")
                self.print_status(f"模型文件: {data.get('model_file')}")
                self.print_status(f"可用端点: {', '.join(data.get('endpoints', []))}")
                return True
            else:
                self.print_status(f"获取服务器信息失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"获取服务器信息异常: {str(e)}", "ERROR")
            return False
    
    def test_select_move_empty_board(self):
        """测试空棋盘的走法选择"""
        self.print_status("测试空棋盘走法选择...")
        try:
            payload = {
                "board_size": 19,
                "moves": [],
                "config": {
                    "request_id": "test_empty_board"
                }
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/select-move/katago_gtp_bot",
                json=payload,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                bot_move = data.get('bot_move')
                diagnostics = data.get('diagnostics', {})
                
                self.print_status(f"空棋盘推荐走法: {bot_move} (耗时: {elapsed_time:.2f}s)", "SUCCESS")
                if diagnostics:
                    win_rate = diagnostics.get('win_prob', 'N/A')
                    self.print_status(f"胜率: {win_rate}")
                return True
            else:
                self.print_status(f"空棋盘走法选择失败: HTTP {response.status_code}", "ERROR")
                self.print_status(f"响应: {response.text}")
                return False
                
        except Exception as e:
            self.print_status(f"空棋盘走法选择异常: {str(e)}", "ERROR")
            return False
    
    def test_select_move_with_moves(self):
        """测试有棋子的局面走法选择"""
        self.print_status("测试有棋子局面的走法选择...")
        try:
            # 测试一个简单的开局
            payload = {
                "board_size": 19,
                "moves": ["R4", "D16", "Q16"],
                "config": {
                    "request_id": "test_with_moves"
                }
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/select-move/katago_gtp_bot",
                json=payload,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                bot_move = data.get('bot_move')
                diagnostics = data.get('diagnostics', {})
                
                self.print_status(f"局面走法: {bot_move} (耗时: {elapsed_time:.2f}s)", "SUCCESS")
                if diagnostics:
                    win_rate = diagnostics.get('win_prob', 'N/A')
                    self.print_status(f"胜率: {win_rate}")
                return True
            else:
                self.print_status(f"局面走法选择失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"局面走法选择异常: {str(e)}", "ERROR")
            return False
    
    def test_score_evaluation(self):
        """测试局面评估"""
        self.print_status("测试局面评估...")
        try:
            payload = {
                "board_size": 19,
                "moves": ["R4", "D16", "Q16", "D4"],
                "config": {
                    "request_id": "test_score"
                }
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/score/katago_gtp_bot",
                json=payload,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                probs = data.get('probs', [])
                diagnostics = data.get('diagnostics', {})
                
                self.print_status(f"局面评估完成 (耗时: {elapsed_time:.2f}s)", "SUCCESS")
                self.print_status(f"评估数据点数: {len(probs)}")
                if diagnostics:
                    win_rate = diagnostics.get('win_prob', 'N/A')
                    score = diagnostics.get('score', 'N/A')
                    self.print_status(f"胜率: {win_rate}, 得分: {score}")
                return True
            else:
                self.print_status(f"局面评估失败: HTTP {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"局面评估异常: {str(e)}", "ERROR")
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        self.print_status("测试错误处理...")
        
        # 测试无效请求体
        try:
            response = self.session.post(
                f"{self.base_url}/select-move/katago_gtp_bot",
                json={},
                timeout=10
            )
            if response.status_code == 400 or response.status_code == 500:
                self.print_status("无效请求正确返回错误状态", "SUCCESS")
            else:
                self.print_status(f"无效请求未返回预期错误: HTTP {response.status_code}", "WARNING")
        except Exception as e:
            self.print_status(f"错误处理测试异常: {str(e)}", "WARNING")
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        self.print_status("开始 KataGo 整合版 HTTP Server 测试")
        self.print_status(f"测试目标: {self.base_url}")
        self.print_status("=" * 50)
        
        tests = [
            ("健康检查", self.test_health_check),
            ("服务器信息", self.test_server_info),
            ("空棋盘走法", self.test_select_move_empty_board),
            ("局面走法", self.test_select_move_with_moves),
            ("局面评估", self.test_score_evaluation),
            ("错误处理", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.print_status(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed += 1
                time.sleep(1)  # 避免请求过于频繁
            except KeyboardInterrupt:
                self.print_status("测试被用户中断", "WARNING")
                break
            except Exception as e:
                self.print_status(f"{test_name} 测试出现未预期错误: {str(e)}", "ERROR")
        
        self.print_status("\n" + "=" * 50)
        self.print_status(f"测试完成: {passed}/{total} 通过")
        
        if passed == total:
            self.print_status("🎉 所有测试通过！", "SUCCESS")
            return True
        else:
            self.print_status(f"⚠️  {total - passed} 个测试失败", "WARNING")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='KataGo 整合版 HTTP Server 测试工具')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='服务器URL (默认: http://localhost:8080)')
    parser.add_argument('--test', choices=['health', 'info', 'move', 'score', 'all'],
                       default='all', help='要运行的测试类型')
    
    args = parser.parse_args()
    
    tester = KataGoHTTPTester(args.url)
    
    if args.test == 'health':
        success = tester.test_health_check()
    elif args.test == 'info':
        success = tester.test_server_info()
    elif args.test == 'move':
        success = tester.test_select_move_empty_board()
    elif args.test == 'score':
        success = tester.test_score_evaluation()
    else:
        success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()