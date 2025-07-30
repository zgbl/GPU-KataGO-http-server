#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KataGo Analysis HTTP Server
专门为KataGo Analysis引擎设计的HTTP服务器
使用JSON通信协议获取完整的分析数据

作者: Blckrice Tech
创建时间: 2025年7月30日
"""

import sys
import os
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KataGoAnalysisEngine:
    def __init__(self, katago_binary, model_file, config_file):
        self.katago_binary = katago_binary
        self.model_file = model_file
        self.config_file = config_file
        self.process = None
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """启动KataGo Analysis引擎"""
        try:
            cmd = [
                self.katago_binary, 'analysis',
                '-model', self.model_file,
                '-config', self.config_file
            ]
            
            logger.info(f"启动KataGo Analysis引擎: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            self.running = True
            
            # 启动输入输出处理线程
            threading.Thread(target=self._input_handler, daemon=True).start()
            threading.Thread(target=self._output_handler, daemon=True).start()
            
            logger.info("✓ KataGo Analysis引擎启动成功")
            return True
            
        except Exception as e:
            logger.error(f"KataGo Analysis引擎启动失败: {str(e)}")
            return False
    
    def _input_handler(self):
        """处理输入队列"""
        while self.running and self.process and self.process.poll() is None:
            try:
                query = self.input_queue.get(timeout=1.0)
                if query:
                    logger.debug(f"发送查询: {query}")
                    self.process.stdin.write(query + '\n')
                    self.process.stdin.flush()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"输入处理错误: {str(e)}")
                break
    
    def _output_handler(self):
        """处理输出"""
        while self.running and self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:
                        logger.debug(f"收到响应: {line}")
                        self.output_queue.put(line)
            except Exception as e:
                logger.error(f"输出处理错误: {str(e)}")
                break
    
    def analyze_position(self, board_size, moves, config=None):
        """分析局面"""
        try:
            # 构建分析查询
            query = {
                "id": f"analysis_{int(time.time() * 1000)}",
                "moves": moves,
                "rules": "chinese",
                "komi": config.get('komi', 7.5) if config else 7.5,
                "boardXSize": board_size,
                "boardYSize": board_size,
                "analyzeTurns": [len(moves)] if moves else [0],
                "maxVisits": config.get('maxVisits', 500) if config else 500,
                "includeOwnership": True,
                "includePolicy": True,
                "includePVVisits": True
            }
            
            # 发送查询
            query_str = json.dumps(query)
            self.input_queue.put(query_str)
            
            # 等待响应
            timeout = 30  # 30秒超时
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
                            # 可能是日志信息，继续等待
                            continue
                except Empty:
                    continue
            
            logger.warning("分析超时")
            return None
            
        except Exception as e:
            logger.error(f"分析错误: {str(e)}")
            return None
    
    def stop(self):
        """停止引擎"""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
        logger.info("KataGo Analysis引擎已停止")

class AnalysisKataGoServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS支持
        
        # 配置参数
        self.katago_binary = os.environ.get('KATAGO_BINARY', '/app/bin/katago')
        self.model_file = os.environ.get('KATAGO_MODEL', '/app/models/model.bin.gz')
        self.config_file = os.environ.get('KATAGO_CONFIG', '/app/cpp/configs/analysis_example.cfg')
        self.port = int(os.environ.get('HTTP_PORT', '8080'))
        
        logger.info(f"初始化KataGo Analysis HTTP服务器")
        logger.info(f"KataGo二进制文件: {self.katago_binary}")
        logger.info(f"模型文件: {self.model_file}")
        logger.info(f"配置文件: {self.config_file}")
        
        # 检查文件存在性
        self._check_files()
        
        # 初始化KataGo引擎
        self.engine = KataGoAnalysisEngine(
            self.katago_binary,
            self.model_file,
            self.config_file
        )
        
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
    
    def _setup_routes(self):
        """设置Flask路由"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': 'analysis-v1.0',
                'engine_running': self.engine.running
            })
        
        @self.app.route('/select-move/katago_gtp_bot', methods=['POST'])
        def select_move():
            """获取最佳走法和分析数据"""
            try:
                dtstr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                content = request.json
                
                if not content:
                    return jsonify({'error': '请求体不能为空'}), 400
                
                board_size = content.get('board_size', 19)
                moves = content.get('moves', [])
                config = content.get('config', {})
                
                logger.info(f'>>> {dtstr} select_move board_size={board_size} moves_count={len(moves)} config={config}')
                
                # KataGo Analysis模式需要[['B', 'Q16'], ['W', 'D16']]格式
                if moves and isinstance(moves[0], list) and len(moves[0]) == 2:
                    # 已经是正确的格式
                    analysis_moves = moves
                    logger.info(f'Using moves in color+position format: {analysis_moves}')
                elif moves:
                    # 如果只有位置信息，需要添加颜色信息
                    analysis_moves = []
                    for i, move in enumerate(moves):
                        color = 'B' if i % 2 == 0 else 'W'  # 黑棋先手
                        analysis_moves.append([color, move])
                    logger.info(f'Converted position-only moves to color+position format: {analysis_moves}')
                else:
                    analysis_moves = []
                
                # 调用KataGo Analysis引擎
                result = self.engine.analyze_position(board_size, analysis_moves, config)
                
                if result:
                    # 提取分析结果
                    analysis_data = result.get('moveInfos', [])
                    if analysis_data:
                        best_move = analysis_data[0].get('move', 'pass')
                        winrate = analysis_data[0].get('winrate', 0.5)
                        score = analysis_data[0].get('scoreMean', 0.0)
                        visits = analysis_data[0].get('visits', 0)
                        
                        response_data = {
                            'bot_move': best_move,
                            'winrate': winrate,
                            'score': score,
                            'visits': visits,
                            'analysis': analysis_data[:5],  # 返回前5个候选走法
                            'full_analysis': result  # 完整分析数据
                        }
                        
                        logger.info(f'<<< {dtstr} select_move response: {best_move} (winrate: {winrate:.3f}, score: {score:.1f})')
                        return jsonify(response_data)
                    else:
                        logger.warning(f'<<< {dtstr} select_move response: No analysis data')
                        return jsonify({'error': 'No analysis data available'}), 500
                else:
                    logger.warning(f'<<< {dtstr} select_move response: Analysis failed')
                    return jsonify({'error': 'Analysis failed'}), 500
                
            except Exception as e:
                error_msg = f"处理select-move请求时出错: {str(e)}"
                logger.error(error_msg)
                return jsonify({'error': error_msg}), 500
    
    def run(self):
        """启动服务器"""
        try:
            # 启动KataGo引擎
            if not self.engine.start():
                raise RuntimeError("KataGo引擎启动失败")
            
            logger.info(f"启动HTTP服务器，端口: {self.port}")
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        except Exception as e:
            logger.error(f"服务器运行错误: {str(e)}")
        finally:
            self.engine.stop()

def main():
    """主函数"""
    try:
        server = AnalysisKataGoServer()
        server.run()
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()