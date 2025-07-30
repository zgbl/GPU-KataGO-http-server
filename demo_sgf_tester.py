#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SGF HTTP 测试工具演示脚本
自动演示SGF分析功能
"""

import sys
import time
from sgf_http_tester import SGFHTTPTester

def demo_sgf_analysis():
    """演示SGF分析功能"""
    print("🎮 KataGo HTTP Server SGF 测试工具演示")
    print("="*60)
    
    # 创建测试器
    tester = SGFHTTPTester("http://localhost:8080")
    
    # 设置较短的分析间隔用于演示
    tester.analysis_interval = 3
    
    # 测试服务器连接
    print("\n📡 测试服务器连接...")
    if not tester.test_server_connection():
        print("❌ 服务器连接失败，请确保 katago-integrated-server 正在运行")
        return False
    
    # 获取服务器信息
    server_info = tester.get_server_info()
    if server_info:
        print(f"✅ 服务器信息获取成功")
    
    # 使用一个简单的示例SGF
    demo_sgf = """(;FF[4]CA[UTF-8]GM[1]DT[2024-01-01]
SZ[19]KM[7.5]PW[White]PB[Black]
;B[pd];W[dd];B[pq];W[dp];B[fq];W[cn];B[jp];W[qf]
;B[nd];W[rd];B[qc];W[qi])"""
    
    print("\n🎯 使用演示SGF进行分析")
    print("SGF内容:")
    print(demo_sgf)
    
    # 解析SGF
    moves = tester.parse_sgf_moves(demo_sgf)
    
    if not moves:
        print("❌ SGF解析失败")
        return False
    
    print(f"\n✅ 解析到 {len(moves)} 手棋:")
    for i, (color, pos) in enumerate(moves):
        print(f"  第{i+1}手: {color} {pos}")
    
    # 分析前5手
    print("\n🧠 开始分析前5手棋...")
    print(f"分析间隔: {tester.analysis_interval}秒")
    
    try:
        tester.step_by_step_analysis(moves, 1, min(5, len(moves)))
        print("\n🎉 演示完成!")
        return True
    except KeyboardInterrupt:
        print("\n⚠️ 演示被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        return False

def quick_test():
    """快速测试功能"""
    print("🚀 快速功能测试")
    print("="*40)
    
    tester = SGFHTTPTester("http://localhost:8080")
    
    # 测试连接
    if tester.test_server_connection():
        print("✅ 服务器连接正常")
    else:
        print("❌ 服务器连接失败")
        return False
    
    # 测试简单分析
    simple_sgf = "(;FF[4]GM[1]SZ[19];B[pd];W[dd];B[pq])"
    moves = tester.parse_sgf_moves(simple_sgf)
    
    if moves:
        print(f"✅ SGF解析正常，解析到 {len(moves)} 手棋")
        
        # 分析第一手
        result = tester.analyze_position(moves, 1)
        if result:
            print("✅ 局面分析正常")
            bot_move = result.get('bot_move', 'N/A')
            print(f"推荐走法: {bot_move}")
        else:
            print("❌ 局面分析失败")
            return False
    else:
        print("❌ SGF解析失败")
        return False
    
    print("\n🎉 快速测试完成!")
    return True

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 快速测试模式
        success = quick_test()
    else:
        # 完整演示模式
        print("提示: 使用 --quick 参数进行快速测试")
        print("正在进行完整演示...\n")
        success = demo_sgf_analysis()
    
    if success:
        print("\n✅ 测试成功完成!")
        print("\n📖 使用说明:")
        print("1. 运行 'python sgf_http_tester.py' 进入交互模式")
        print("2. 选择选项1输入自己的SGF内容")
        print("3. 选择选项2使用内置示例SGF")
        print("4. 选择选项3调整分析间隔时间")
        print("5. 工具会逐步分析每一手棋，每隔设定时间显示一次结果")
    else:
        print("\n❌ 测试失败")
        print("请检查:")
        print("1. katago-integrated-server 是否正在运行")
        print("2. 服务器地址是否正确 (默认: http://localhost:8080)")
        print("3. 网络连接是否正常")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())