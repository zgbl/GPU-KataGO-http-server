#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo 引擎测试脚本 - 测试 192.168.0.162:8080
模拟前端 SGFAnalysis 发送的请求格式
"""

import requests
import json
import time
import sys
from datetime import datetime

KATAGO_URL = "http://192.168.0.162:8080"

def log(msg, level="INFO"):
    ts = datetime.now().strftime('%H:%M:%S')
    icons = {"INFO": "🔵", "OK": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"[{ts}] {icons.get(level, '🔵')} {msg}")

def test_health():
    """测试 /health 端点"""
    log("测试 /health ...")
    try:
        r = requests.get(f"{KATAGO_URL}/health", timeout=10)
        log(f"HTTP {r.status_code}: {r.text[:200]}", "OK" if r.ok else "FAIL")
        return r.ok
    except Exception as e:
        log(f"健康检查失败: {e}", "FAIL")
        return False

def test_info():
    """测试 /info 端点"""
    log("测试 /info ...")
    try:
        r = requests.get(f"{KATAGO_URL}/info", timeout=10)
        if r.ok:
            data = r.json()
            log(f"服务器: {data.get('name', 'unknown')} v{data.get('version', '?')}", "OK")
            log(f"模型: {data.get('model_file', 'unknown')}")
            log(f"端点: {data.get('endpoints', [])}")
        else:
            log(f"HTTP {r.status_code}: {r.text[:200]}", "FAIL")
        return r.ok
    except Exception as e:
        log(f"/info 失败: {e}", "FAIL")
        return False

def test_select_move_empty():
    """测试空棋盘 - 最简单的请求"""
    log("测试空棋盘 select-move ...")
    payload = {
        "board_size": 19,
        "moves": [],
        "config": {"request_id": "test_empty"}
    }
    return _do_select_move(payload, "空棋盘")

def test_select_move_position_only():
    """测试位置格式的 moves (旧格式: ['R4', 'D16'])"""
    log("测试 position-only 格式 (旧格式) ...")
    payload = {
        "board_size": 19,
        "moves": ["R4", "D16", "Q16"],
        "config": {"request_id": "test_position_only"}
    }
    return _do_select_move(payload, "position-only 格式")

def test_select_move_color_position():
    """测试颜色+位置格式 (前端实际发送的格式: [['B', 'P16'], ['W', 'Q4']])"""
    log("测试 color+position 格式 (前端格式) ...")
    payload = {
        "board_size": 19,
        "moves": [["B", "P16"], ["W", "Q4"]],
        "config": {"request_id": "test_color_position"}
    }
    return _do_select_move(payload, "color+position 格式")

def test_select_move_frontend_full():
    """完整模拟前端 analyzePosition 发送的请求"""
    log("测试前端完整 payload 格式 ...")
    payload = {
        "board_size": 19,
        "moves": [["B", "P16"], ["W", "Q4"]],
        "maxVisits": 800,
        "analysisWideRootNoise": 0.04,
        "includeOwnership": True,
        "includeMovesOwnership": False,
        "includePVVisits": True,
        "reportAnalysisWinratesAsRoot": True,
        "reportAnalysisWinrates": True,
        "overrideSettings": {
            "reportAnalysisWinratesAsRoot": True,
        },
        "reportDuringSearchEvery": 200
    }
    return _do_select_move(payload, "前端完整格式")

def _do_select_move(payload, label):
    """执行 select-move 请求"""
    url = f"{KATAGO_URL}/select-move/katago_gtp_bot"
    log(f"  POST {url}")
    log(f"  Payload: {json.dumps(payload, ensure_ascii=False)[:300]}")
    
    try:
        start = time.time()
        r = requests.post(url, json=payload, timeout=60, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'SGF-Analysis-Frontend/1.0'
        })
        elapsed = time.time() - start
        
        log(f"  HTTP {r.status_code} ({elapsed:.2f}s)")
        
        if r.ok:
            data = r.json()
            log(f"  bot_move: {data.get('bot_move', 'N/A')}", "OK")
            diag = data.get('diagnostics', {})
            if diag:
                log(f"  胜率: {diag.get('win_prob', 'N/A')}")
                log(f"  得分: {diag.get('score', 'N/A')}")
            
            # 检查前端需要的关键字段
            log(f"  winrate: {data.get('winrate', 'N/A')}")
            log(f"  score: {data.get('score', 'N/A')}")
            log(f"  analysis 长度: {len(data.get('analysis', []))}")
            log(f"  visits: {data.get('visits', 'N/A')}")
            
            # 打印完整响应（限制大小）
            resp_str = json.dumps(data, ensure_ascii=False, indent=2)
            if len(resp_str) > 2000:
                log(f"  完整响应 (截断): {resp_str[:2000]}...")
            else:
                log(f"  完整响应: {resp_str}")
            return True
        else:
            log(f"  错误响应: {r.text[:500]}", "FAIL")
            return False
            
    except requests.exceptions.Timeout:
        log(f"  请求超时 (60s)!", "FAIL")
        return False
    except Exception as e:
        log(f"  异常: {e}", "FAIL")
        return False

def main():
    log(f"KataGo 引擎测试 - 目标: {KATAGO_URL}")
    log("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Server Info", test_info),
        ("空棋盘", test_select_move_empty),
        ("Position-only 格式", test_select_move_position_only),
        ("Color+Position 格式", test_select_move_color_position),
        ("前端完整格式", test_select_move_frontend_full),
    ]
    
    passed = 0
    for name, func in tests:
        log(f"\n--- {name} ---")
        try:
            if func():
                passed += 1
        except KeyboardInterrupt:
            log("测试中断", "WARN")
            break
        except Exception as e:
            log(f"未预期错误: {e}", "FAIL")
        time.sleep(0.5)
    
    log(f"\n{'=' * 50}")
    log(f"结果: {passed}/{len(tests)} 通过", "OK" if passed == len(tests) else "WARN")

if __name__ == '__main__':
    main()
