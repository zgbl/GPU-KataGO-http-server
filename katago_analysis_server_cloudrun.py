#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo Analysis HTTP Server - Cloud Run优化版本
专门为Google Cloud Run免费版本优化的轻量化服务器
"""

import os
import sys
import json
import logging
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from queue import Queue, Empty

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudRunKataGoEngine:
    """Cloud Run优化的KataGo引擎"""
    
    def __init__(self, katago_binary, config_file):
        self.katago_binary = katago_binary
        self.config_file = config_file
        self.process = None
        self.input_queue = Queue(maxsize=10)
        self.output_queue = Queue(maxsize=10)
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """启动KataGo引擎"""
        try:
            cmd = [
                self.katago_binary, 'analysis',
                '-config', self.config_file
            ]
            
            logger.info(f"启动KataGo: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            self.running = True
            threading.Thread(target=self._input_handler, daemon=True).start()
            threading.Thread(target=self._output_handler, daemon=True).start()
            
            logger.info("KataGo引擎启动成功")
            return True
            
        except Exception as e:
            logger.error(f"KataGo启动失败: {e}")
            return False
    
    def _input_handler(self):
        """处理输入队列"""
        while self.running and self.process and self.process.poll() is None:
            try:
                query = self.input_queue.get(timeout=1.0)
                if query:
                    self.process.stdin.write(query + '\n')
                    self.process.stdin.flush()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"输入处理错误: {e}")
                break
    
    def _output_handler(self):
        """处理输出"""
        while self.running and self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        self.output_queue.put(line)
            except Exception as e:
                logger.error(f"输出处理错误: {e}")
                break
    
    def analyze_position(self, board_size, moves, max_visits=100):
        """分析局面（Cloud Run优化版本）"""
        try:
            query = {
                "id": f"analysis_{int(time.time() * 1000)}",
                "moves": moves,
                "rules": "chinese",
                "komi": 7.5,
                "boardXSize": board_size,
                "boardYSize": board_size,
                "analyzeTurns": [len(moves)] if moves else [0],
                "maxVisits": min(max_visits, 200),  # 限制访问次数以节省资源
                "includeOwnership": False,  # 减少数据传输
                "includePolicy": True,
                "includePVVisits": False
            }
            
            query_str = json.dumps(query)
            self.input_queue.put(query_str)
            
            # 等待响应（缩短超时时间）
            timeout = 15
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = self.output_queue.get(timeout=1.0)
                    if response:
                        try:
                            result = json.loads(response)
                            if result.get('id') == query['id']:
                                return result
                        except json.JSONDecodeError:
                            continue
                except Empty:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"分析错误: {e}")
            return None
    
    def stop(self):
        """停止引擎"""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.process = None

# 创建Flask应用
app = Flask(__name__)
CORS(app, origins="*")

# 全局引擎实例
engine = None

def init_engine():
    """初始化引擎"""
    global engine
    katago_binary = os.environ.get('KATAGO_BINARY', '/app/bin/katago')
    config_file = os.environ.get('KATAGO_CONFIG', '/app/configs/analysis_example.cfg')
    
    engine = CloudRunKataGoEngine(katago_binary, config_file)
    if not engine.start():
        logger.error("引擎启动失败")
        sys.exit(1)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'KataGo Analysis Server - Cloud Run',
        'version': 'cloudrun-v1.0',
        'status': 'running'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        board_size = data.get('board_size', 19)
        moves = data.get('moves', [])
        max_visits = min(data.get('max_visits', 100), 200)  # 限制最大访问次数
        
        # 转换走法格式
        if moves and isinstance(moves[0], list):
            analysis_moves = moves
        else:
            analysis_moves = []
            for i, move in enumerate(moves):
                color = 'B' if i % 2 == 0 else 'W'
                analysis_moves.append([color, move])
        
        result = engine.analyze_position(board_size, analysis_moves, max_visits)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Analysis failed'}), 500
            
    except Exception as e:
        logger.error(f"分析错误: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_engine()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
else:
    # Gunicorn启动时初始化
    init_engine()