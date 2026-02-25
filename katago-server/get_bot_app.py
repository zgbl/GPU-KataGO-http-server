#!/usr/bin/env python3

# /********************************************************************
# Filename: get_bot_app.py
# Author: AHN (Updated for modern environment)
# Creation Date: Mar, 2019
# Updated: Jan, 2025 - Modernized for Flask 2.x, better error handling
# **********************************************************************/
#
# Flask endpoint to get the next move from any bot
# Now with improved logging and error handling
#

import os
import logging
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# 配置日志
logger = logging.getLogger(__name__)

# Return a flask app that will ask the specified bot for a move.
#-----------------------------------------------------------------
def get_bot_app(name, bot):
    """创建包含机器人端点的 Flask 应用"""
    
    here = os.path.dirname(__file__)
    static_path = os.path.join(here, 'static')
    app = Flask(__name__, static_folder=static_path, static_url_path='/static')
    
    # 启用 CORS
    CORS(app)
    
    @app.route('/select-move/' + name, methods=['POST'])
    def select_move():
        """请求机器人选择下一步走法"""
        try:
            dtstr = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            
            # 验证请求内容
            if not request.is_json:
                logger.error("Request must be JSON")
                return jsonify({'error': 'Request must be JSON'}), 400
            
            content = request.json
            if not content:
                logger.error("Empty request body")
                return jsonify({'error': 'Empty request body'}), 400
            
            # 验证必需字段
            if 'board_size' not in content:
                logger.error("Missing required field: board_size")
                return jsonify({'error': 'Missing required field: board_size'}), 400
            
            if 'moves' not in content:
                logger.error("Missing required field: moves")
                return jsonify({'error': 'Missing required field: moves'}), 400
            
            logger.info(f'{dtstr} select move {name} {str(content.get("config", {}))}')
            
            board_size = content['board_size']
            moves = content['moves']
            config = content.get('config', {})
            
            # 验证棋盘大小
            if not isinstance(board_size, int) or board_size < 9 or board_size > 25:
                logger.error(f"Invalid board size: {board_size}")
                return jsonify({'error': 'Board size must be between 9 and 25'}), 400
            
            # 验证走法格式
            if not isinstance(moves, list):
                logger.error("Moves must be a list")
                return jsonify({'error': 'Moves must be a list'}), 400
            
            # 调用机器人选择走法
            bot_move = bot.select_move(moves, config)
            diag = bot.diagnostics()
            
            response = {
                'bot_move': bot_move,
                'diagnostics': diag,
                'request_id': config.get('request_id', ''),
                'timestamp': dtstr
            }
            
            logger.info(f"Move selected: {bot_move}")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in select_move: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500

    @app.route('/score/' + name, methods=['POST'])
    def score():
        """请求机器人评估局面"""
        try:
            dtstr = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            
            # 验证请求内容
            if not request.is_json:
                logger.error("Request must be JSON")
                return jsonify({'error': 'Request must be JSON'}), 400
            
            content = request.json
            if not content:
                logger.error("Empty request body")
                return jsonify({'error': 'Empty request body'}), 400
            
            # 验证必需字段
            if 'board_size' not in content:
                logger.error("Missing required field: board_size")
                return jsonify({'error': 'Missing required field: board_size'}), 400
            
            if 'moves' not in content:
                logger.error("Missing required field: moves")
                return jsonify({'error': 'Missing required field: moves'}), 400
            
            logger.info(f'{dtstr} score {name} {str(content.get("config", {}))}')
            
            board_size = content['board_size']
            moves = content['moves']
            config = content.get('config', {})
            
            # 验证棋盘大小
            if not isinstance(board_size, int) or board_size < 9 or board_size > 25:
                logger.error(f"Invalid board size: {board_size}")
                return jsonify({'error': 'Board size must be between 9 and 25'}), 400
            
            # 验证走法格式
            if not isinstance(moves, list):
                logger.error("Moves must be a list")
                return jsonify({'error': 'Moves must be a list'}), 400
            
            # 调用机器人评估局面
            ownership_arr = bot.score(moves, config)
            diag = bot.diagnostics()
            
            response = {
                'probs': ownership_arr,
                'diagnostics': diag,
                'request_id': config.get('request_id', ''),
                'timestamp': dtstr
            }
            
            logger.info(f"Score calculated for {len(moves)} moves")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in score: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500

    return app
