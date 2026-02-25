#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo 整合版 HTTP Server
结合最新GPU KataGo引擎和HTTP API服务器

作者: Blckrice Tech
创建时间: 2025年7月30日
"""

import sys
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# 添加katago-server目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'katago-server'))

from katago_gtp_bot import KataGTPBot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedKataGoServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS支持
        
        # 配置参数
        self.katago_binary = os.environ.get('KATAGO_BINARY', '/app/bin/katago')
        self.model_file = os.environ.get('KATAGO_MODEL', '/app/models/model.bin.gz')
        self.config_file = os.environ.get('KATAGO_CONFIG', '/app/cpp/configs/analysis_example.cfg')
        self.port = int(os.environ.get('HTTP_PORT', '8080'))
        
        logger.info(f"初始化KataGo HTTP服务器")
        logger.info(f"KataGo二进制文件: {self.katago_binary}")
        logger.info(f"模型文件: {self.model_file}")
        logger.info(f"配置文件: {self.config_file}")
        
        # 检查文件存在性
        self._check_files()
        
        # 初始化KataGo引擎
        self._init_katago()
        
        # 设置路由
        self._setup_routes()
    
    def _check_files(self):
        """检查必要文件是否存在"""
        files_to_check = [
            (self.katago_binary, "KataGo二进制文件"),
            (self.model_file, "模型文件"),
            (self.config_file, "配置文件")
        ]
        
        for file_path, description in files_to_check:
            if not os.path.exists(file_path):
                error_msg = f"{description}不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            logger.info(f"✓ {description}: {file_path}")
    
    def _init_katago(self):
        """初始化KataGo Analysis引擎"""
        try:
            katago_cmd = f"{self.katago_binary} analysis -model {self.model_file} -config {self.config_file}"
            logger.info(f"启动KataGo命令: {katago_cmd}")
            
            self.katago_bot = KataGTPBot(katago_cmd.split())
            logger.info("✓ KataGo Analysis引擎初始化成功")
            
        except Exception as e:
            error_msg = f"KataGo引擎初始化失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _setup_routes(self):
        """设置Flask路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': 'integrated-v1.0'
            })
        
        @self.app.route('/select-move/katago_gtp_bot', methods=['POST'])
        def select_move():
            """获取最佳走法"""
            try:
                dtstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                content = request.json
                
                if not content:
                    return jsonify({'error': '请求体不能为空'}), 400
                
                board_size = content.get('board_size', 19)
                moves = content.get('moves', [])
                config = content.get('config', {})
                
                logger.info(f'>>> {dtstr} select_move board_size={board_size} moves_count={len(moves)} config={config}')
                
                # 转换moves格式：从[['B', 'R16'], ['W', 'C4']]转换为['R16', 'C4']
                if moves and isinstance(moves[0], list) and len(moves[0]) == 2:
                    # 如果moves是包含颜色信息的格式，提取位置信息
                    position_moves = [move[1] for move in moves]
                    logger.info(f'Converted moves from color+position format to position-only: {position_moves}')
                else:
                    # 如果moves已经是位置字符串列表，直接使用
                    position_moves = moves
                    logger.info(f'Using moves as-is (position-only format): {position_moves}')
                
                # 调用KataGo引擎
                bot_move = self.katago_bot.select_move(position_moves, config)
                diagnostics = self.katago_bot.diagnostics()
                
                response = {
                    'bot_move': bot_move,
                    'diagnostics': diagnostics,
                    'request_id': config.get('request_id', ''),
                    'timestamp': dtstr
                }
                
                logger.info(f'<<< {dtstr} select_move response: {bot_move}')
                return jsonify(response)
                
            except Exception as e:
                error_msg = f"选择走法时发生错误: {str(e)}"
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 500
        
        @self.app.route('/score/katago_gtp_bot', methods=['POST'])
        def score():
            """获取局面评估"""
            try:
                dtstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                content = request.json
                
                if not content:
                    return jsonify({'error': '请求体不能为空'}), 400
                
                board_size = content.get('board_size', 19)
                moves = content.get('moves', [])
                config = content.get('config', {})
                
                logger.info(f'>>> {dtstr} score board_size={board_size} moves_count={len(moves)} config={config}')
                
                # 调用KataGo引擎
                ownership_arr = self.katago_bot.score(moves, config)
                diagnostics = self.katago_bot.diagnostics()
                
                response = {
                    'probs': ownership_arr,
                    'diagnostics': diagnostics,
                    'request_id': config.get('request_id', ''),
                    'timestamp': dtstr
                }
                
                logger.info(f'<<< {dtstr} score response length: {len(ownership_arr) if ownership_arr else 0}')
                return jsonify(response)
                
            except Exception as e:
                error_msg = f"评估局面时发生错误: {str(e)}"
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 500
        
        @self.app.route('/info', methods=['GET'])
        def info():
            """获取服务器信息"""
            return jsonify({
                'name': 'KataGo Integrated HTTP Server',
                'version': 'integrated-v1.0',
                'katago_binary': self.katago_binary,
                'model_file': os.path.basename(self.model_file),
                'config_file': os.path.basename(self.config_file),
                'endpoints': [
                    '/health',
                    '/info',
                    '/select-move/katago_gtp_bot',
                    '/score/katago_gtp_bot'
                ]
            })
    
    def run(self):
        """启动HTTP服务器"""
        logger.info(f"🚀 启动KataGo整合版HTTP服务器，端口: {self.port}")
        self.app.run(
            host='0.0.0.0',
            port=self.port,
            debug=False,
            threaded=True
        )

def main():
    """主函数"""
    try:
        # 创建日志目录
        os.makedirs('/app/logs', exist_ok=True)
        
        # 启动服务器
        server = IntegratedKataGoServer()
        server.run()
        
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()