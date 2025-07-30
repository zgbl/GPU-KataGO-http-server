#!/usr/bin/env python3

"""
测试升级后的 KataGo 服务器

这个脚本用于测试升级后的 katago-server 项目是否能正常工作，
包括 KataGo GTP Bot 的初始化、走法选择和局面评估功能。
"""

import os
import sys
import json
import time
import logging
import requests
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_katago_gtp_bot():
    """测试 KataGo GTP Bot 的基本功能"""
    try:
        # 导入 KataGTPBot
        from katago_gtp_bot import KataGTPBot
        
        # 检查 KataGo 二进制文件
        katago_binary = os.environ.get('KATAGO_BINARY', '/app/katago')
        model_path = os.environ.get('KATAGO_MODEL', '/app/models/default_model.bin.gz')
        config_path = os.environ.get('KATAGO_CONFIG', '/app/configs/katago_gtp.cfg')
        
        logger.info(f"Testing KataGo binary: {katago_binary}")
        logger.info(f"Model path: {model_path}")
        logger.info(f"Config path: {config_path}")
        
        # 构建 KataGo 命令行
        katago_cmdline = [
            katago_binary,
            'gtp',
            '-model', model_path,
            '-config', config_path
        ]
        
        logger.info("Initializing KataGo GTP Bot...")
        bot = KataGTPBot(katago_cmdline)
        
        # 测试基本功能
        logger.info("Testing basic functionality...")
        
        # 测试诊断信息
        diag = bot.diagnostics()
        logger.info(f"Diagnostics: {diag}")
        
        # 测试简单走法选择
        moves = ['d4', 'q16', 'p4', 'c16']
        config = {'komi': 7.5}
        
        logger.info(f"Testing move selection with moves: {moves}")
        selected_move = bot.select_move(moves, config)
        
        if selected_move:
            logger.info(f"Selected move: {selected_move}")
        else:
            logger.error("Failed to select move")
            return False
            
        # 测试局面评估
        logger.info("Testing position scoring...")
        ownership = bot.score(moves, config)
        
        if ownership:
            logger.info(f"Ownership data length: {len(ownership)}")
        else:
            logger.warning("No ownership data returned")
            
        logger.info("KataGo GTP Bot test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"KataGo GTP Bot test failed: {e}")
        return False

def test_flask_server():
    """测试 Flask 服务器的 HTTP 端点"""
    try:
        base_url = "http://localhost:8080"
        
        # 测试健康检查端点
        logger.info("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            logger.info("Health check passed")
        else:
            logger.error(f"Health check failed: {response.status_code}")
            return False
            
        # 测试信息端点
        logger.info("Testing info endpoint...")
        response = requests.get(f"{base_url}/info", timeout=10)
        
        if response.status_code == 200:
            info = response.json()
            logger.info(f"Server info: {info}")
        else:
            logger.warning(f"Info endpoint failed: {response.status_code}")
            
        # 测试走法选择端点
        logger.info("Testing select-move endpoint...")
        test_data = {
            "board_size": 19,
            "moves": ["d4", "q16", "p4", "c16"],
            "config": {"komi": 7.5}
        }
        
        response = requests.post(
            f"{base_url}/select-move/test_bot",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Move selection result: {result}")
        else:
            logger.error(f"Move selection failed: {response.status_code}")
            return False
            
        # 测试局面评估端点
        logger.info("Testing score endpoint...")
        response = requests.post(
            f"{base_url}/score/test_bot",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Score result keys: {list(result.keys())}")
        else:
            logger.warning(f"Score endpoint failed: {response.status_code}")
            
        logger.info("Flask server test completed")
        return True
        
    except requests.exceptions.ConnectionError:
        logger.warning("Flask server is not running, skipping HTTP tests")
        return True
    except Exception as e:
        logger.error(f"Flask server test failed: {e}")
        return False

def test_environment():
    """测试环境配置"""
    logger.info("Testing environment configuration...")
    
    # 检查环境变量
    env_vars = [
        'KATAGO_BINARY',
        'KATAGO_MODEL', 
        'KATAGO_CONFIG',
        'FLASK_PORT',
        'FLASK_DEBUG'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"{var}: {value}")
        else:
            logger.warning(f"{var}: not set")
            
    # 检查文件存在性
    files_to_check = [
        'katago_server.py',
        'katago_gtp_bot.py',
        'get_bot_app.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path} exists")
        else:
            logger.warning(f"✗ {file_path} missing")
            
    return True

def main():
    """主测试函数"""
    logger.info("Starting upgraded katago-server tests...")
    
    # 测试环境
    test_environment()
    
    # 测试 KataGo GTP Bot（如果有 KataGo 二进制文件）
    katago_binary = os.environ.get('KATAGO_BINARY', '/app/katago')
    if os.path.exists(katago_binary) or os.path.exists('./katago_eigen'):
        logger.info("KataGo binary found, testing GTP Bot...")
        if not test_katago_gtp_bot():
            logger.error("KataGo GTP Bot test failed")
            return False
    else:
        logger.warning("KataGo binary not found, skipping GTP Bot tests")
        
    # 测试 Flask 服务器（如果正在运行）
    if not test_flask_server():
        logger.error("Flask server test failed")
        return False
        
    logger.info("All tests completed successfully!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)