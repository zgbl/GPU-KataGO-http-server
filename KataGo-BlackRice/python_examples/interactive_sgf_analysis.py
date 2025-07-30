#!/usr/bin/env python3
"""
交互式SGF分析工具
允许用户输入SGF内容或选择预设局面进行KataGo分析
"""

import json
import subprocess
import re
import sys

def send_analysis_to_docker(query_data, container_name="katago-analysis"):
    """向Docker容器发送分析请求"""
    try:
        query_json = json.dumps(query_data)
        
        cmd = [
            "docker", "exec", "-i", container_name,
            "/bin/bash", "-c", 
            f"echo '{query_json}' | katago analysis -config /app/configs/analysis_example.cfg -model /app/models/model.bin.gz"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return None, f"执行错误: {result.stderr}"
            
        # 查找JSON响应
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    return json.loads(line), None
                except json.JSONDecodeError:
                    continue
                    
        return None, "未找到有效响应"
        
    except subprocess.TimeoutExpired:
        return None, "分析超时"
    except Exception as e:
        return None, f"错误: {e}"

def parse_sgf_moves(sgf_content):
    """解析SGF内容中的着法"""
    moves = []
    
    # 清理SGF内容，移除换行和多余空格
    sgf_content = re.sub(r'\s+', ' ', sgf_content.strip())
    
    # 更强大的SGF解析 - 查找 ;B[xx] 和 ;W[xx] 模式
    # 支持空着法 ;B[] 和 ;W[]
    move_pattern = r';([BW])\[([a-s]{0,2})\]'
    matches = re.findall(move_pattern, sgf_content, re.IGNORECASE)
    
    print(f"调试: 找到 {len(matches)} 个匹配项")
    
    for color, pos in matches:
        color = color.upper()
        pos = pos.lower()
        
        if pos and len(pos) == 2:  # 非空着法且格式正确
            # 将SGF坐标转换为KataGo格式
            try:
                # SGF坐标: a-s (跳过i), 从左下角开始
                col_sgf = pos[0]
                row_sgf = pos[1]
                
                # 转换列坐标 (a-s -> A-T, 跳过I)
                col_num = ord(col_sgf) - ord('a')
                if col_num >= 8:  # 跳过i (第9个字母)
                    col_katago = chr(ord('A') + col_num + 1)
                else:
                    col_katago = chr(ord('A') + col_num)
                
                # 转换行坐标 (SGF从下往上，KataGo从上往下)
                row_num = ord(row_sgf) - ord('a')
                row_katago = str(19 - row_num)
                
                katago_pos = col_katago + row_katago
                moves.append([color, katago_pos])
                print(f"调试: {color} {pos} -> {katago_pos}")
                
            except Exception as e:
                print(f"调试: 转换坐标失败 {pos}: {e}")
                continue
        elif not pos:
            # 空着法 (pass)
            moves.append([color, "pass"])
            print(f"调试: {color} pass")
    
    return moves

def display_analysis_result(result):
    """显示分析结果"""
    if not result:
        return
        
    print(f"\n📊 分析结果 (ID: {result['id']})")
    print("-" * 50)
    
    if 'moveInfos' in result and result['moveInfos']:
        print("推荐着法 (前5个):")
        for i, move_info in enumerate(result['moveInfos'][:5]):
            move = move_info['move']
            winrate = move_info['winrate']
            visits = move_info['visits']
            
            # 计算分数差
            score_lead = move_info.get('scoreLead', 0)
            
            print(f"  {i+1}. {move:>4} - 胜率: {winrate:6.1%} - 访问: {visits:>6} - 分差: {score_lead:+.1f}")
    
    # 显示整体评估
    if 'rootInfo' in result:
        root = result['rootInfo']
        print(f"\n当前局面评估:")
        print(f"  胜率: {root.get('winrate', 0):.1%}")
        print(f"  分差: {root.get('scoreLead', 0):+.1f}")
        print(f"  总访问: {root.get('visits', 0)}")

def get_preset_positions():
    """获取预设局面"""
    return {
        "1": {
            "name": "空棋盘",
            "moves": []
        },
        "2": {
            "name": "星小目开局",
            "moves": [["B", "D4"], ["W", "Q16"], ["B", "P4"], ["W", "D16"]]
        },
        "3": {
            "name": "中国流布局",
            "moves": [["B", "Q4"], ["W", "D4"], ["B", "P16"], ["W", "Q16"], ["B", "R14"]]
        },
        "4": {
            "name": "小林流",
            "moves": [["B", "R4"], ["W", "D4"], ["B", "C16"], ["W", "Q16"], ["B", "C6"]]
        }
    }

def main():
    """主函数"""
    print("🔍 KataGo 交互式SGF分析工具")
    print("=" * 50)
    
    # 检查Docker容器
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=katago-analysis", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )
        if "katago-analysis" not in result.stdout:
            print("❌ Docker容器 katago-analysis 未运行")
            print("请先运行: docker-compose up katago-analysis")
            return
    except:
        print("❌ 无法检查Docker状态")
        return
    
    while True:
        print("\n请选择分析方式:")
        print("1. 预设局面")
        print("2. 输入SGF内容")
        print("3. 手动输入着法")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-3): ").strip()
        
        if choice == "0":
            print("再见!")
            break
            
        elif choice == "1":
            # 预设局面
            presets = get_preset_positions()
            print("\n可用的预设局面:")
            for key, preset in presets.items():
                print(f"  {key}. {preset['name']}")
                
            preset_choice = input("\n请选择预设局面: ").strip()
            if preset_choice in presets:
                preset = presets[preset_choice]
                moves = preset['moves']
                print(f"\n分析局面: {preset['name']}")
                print(f"着法序列: {moves}")
            else:
                print("无效选择")
                continue
                
        elif choice == "2":
            # SGF内容
            print("\n请输入SGF内容 (可以是完整SGF或部分内容):")
            sgf_content = input().strip()
            
            if not sgf_content:
                print("SGF内容不能为空")
                continue
                
            moves = parse_sgf_moves(sgf_content)
            print(f"\n解析到 {len(moves)} 手棋:")
            for i, move in enumerate(moves):
                print(f"  {i+1}. {move[0]} {move[1]}")
                
        elif choice == "3":
            # 手动输入
            print("\n请输入着法序列 (格式: B D4, W Q16, ...)")
            print("输入 'done' 完成输入")
            
            moves = []
            while True:
                move_input = input(f"第{len(moves)+1}手: ").strip()
                if move_input.lower() == 'done':
                    break
                    
                try:
                    parts = move_input.split()
                    if len(parts) == 2:
                        color, pos = parts
                        if color.upper() in ['B', 'W']:
                            moves.append([color.upper(), pos.upper()])
                            print(f"  添加: {color.upper()} {pos.upper()}")
                        else:
                            print("颜色必须是 B 或 W")
                    else:
                        print("格式错误，请输入: 颜色 位置 (如: B D4)")
                except:
                    print("输入格式错误")
                    
        else:
            print("无效选择")
            continue
        
        # 执行分析
        if 'moves' in locals():
            print(f"\n🔄 正在分析局面... (共{len(moves)}手)")
            
            query = {
                "id": f"interactive_analysis_{int(time.time()) if 'time' in dir() else 1}",
                "moves": moves,
                "rules": "tromp-taylor",
                "komi": 7.5,
                "boardXSize": 19,
                "boardYSize": 19,
                "analyzeTurns": [len(moves)],
                "maxVisits": 1000,
                "includeOwnership": True,
                "includePolicy": True,
                "includeMovesOwnership": False
            }
            
            result, error = send_analysis_to_docker(query)
            
            if result:
                display_analysis_result(result)
            else:
                print(f"❌ 分析失败: {error}")

if __name__ == "__main__":
    import time
    main()