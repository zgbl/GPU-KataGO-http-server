#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KataGo Container 诊断工具
用于测试和诊断KataGo HTTP服务器的连接和功能状态

使用方法:
    python container_diagnostic.py [--host HOST] [--port PORT] [--timeout TIMEOUT]

示例:
    # 测试本地服务器
    python container_diagnostic.py
    
    # 测试远程服务器
    python container_diagnostic.py --host 192.168.1.100 --port 8080
    
    # 设置超时时间
    python container_diagnostic.py --timeout 60
"""

import argparse
import requests
import json
import time
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class KataGoContainerDiagnostic:
    """KataGo Container 诊断工具"""
    
    def __init__(self, host: str = "localhost", port: int = 8080, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.timeout = timeout
        
        # 测试结果
        self.results = {
            'connection': False,
            'health': False,
            'info': False,
            'select_move': False,
            'score': False,
            'analyze': False,
            'errors': []
        }
        
        print(f"🔍 KataGo Container 诊断工具")
        print(f"📡 目标服务器: {self.base_url}")
        print(f"⏱️  超时时间: {timeout}秒")
        print("=" * 60)
    
    def test_basic_connection(self) -> bool:
        """测试基本连接"""
        print("\n1️⃣ 测试基本连接...")
        
        try:
            response = self.session.get(self.base_url, timeout=5)
            print(f"   ✅ 连接成功 (状态码: {response.status_code})")
            self.results['connection'] = True
            return True
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接被拒绝 - 服务器可能未启动")
            self.results['errors'].append("连接被拒绝")
            return False
        except requests.exceptions.Timeout:
            print(f"   ❌ 连接超时")
            self.results['errors'].append("连接超时")
            return False
        except Exception as e:
            print(f"   ❌ 连接错误: {e}")
            self.results['errors'].append(f"连接错误: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        print("\n2️⃣ 测试健康检查端点 (/health)...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 健康检查通过")
                print(f"   📊 状态: {data.get('status', 'unknown')}")
                print(f"   🏷️  版本: {data.get('version', 'unknown')}")
                if 'engine_running' in data:
                    print(f"   🔧 引擎状态: {'运行中' if data['engine_running'] else '未运行'}")
                self.results['health'] = True
                return True
            else:
                print(f"   ❌ 健康检查失败 (状态码: {response.status_code})")
                self.results['errors'].append(f"健康检查失败: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 健康检查请求失败: {e}")
            self.results['errors'].append(f"健康检查请求失败: {e}")
            return False
        except json.JSONDecodeError:
            print(f"   ❌ 健康检查响应格式错误")
            self.results['errors'].append("健康检查响应格式错误")
            return False
    
    def test_info_endpoint(self) -> bool:
        """测试信息端点"""
        print("\n3️⃣ 测试信息端点 (/info)...")
        
        try:
            response = self.session.get(f"{self.base_url}/info")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 信息端点正常")
                print(f"   🏷️  服务器: {data.get('server', 'unknown')}")
                print(f"   📦 版本: {data.get('version', 'unknown')}")
                
                if 'endpoints' in data:
                    print(f"   🔗 可用端点: {', '.join(data['endpoints'])}")
                
                self.results['info'] = True
                return True
            else:
                print(f"   ⚠️  信息端点不可用 (状态码: {response.status_code})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  信息端点请求失败: {e}")
            return False
        except json.JSONDecodeError:
            print(f"   ⚠️  信息端点响应格式错误")
            return False
    
    def test_select_move_endpoint(self) -> bool:
        """测试走法选择端点"""
        print("\n4️⃣ 测试走法选择端点 (/select-move/katago_gtp_bot)...")
        
        test_data = {
            "board_size": 19,
            "moves": ["R4", "D16"],
            "config": {
                "komi": 7.5,
                "max_visits": 100,  # 使用较小的访问数以加快测试
                "request_id": f"diagnostic_{int(time.time())}"
            }
        }
        
        try:
            print(f"   📤 发送测试请求...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/select-move/katago_gtp_bot",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 走法选择成功 (耗时: {duration:.2f}秒)")
                
                if 'bot_move' in data:
                    print(f"   🎯 推荐走法: {data['bot_move']}")
                
                if 'winrate' in data:
                    winrate = data['winrate']
                    print(f"   📊 胜率: {winrate:.3f} ({winrate*100:.1f}%)")
                
                if 'visits' in data:
                    print(f"   🔍 访问次数: {data['visits']}")
                
                self.results['select_move'] = True
                return True
            else:
                print(f"   ❌ 走法选择失败 (状态码: {response.status_code})")
                print(f"   📝 错误信息: {response.text[:200]}...")
                self.results['errors'].append(f"走法选择失败: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ❌ 走法选择超时 (>{self.timeout}秒)")
            self.results['errors'].append("走法选择超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 走法选择请求失败: {e}")
            self.results['errors'].append(f"走法选择请求失败: {e}")
            return False
        except json.JSONDecodeError:
            print(f"   ❌ 走法选择响应格式错误")
            self.results['errors'].append("走法选择响应格式错误")
            return False
    
    def test_score_endpoint(self) -> bool:
        """测试局面评估端点"""
        print("\n5️⃣ 测试局面评估端点 (/score/katago_gtp_bot)...")
        
        test_data = {
            "board_size": 19,
            "moves": ["R4", "D16", "Q16"],
            "config": {
                "komi": 7.5,
                "max_visits": 100,
                "request_id": f"score_diagnostic_{int(time.time())}"
            }
        }
        
        try:
            print(f"   📤 发送评估请求...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/score/katago_gtp_bot",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 局面评估成功 (耗时: {duration:.2f}秒)")
                
                if 'probs' in data:
                    probs = data['probs']
                    if isinstance(probs, list) and len(probs) > 0:
                        print(f"   📊 领域信息: {len(probs)}x{len(probs[0]) if probs[0] else 0} 矩阵")
                
                self.results['score'] = True
                return True
            else:
                print(f"   ⚠️  局面评估失败 (状态码: {response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️  局面评估超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  局面评估请求失败: {e}")
            return False
        except json.JSONDecodeError:
            print(f"   ⚠️  局面评估响应格式错误")
            return False
    
    def test_analyze_endpoint(self) -> bool:
        """测试原生分析端点"""
        print("\n6️⃣ 测试原生分析端点 (/analyze)...")
        
        test_data = {
            "id": f"diagnostic_{int(time.time())}",
            "moves": [["B", "R4"], ["W", "D16"]],
            "rules": "tromp-taylor",
            "komi": 7.5,
            "boardXSize": 19,
            "boardYSize": 19,
            "analyzeTurns": [2],
            "maxVisits": 100,
            "includeOwnership": True,
            "includePVVisits": True
        }
        
        try:
            print(f"   📤 发送分析请求...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/analyze",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 原生分析成功 (耗时: {duration:.2f}秒)")
                
                if 'turnInfos' in data:
                    turn_infos = data['turnInfos']
                    print(f"   📊 分析回合数: {len(turn_infos)}")
                
                self.results['analyze'] = True
                return True
            else:
                print(f"   ⚠️  原生分析不可用 (状态码: {response.status_code})")
                return False
                
        except requests.exceptions.Timeout:
            print(f"   ⚠️  原生分析超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  原生分析请求失败: {e}")
            return False
        except json.JSONDecodeError:
            print(f"   ⚠️  原生分析响应格式错误")
            return False
    
    def generate_report(self) -> None:
        """生成诊断报告"""
        print("\n" + "=" * 60)
        print("📋 诊断报告")
        print("=" * 60)
        
        # 统计成功的测试
        successful_tests = sum(1 for result in self.results.values() if isinstance(result, bool) and result)
        total_tests = len([k for k, v in self.results.items() if isinstance(v, bool)])
        
        print(f"\n📊 测试结果: {successful_tests}/{total_tests} 通过")
        
        # 详细结果
        test_names = {
            'connection': '基本连接',
            'health': '健康检查',
            'info': '信息端点',
            'select_move': '走法选择',
            'score': '局面评估',
            'analyze': '原生分析'
        }
        
        print("\n🔍 详细结果:")
        for key, name in test_names.items():
            status = "✅ 通过" if self.results[key] else "❌ 失败"
            print(f"   {name}: {status}")
        
        # 错误信息
        if self.results['errors']:
            print("\n⚠️  发现的问题:")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"   {i}. {error}")
        
        # 建议
        print("\n💡 诊断建议:")
        
        if not self.results['connection']:
            print("   🔧 连接问题:")
            print("      - 检查KataGo容器是否正在运行")
            print("      - 确认端口映射是否正确 (8080)")
            print("      - 检查防火墙设置")
            print("      - 尝试: docker ps | grep katago")
        
        elif not self.results['health']:
            print("   🔧 健康检查问题:")
            print("      - KataGo服务可能未完全启动")
            print("      - 检查容器日志: docker logs <container_name>")
            print("      - 等待几分钟后重试")
        
        elif not self.results['select_move']:
            print("   🔧 功能问题:")
            print("      - KataGo引擎可能未正确配置")
            print("      - 检查模型文件是否存在")
            print("      - 检查GPU/CPU资源是否充足")
            print("      - 查看服务器日志获取详细错误信息")
        
        else:
            print("   🎉 服务器运行正常!")
            print("      - 所有核心功能都可用")
            print("      - 可以正常使用KataGo分析服务")
        
        # 服务器信息
        print(f"\n📡 服务器信息:")
        print(f"   地址: {self.base_url}")
        print(f"   测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   超时设置: {self.timeout}秒")
    
    def run_full_diagnostic(self) -> bool:
        """运行完整诊断"""
        print("🚀 开始完整诊断...\n")
        
        # 按顺序执行测试
        tests = [
            self.test_basic_connection,
            self.test_health_endpoint,
            self.test_info_endpoint,
            self.test_select_move_endpoint,
            self.test_score_endpoint,
            self.test_analyze_endpoint
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # 短暂延迟
            except KeyboardInterrupt:
                print("\n⏹️  诊断被用户中断")
                break
            except Exception as e:
                print(f"\n❌ 测试执行错误: {e}")
                self.results['errors'].append(f"测试执行错误: {e}")
        
        # 生成报告
        self.generate_report()
        
        # 返回是否至少基本功能可用
        return self.results['connection'] and self.results['health'] and self.results['select_move']


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="KataGo Container 诊断工具")
    parser.add_argument('--host', default='localhost', help='服务器主机地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (默认: 8080)')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间 (默认: 30秒)')
    parser.add_argument('--quick', action='store_true', help='快速测试模式 (仅测试基本功能)')
    
    args = parser.parse_args()
    
    try:
        diagnostic = KataGoContainerDiagnostic(args.host, args.port, args.timeout)
        
        if args.quick:
            # 快速模式：仅测试连接和健康检查
            print("⚡ 快速测试模式")
            success = (diagnostic.test_basic_connection() and 
                      diagnostic.test_health_endpoint() and 
                      diagnostic.test_select_move_endpoint())
            diagnostic.generate_report()
        else:
            # 完整诊断
            success = diagnostic.run_full_diagnostic()
        
        # 退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n👋 诊断被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 诊断工具执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()