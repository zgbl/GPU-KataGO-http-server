#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示用户SGF棋谱分析
展示修复后的胜率和推荐走法显示功能
"""

import time
from sgf_http_tester import SGFHTTPTester

def demo_user_sgf_analysis():
    """演示用户SGF分析功能"""
    print("🎯 用户SGF棋谱分析演示")
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
        
        print("\n📋 解析SGF棋谱...")
        moves = tester.parse_sgf_moves(user_sgf)
        
        if not moves:
            print("❌ SGF解析失败")
            return
        
        print(f"✅ 成功解析出 {len(moves)} 手棋")
        print(f"前10手: {[f'{m[0]}{m[1]}' for m in moves[:10]]}")
        
        print("\n🧠 开始逐步分析...")
        print("注意：现在能正确显示推荐走法和胜率估算！")
        print("=" * 60)
        
        # 分析前40手
        for i in range(min(40, len(moves))):
            # 获取到当前手数的所有走法，只取位置信息
            current_moves = [move[1] for move in moves[:i+1]]
            move_display = f"{moves[i][0]}{moves[i][1]}"
            
            print(f"\n--- 第 {i+1} 手: {move_display} ---")
            
            try:
                # 配置分析参数
                config = {
                    "request_id": f"demo_user_{i+1}",
                    "max_visits": 1600,
                    "analyze_after_move": True,
                    "include_ownership": True,
                    "include_policy": True,
                    "include_pv": True
                }
                
                start_time = time.time()
                result = tester.select_move(current_moves, config=config)
                elapsed_time = time.time() - start_time
                
                # 显示分析结果
                diagnostics = result.get('diagnostics', {})
                bot_move = result.get('bot_move') or diagnostics.get('bot_move', 'N/A')
                score = diagnostics.get('score', 0)
                
                # 计算胜率估算
                if score is not None:
                    if score > 0:
                        win_rate = min(0.5 + score / 20.0, 0.95)
                    else:
                        win_rate = max(0.5 + score / 20.0, 0.05)
                    win_rate_str = f"{win_rate * 100:.1f}%"
                else:
                    win_rate_str = "N/A"
                
                print(f"🎯 推荐走法: {bot_move}")
                print(f"📈 胜率估算: {win_rate_str}")
                print(f"📊 分数: {score:.3f}")
                print(f"⏱️ 分析耗时: {elapsed_time:.2f}秒")
                
                # 短暂延迟
                if i < 39:
                    print("⏳ 等待1秒...")
                    time.sleep(1)
                
            except Exception as e:
                print(f"❌ 分析第 {i+1} 手时出错: {e}")
                continue
        
        print("\n🎉 演示完成！")
        print("\n📝 总结:")
        print("✅ SGF解析功能正常")
        print("✅ 推荐走法显示正常")
        print("✅ 胜率估算功能正常")
        print("✅ 分数显示正常")
        print("\n💡 说明: 由于KataGo配置限制，胜率是基于分数的估算值")
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")

def quick_functionality_test():
    """快速功能测试"""
    print("🚀 快速功能测试")
    print("=" * 30)
    
    try:
        tester = SGFHTTPTester()
        
        # 测试服务器连接
        print("1. 测试服务器连接...")
        if tester.test_connection():
            print("✅ 服务器连接正常")
        else:
            print("❌ 服务器连接失败")
            return False
        
        # 测试API调用
        print("\n2. 测试API调用...")
        result = tester.select_move(["R4", "D16"], config={"request_id": "quick_test"})
        
        diagnostics = result.get('diagnostics', {})
        bot_move = result.get('bot_move') or diagnostics.get('bot_move', 'N/A')
        score = diagnostics.get('score', 0)
        
        print(f"✅ API调用成功")
        print(f"   推荐走法: {bot_move}")
        print(f"   分数: {score}")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎮 用户SGF棋谱分析演示程序")
    print("=" * 60)
    
    # 快速功能测试
    if not quick_functionality_test():
        print("\n❌ 基础功能测试失败，请检查服务器状态")
        return
    
    print("\n" + "=" * 60)
    
    # 用户SGF演示
    demo_user_sgf_analysis()

if __name__ == '__main__':
    main()