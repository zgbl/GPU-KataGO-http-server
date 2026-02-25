#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo HTTP Server SGF 测试工具
支持手动输入SGF棋谱，逐步分析每一手棋
每5秒反馈一步分析结果
"""

import requests
import json
import time
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class SGFHTTPTester:
    """SGF HTTP 测试工具"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SGF-HTTP-Tester/1.0'
        })
        self.analysis_interval = 5  # 5秒间隔
    
    def print_status(self, message: str, status: str = "INFO"):
        """打印带状态的消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        status_symbols = {
            'INFO': '🔵',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️',
            'ANALYSIS': '🧠',
            'MOVE': '🎯'
        }
        symbol = status_symbols.get(status, '🔵')
        print(f"[{timestamp}] {symbol} {message}")
    
    def parse_sgf_moves(self, sgf_content: str) -> List[List[str]]:
        """解析SGF内容中的着法"""
        moves = []
        
        # 清理SGF内容
        sgf_content = re.sub(r'\s+', ' ', sgf_content.strip())
        
        # SGF解析正则表达式 - 匹配 ;B[xx] 或 ;W[xx] 格式
        move_pattern = r';([BW])\[([a-t]*)\]'
        matches = re.findall(move_pattern, sgf_content, re.IGNORECASE)
        
        self.print_status(f"找到 {len(matches)} 个着法匹配项")
        
        for i, (color, pos) in enumerate(matches):
            color = color.upper()
            pos = pos.lower().strip()
            
            if pos and len(pos) == 2:  # 正常着法
                try:
                    col_sgf = pos[0]  # a-s
                    row_sgf = pos[1]  # a-s
                    
                    # 检查坐标范围
                    if col_sgf < 'a' or col_sgf > 's' or row_sgf < 'a' or row_sgf > 's':
                        self.print_status(f"跳过无效坐标: {pos}", "WARNING")
                        continue
                    
                    # 转换列坐标 (a-s -> A-T, 跳过I)
                    col_index = ord(col_sgf) - ord('a')  # 0-18
                    if col_index >= 8:  # i及之后的字母
                        col_katago = chr(ord('A') + col_index + 1)  # 跳过I
                    else:
                        col_katago = chr(ord('A') + col_index)
                    
                    # 转换行坐标 (SGF的a=19行, s=1行)
                    row_index = ord(row_sgf) - ord('a')  # 0-18
                    row_katago = str(19 - row_index)
                    
                    katago_pos = col_katago + row_katago
                    moves.append([color, katago_pos])
                    
                except Exception as e:
                    self.print_status(f"转换失败 {pos}: {e}", "ERROR")
                    continue
                    
            elif not pos:  # 空着法
                moves.append([color, "pass"])
            else:
                self.print_status(f"跳过格式错误的着法: {pos}", "WARNING")
        
        return moves
    
    def health_check(self) -> Dict:
        """检查服务器健康状态"""
        response = self.session.get(f"{self.base_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()
    
    def test_server_connection(self) -> bool:
        """测试服务器连接"""
        self.print_status("测试服务器连接...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_status(f"服务器连接成功: {data.get('status')}", "SUCCESS")
                return True
            else:
                self.print_status(f"服务器连接失败: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"服务器连接异常: {str(e)}", "ERROR")
            return False
    
    def get_server_info(self) -> Optional[Dict]:
        """获取服务器信息"""
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_status(f"服务器: {data.get('name')} v{data.get('version')}", "INFO")
                self.print_status(f"模型: {data.get('model_file')}", "INFO")
                return data
            else:
                self.print_status(f"获取服务器信息失败: HTTP {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.print_status(f"获取服务器信息异常: {str(e)}", "ERROR")
            return None
    
    def test_connection(self):
        """测试服务器连接"""
        try:
            health = self.health_check()
            info = self.get_server_info()
            self.print_status(f"✅ 服务器连接成功: {health.get('status', 'Unknown')}", "SUCCESS")
            self.print_status(f"📦 服务器版本: {info.get('version', 'Unknown')}")
            return True
        except Exception as e:
            self.print_status(f"❌ 服务器连接失败: {e}", "ERROR")
            return False
    
    def select_move(self, moves, board_size=19, config=None):
        """调用KataGo API获取推荐走法"""
        if config is None:
            config = {"request_id": f"sgf_test_{int(time.time())}"}
        
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
    
    def analyze_position(self, moves: List[List[str]], move_number: int) -> Optional[Dict]:
        """分析指定手数的局面"""
        try:
            # 转换moves格式为API需要的格式，保持[color, position]格式
            api_moves = moves[:move_number]
            
            config = {
                "request_id": f"sgf_analysis_{move_number}",
                "max_visits": 1000,
                "include_ownership": True,
                "include_policy": True,
                "include_pv": True
            }
            
            start_time = time.time()
            data = self.select_move(api_moves, board_size=19, config=config)
            elapsed_time = time.time() - start_time
            
            data['analysis_time'] = elapsed_time
            return data
                
        except Exception as e:
            self.print_status(f"分析异常: {str(e)}", "ERROR")
            return None
    
    def format_analysis_result(self, result: Dict, move_number: int, current_move: List[str]) -> str:
        """格式化分析结果"""
        if not result:
            return "分析失败"
        
        diagnostics = result.get('diagnostics', {})
        analysis_time = result.get('analysis_time', 0)
        
        # 提取关键信息 - 优先从diagnostics中获取
        bot_move = result.get('bot_move') or diagnostics.get('bot_move', 'N/A')
        win_prob = diagnostics.get('winprob', 'N/A')
        score_lead = diagnostics.get('score_lead', 'N/A')
        visits = diagnostics.get('visits', 'N/A')
        best_ten = diagnostics.get('best_ten', [])
        
        # 如果winprob为None，尝试从score计算胜率估算
        if win_prob is None and 'score' in diagnostics:
            score = diagnostics.get('score')
            if isinstance(score, (int, float)):
                # 简单的分数到胜率转换（这只是估算）
                if score > 0:
                    win_prob = min(0.5 + score / 20.0, 0.95)  # 正分数偏向当前方
                else:
                    win_prob = max(0.5 + score / 20.0, 0.05)  # 负分数偏向对方
        
        # 格式化胜率
        if isinstance(win_prob, (int, float)):
            win_prob = f"{win_prob * 100:.1f}%"
        elif win_prob is None:
            win_prob = "N/A"
        
        # 格式化分差
        if isinstance(score_lead, (int, float)):
            score_lead = f"{score_lead:.1f}"
        elif score_lead is None:
            score_lead = "N/A"
        
        # 格式化访问次数（从best_ten中获取）
        if visits == 'N/A' and best_ten and len(best_ten) > 0:
            visits = best_ten[0].get('visits', 'N/A')
        
        # 格式化输出
        output = []
        output.append(f"第{move_number}手: {current_move[0]} {current_move[1]}")
        output.append(f"推荐走法: {bot_move}")
        output.append(f"胜率: {win_prob}")
        output.append(f"分差: {score_lead}")
        output.append(f"访问次数: {visits}")
        output.append(f"分析时间: {analysis_time:.2f}秒")
        
        return " | ".join(output)
    
    def step_by_step_analysis(self, moves: List[List[str]], start_from: int = 1, end_at: Optional[int] = None):
        """逐步分析棋局"""
        if end_at is None:
            end_at = len(moves)
        
        self.print_status(f"开始逐步分析: 第{start_from}手到第{end_at}手", "ANALYSIS")
        self.print_status(f"分析间隔: {self.analysis_interval}秒")
        
        for i in range(start_from, end_at + 1):
            current_move = moves[i - 1]
            
            self.print_status(f"分析第{i}手: {current_move[0]} {current_move[1]}", "MOVE")
            
            # 分析当前局面
            result = self.analyze_position(moves, i)
            
            if result:
                analysis_text = self.format_analysis_result(result, i, current_move)
                self.print_status(analysis_text, "SUCCESS")
            else:
                self.print_status(f"第{i}手分析失败", "ERROR")
            
            # 如果不是最后一手，等待指定时间
            if i < end_at:
                self.print_status(f"等待{self.analysis_interval}秒后继续...")
                time.sleep(self.analysis_interval)
        
        self.print_status("分析完成!", "SUCCESS")
    
    def interactive_mode(self):
        """交互模式"""
        self.print_status("进入交互模式")
        
        while True:
            print("\n" + "="*60)
            print("SGF HTTP 测试工具 - 交互模式")
            print("1. 输入SGF内容进行分析")
            print("2. 使用示例SGF")
            print("3. 设置分析间隔")
            print("4. 测试服务器连接")
            print("5. 退出")
            print("="*60)
            
            choice = input("请选择操作 (1-5): ").strip()
            
            if choice == "1":
                self.handle_sgf_input()
            elif choice == "2":
                self.handle_example_sgf()
            elif choice == "3":
                self.handle_set_interval()
            elif choice == "4":
                self.test_server_connection()
                self.get_server_info()
            elif choice == "5":
                self.print_status("退出程序", "INFO")
                break
            else:
                self.print_status("无效选择，请重新输入", "WARNING")
    
    def handle_sgf_input(self):
        """处理SGF输入"""
        print("\n请输入SGF内容 (输入空行结束):")
        sgf_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            sgf_lines.append(line)
        
        sgf_content = '\n'.join(sgf_lines)
        
        if not sgf_content.strip():
            self.print_status("SGF内容不能为空", "ERROR")
            return
        
        self.process_sgf(sgf_content)
    
    def handle_example_sgf(self):
        """处理示例SGF"""
        example_sgf = """(;FF[4]
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
        
        self.print_status("使用示例SGF进行分析", "INFO")
        self.process_sgf(example_sgf)
    
    def handle_set_interval(self):
        """设置分析间隔"""
        try:
            interval = float(input(f"请输入分析间隔(秒，当前: {self.analysis_interval}): "))
            if interval > 0:
                self.analysis_interval = interval
                self.print_status(f"分析间隔已设置为 {interval} 秒", "SUCCESS")
            else:
                self.print_status("间隔必须大于0", "ERROR")
        except ValueError:
            self.print_status("无效的数值", "ERROR")
    
    def process_sgf(self, sgf_content: str):
        """处理SGF内容"""
        # 解析SGF
        moves = self.parse_sgf_moves(sgf_content)
        
        if not moves:
            self.print_status("未解析到有效着法，请检查SGF格式", "ERROR")
            return
        
        self.print_status(f"解析到 {len(moves)} 手棋", "SUCCESS")
        
        # 显示前几手
        preview_count = min(5, len(moves))
        for i in range(preview_count):
            color, pos = moves[i]
            self.print_status(f"第{i+1}手: {color} {pos}", "INFO")
        
        if len(moves) > preview_count:
            self.print_status(f"... 还有 {len(moves) - preview_count} 手", "INFO")
        
        # 设置分析范围
        try:
            range_input = input(f"\n分析范围 (1-{len(moves)}, 格式: 开始-结束 或 结束手数, 直接回车分析全部): ").strip()
            
            start_from = 1
            end_at = len(moves)
            
            if range_input:
                if '-' in range_input:
                    start_str, end_str = range_input.split('-', 1)
                    start_from = int(start_str.strip())
                    end_at = int(end_str.strip())
                else:
                    end_at = int(range_input)
                
                # 验证范围
                if start_from < 1 or end_at > len(moves) or start_from > end_at:
                    self.print_status("无效范围，使用默认范围", "WARNING")
                    start_from = 1
                    end_at = len(moves)
            
            # 确认开始分析
            confirm = input(f"\n确定分析第{start_from}手到第{end_at}手吗？(y/N): ").strip().lower()
            if confirm == 'y':
                # 测试连接
                if not self.test_server_connection():
                    self.print_status("服务器连接失败，无法进行分析", "ERROR")
                    return
                
                # 开始分析
                self.step_by_step_analysis(moves, start_from, end_at)
            else:
                self.print_status("取消分析", "INFO")
                
        except ValueError:
            self.print_status("无效的范围格式", "ERROR")
        except KeyboardInterrupt:
            self.print_status("\n用户中断分析", "WARNING")

def main():
    """主函数"""
    print("KataGo HTTP Server SGF 测试工具")
    print("支持手动输入SGF棋谱，逐步分析每一手棋")
    print("="*60)
    
    # 解析命令行参数
    base_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # 创建测试器
    tester = SGFHTTPTester(base_url)
    
    try:
        # 进入交互模式
        tester.interactive_mode()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序异常: {e}")
    
    print("\n感谢使用 SGF HTTP 测试工具!")

if __name__ == '__main__':
    main()