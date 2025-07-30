#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试用户提供的SGF棋谱分析工具
验证胜率、分差等信息的正确显示
"""

import sys
import time
from sgf_http_tester import SGFHTTPTester

def test_user_sgf():
    """测试用户提供的SGF棋谱"""
    print("🎯 测试用户提供的SGF棋谱分析")
    print("=" * 50)
    
    # 用户提供的SGF内容
    user_sgf = """(;FF[4]
CA[UTF-8]
GM[1]
DT[2024-06-25]
PC[OGS: `https://online-go.com/game/65465972]`
GN[Friendly Match]
PB[minshan]
PW[AlexanderQi]
BR[?]
WR[?]
TM[3600]OT[25/600 canadian]
RE[W+R]
SZ[19]
KM[7.5]
RU[AGA]
;B[qd]
(;W[cp]
(;B[pq]
(;W[dc]
(;B[eq]
(;W[oc]
(;B[dn]
(;W[pe]
(;B[qe]
(;W[pf]
(;B[rg]
(;W[ep]
(;B[dp]
(;W[do]
(;B[dq]
(;W[co]
(;B[eo]
(;W[fp]
(;B[cq]
(;W[cn]
(;B[fo]
(;W[fq]
(;B[fr]
(;W[gr]
(;B[er]
(;W[dm]
(;B[go]
(;W[pp]
(;B[op]
(;W[qq]
(;B[po]
(;W[qp]
(;B[oq]
(;W[rn]
(;B[qm]
(;W[qn]
(;B[pm]
(;W[pn]
(;B[on]
(;W[om]
(;B[rm]
(;W[ol]
(;B[pk]
(;W[ok]
(;B[pj]
(;W[oj]
(;B[pi]
(;W[qr]
(;B[nn]
(;W[oi]
(;B[oh]
(;W[pl]
(;B[qk]
(;W[nh]
(;B[og]
(;W[qg]
(;B[ng]
(;W[rh]
(;B[rf]
(;W[qh]
(;B[ph]
(;W[ne]
(;B[mh]
(;W[lk]
(;B[pb]
(;W[kq]
(;B[ko]
(;W[hp]
(;B[gp]
(;W[gq]
(;B[hq]"""
    
    try:
        # 创建测试器
        tester = SGFHTTPTester()
        
        # 测试服务器连接
        print("\n1️⃣ 测试服务器连接...")
        if not tester.test_connection():
            print("❌ 服务器连接失败，请确保KataGo服务器正在运行")
            return False
        
        # 解析SGF
        print("\n2️⃣ 解析SGF棋谱...")
        moves = tester.parse_sgf_moves(user_sgf)
        if not moves:
            print("❌ SGF解析失败")
            return False
        
        print(f"✅ 成功解析出 {len(moves)} 手棋")
        print(f"前10手: {moves[:10]}")
        
        # 测试前几手的分析
        print("\n3️⃣ 测试前5手的分析结果...")
        current_moves = []
        
        for i in range(min(5, len(moves))):
            current_moves.append(moves[i])
            move_num = i + 1
            
            print(f"\n--- 分析第 {move_num} 手: {moves[i]} ---")
            
            try:
                # 使用详细配置
                config = {
                    "request_id": f"test_user_sgf_{move_num}",
                    "max_visits": 1000,
                    "analyze_after_move": True
                }
                
                start_time = time.time()
                result = tester.select_move(current_moves, config=config)
                elapsed_time = time.time() - start_time
                
                # 显示详细分析结果
                analysis = tester.format_analysis_result(result, move_num, moves[i])
                print(analysis)
                print(f"⏱️ 分析耗时: {elapsed_time:.2f}秒")
                
                # 显示原始API响应（用于调试）
                print("\n🔍 API响应详情:")
                diagnostics = result.get('diagnostics', {})
                print(f"  - bot_move: {result.get('bot_move')}")
                print(f"  - winprob: {diagnostics.get('winprob')}")
                print(f"  - score: {diagnostics.get('score')}")
                print(f"  - best_ten: {len(diagnostics.get('best_ten', []))} 项")
                
                time.sleep(2)  # 避免请求过于频繁
                
            except Exception as e:
                print(f"❌ 分析第 {move_num} 手时出错: {e}")
                continue
        
        print("\n🎉 用户SGF测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def quick_api_test():
    """快速API测试"""
    print("\n🚀 快速API测试")
    print("=" * 30)
    
    try:
        tester = SGFHTTPTester()
        
        # 测试简单局面
        test_moves = ["R4", "D16", "Q16"]
        print(f"测试走法: {test_moves}")
        
        config = {
            "request_id": "quick_test",
            "max_visits": 500
        }
        
        result = tester.select_move(test_moves, config=config)
        
        print("\n📊 API响应:")
        print(f"Status: 成功")
        print(f"Bot Move: {result.get('bot_move')}")
        
        diagnostics = result.get('diagnostics', {})
        print(f"Winprob: {diagnostics.get('winprob')}")
        print(f"Score: {diagnostics.get('score')}")
        print(f"Best Ten: {len(diagnostics.get('best_ten', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎮 SGF HTTP 测试工具 - 用户棋谱测试")
    print("=" * 60)
    
    # 快速API测试
    if not quick_api_test():
        print("\n❌ 快速API测试失败，请检查服务器状态")
        return
    
    print("\n" + "=" * 60)
    
    # 用户SGF测试
    if test_user_sgf():
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败，请检查配置")

if __name__ == '__main__':
    main()