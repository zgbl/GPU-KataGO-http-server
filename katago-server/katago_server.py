#!/usr/bin/env python3

# /********************************************************************
# Filename: katago_server.py
# Author: AHN (Updated for modern environment)
# Creation Date: Jan, 2020
# Updated: Jan, 2025 - Modernized for Ubuntu 22.04, Flask 2.x, GPU support
# **********************************************************************/
#
# A back end API to run KataGo as a REST service
# Now supports GPU acceleration and modern Flask
#

import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from katago_gtp_bot import KataGTPBot
from get_bot_app import get_bot_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/katago_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_katago_config():
    """获取 KataGo 配置"""
    # 从环境变量获取配置，如果没有则使用默认值
    katago_binary = os.getenv('KATAGO_BINARY', '/usr/local/bin/katago')
    katago_model = os.getenv('KATAGO_MODEL', '/app/models/model.bin.gz')
    katago_config = os.getenv('KATAGO_CONFIG', '/app/configs/katago_gtp.cfg')
    
    # 检查文件是否存在
    if not os.path.exists(katago_binary):
        logger.error(f"KataGo binary not found: {katago_binary}")
        sys.exit(1)
    
    if not os.path.exists(katago_model):
        logger.error(f"KataGo model not found: {katago_model}")
        logger.info("Please mount model file to /app/models/model.bin.gz")
        sys.exit(1)
    
    if not os.path.exists(katago_config):
        logger.warning(f"KataGo config not found: {katago_config}, using default")
        katago_config = None
    
    return katago_binary, katago_model, katago_config

def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 启用 CORS
    CORS(app)
    
    # 获取 KataGo 配置
    katago_binary, katago_model, katago_config = get_katago_config()
    
    # 构建 KataGo 命令
    katago_cmd_parts = [katago_binary, 'gtp', '-model', katago_model]
    if katago_config:
        katago_cmd_parts.extend(['-config', katago_config])
    
    logger.info(f"Starting KataGo with command: {' '.join(katago_cmd_parts)}")
    
    # 创建 KataGo GTP Bot
    try:
        katago_gtp_bot = KataGTPBot(katago_cmd_parts)
        logger.info("KataGo GTP Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize KataGo GTP Bot: {e}")
        sys.exit(1)
    
    # 获取带有机器人端点的应用
    bot_app = get_bot_app(name='katago_gtp_bot', bot=katago_gtp_bot)
    
    # 将机器人路由注册到主应用
    for rule in bot_app.url_map.iter_rules():
        app.add_url_rule(
            rule.rule,
            endpoint=rule.endpoint,
            view_func=bot_app.view_functions[rule.endpoint],
            methods=rule.methods
        )
    
    # 添加健康检查端点
    @app.route('/health')
    def health_check():
        """健康检查端点"""
        try:
            # 简单检查 KataGo 是否响应
            return jsonify({
                'status': 'healthy',
                'katago_binary': katago_binary,
                'katago_model': os.path.basename(katago_model),
                'katago_config': os.path.basename(katago_config) if katago_config else 'default'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    
    # 添加信息端点
    @app.route('/info')
    def server_info():
        """服务器信息端点"""
        return jsonify({
            'server': 'KataGo HTTP Server',
            'version': '2.0.0',
            'katago_binary': katago_binary,
            'katago_model': os.path.basename(katago_model),
            'katago_config': os.path.basename(katago_config) if katago_config else 'default',
            'endpoints': [
                '/health',
                '/info',
                '/select-move/katago_gtp_bot',
                '/score/katago_gtp_bot'
            ]
        })
    
    return app

# 创建应用实例
app = create_app()

#----------------------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting KataGo HTTP Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
