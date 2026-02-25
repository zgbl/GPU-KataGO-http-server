#!/usr/bin/env python3

# /*********************************
# Filename: katago_gtp_bot.py
# Creation Date: Jan, 2020
# Author: AHN
# Updated: 2024 - Modernized for latest KataGo and Python 3.10+
# **********************************/
#
# A wrapper around a KataGo process to use it in a REST service.
# For use from a website where people can play KataGo.
# Supports modern KataGo versions with improved error handling and logging.
#

import os
import sys
import re
import signal
import time
import logging
import subprocess
from threading import Thread, Lock, Event
import atexit
from typing import List, Dict, Optional, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局变量 - 用于线程间通信
g_response: Optional[str] = None
g_handler_lock = Lock()
g_response_event = Event()
g_win_prob: float = -1.0
g_score: float = 0.0
g_bot_move: str = ''
g_best_ten: List[Dict[str, Any]] = []

# 配置常量
MOVE_TIMEOUT = 30  # 增加超时时间以适应现代 KataGo
DEFAULT_KOMI = 7.5
MIN_BOARD_SIZE = 9
MAX_BOARD_SIZE = 25
#===========================
class KataGTPBot:
    # Listen on a stream in a separate thread until
    # a line comes in. Process line in a callback.
    #=================================================
    class Listener:
        #------------------------------------------------------------
        def __init__( self, stream, result_handler, error_handler):
            self.stream = stream
            self.result_handler = result_handler

            #--------------------------------------
            def wait_for_line( stream, callback):
                while True:
                    line = stream.readline().decode()
                    if line:
                        result_handler( line)
                    else: # probably my process died
                        error_handler()
                        break

            self.thread = Thread( target = wait_for_line,
                                  args = (self.stream, self.result_handler))
            self.thread.daemon = True
            self.thread.start()

    def __init__(self, katago_cmdline: List[str]):
        """初始化 KataGo GTP Bot
        
        Args:
            katago_cmdline: KataGo 启动命令行参数列表
        """
        self.katago_cmdline = katago_cmdline
        self.last_move_color = ''
        self.is_alive = False
        
        logger.info(f"Initializing KataGo with command: {' '.join(katago_cmdline)}")
        
        try:
            self.katago_proc, self.katago_listener = self._start_katagoproc()
            self.is_alive = True
            atexit.register(self._kill_katago)
            logger.info("KataGo process started successfully")
        except Exception as e:
            logger.error(f"Failed to start KataGo process: {e}")
            raise

    def _start_katagoproc(self):
        """启动 KataGo 进程"""
        try:
            # 使用更安全的进程启动方式
            proc = subprocess.Popen(
                self.katago_cmdline,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                universal_newlines=False,  # 使用字节模式
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            listener = KataGTPBot.Listener(
                proc.stdout,
                self._result_handler,
                self._error_handler
            )
            
            # 等待进程启动
            time.sleep(1)
            if proc.poll() is not None:
                raise RuntimeError(f"KataGo process exited immediately with code {proc.returncode}")
            
            return proc, listener
            
        except Exception as e:
            logger.error(f"Error starting KataGo process: {e}")
            raise

    def _kill_katago(self):
        """安全地终止 KataGo 进程"""
        if hasattr(self, 'katago_proc') and self.katago_proc:
            try:
                if self.katago_proc.poll() is None:  # 进程仍在运行
                    logger.info("Terminating KataGo process")
                    if os.name == 'nt':  # Windows
                        self.katago_proc.terminate()
                    else:  # Unix-like
                        os.kill(self.katago_proc.pid, signal.SIGTERM)
                    
                    # 等待进程优雅退出
                    try:
                        self.katago_proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning("KataGo process did not terminate gracefully, forcing kill")
                        if os.name == 'nt':
                            self.katago_proc.kill()
                        else:
                            os.kill(self.katago_proc.pid, signal.SIGKILL)
                        
                self.is_alive = False
                logger.info("KataGo process terminated")
                
            except Exception as e:
                logger.error(f"Error killing KataGo process: {e}")

    def _result_handler(self, katago_response: str):
        """解析 KataGo 响应并触发事件继续执行
        
        Args:
            katago_response: KataGo 的原始响应字符串
        """
        global g_response, g_response_event, g_win_prob, g_score, g_bot_move, g_best_ten

        line = katago_response.strip()
        if not line:
            return
            
        logger.debug(f"KataGo response: {line}")
        
        try:
            # 处理胜率和分数信息 (CHAT/MALKOVICH 格式)
            if g_win_prob < 0 and ('CHAT:' in line or 'MALKOVICH:' in line):
                logger.debug(f"Processing winrate line: {line}")
                g_best_ten = []
                
                # 解析胜率
                winrate_match = re.search(r'Winrate\s+([\d.]+)%', line)
                if winrate_match:
                    g_win_prob = float(winrate_match.group(1)) * 0.01
                    
                # 解析分数领先
                score_match = re.search(r'ScoreLead\s+([-\d.]+)', line)
                if score_match:
                    g_score = float(score_match.group(1))
                    
            # 处理 KataGo 内部日志
            elif '@@' in line:
                logger.info(f"KataGo log: {line}")
                
            # 处理 GTP 响应
            elif line.startswith('='):
                resp = line.split('=', 1)[1].strip()
                if resp:
                    logger.debug(f"GTP response: {resp}")
                    g_response = resp
                    if g_response:
                        g_response_event.set()
                        
            # 处理候选走法 (PSV 格式)
            elif ' PSV ' in line:
                try:
                    psv_match = re.search(r'PSV\s+(\d+)', line)
                    move_match = re.search(r'^([A-Z]\d+)', line)
                    
                    if psv_match and move_match:
                        psv = int(psv_match.group(1))
                        move = move_match.group(1)
                        g_best_ten.append({'move': move, 'psv': psv})
                        
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse PSV line: {line}, error: {e}")
                    
            # 处理 kata-analyze 响应
            elif line.startswith('info '):
                try:
                    self._katagoCmd('stop')
                    
                    # 解析胜率 (现代格式)
                    winrate_match = re.search(r'winrate\s+([\d.]+)', line)
                    if winrate_match:
                        g_win_prob = float(winrate_match.group(1))
                        
                    # 解析分数领先
                    score_match = re.search(r'scoreLead\s+([-\d.]+)', line)
                    if score_match:
                        g_score = float(score_match.group(1))
                        
                    # 解析最佳走法
                    move_match = re.search(r'\s+move\s+([A-Z]\d+|pass)', line)
                    if move_match:
                        g_bot_move = move_match.group(1)
                        
                    g_response = line
                    g_response_event.set()
                    
                except Exception as e:
                    logger.error(f"Error parsing kata-analyze response: {e}")
                    
            # 处理错误响应
            elif line.startswith('?'):
                error_msg = line.split('?', 1)[1].strip() if '?' in line else line
                logger.error(f"KataGo error: {error_msg}")
                g_response = line
                g_response_event.set()
                
        except Exception as e:
            logger.error(f"Error in result handler: {e}, line: {line}")

    def _error_handler(self):
        """处理 KataGo 进程死亡，尝试重启"""
        global g_handler_lock
        
        with g_handler_lock:
            logger.warning("KataGo process died, attempting to resurrect")
            
            try:
                self._kill_katago()
                time.sleep(2)  # 等待清理完成
                
                self.katago_proc, self.katago_listener = self._start_katagoproc()
                self.is_alive = True
                
                # 等待进程稳定
                time.sleep(3)
                
                if self.katago_proc.poll() is None:
                    logger.info("KataGo process successfully resurrected")
                else:
                    logger.error("Failed to resurrect KataGo process")
                    self.is_alive = False
                    
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
                self.is_alive = False

    def _katagoCmd(self, cmdstr: str):
        """向 KataGo 发送命令
        
        Args:
            cmdstr: 要发送的 GTP 命令字符串
        """
        if not self.is_alive or not self.katago_proc:
            logger.error("Cannot send command: KataGo process is not alive")
            return False
            
        try:
            logger.debug(f"Sending command: {cmdstr}")
            
            # 确保命令以换行符结尾
            if not cmdstr.endswith('\n'):
                cmdstr += '\n'
                
            # 发送命令
            self.katago_proc.stdin.write(cmdstr.encode('utf-8'))
            self.katago_proc.stdin.flush()
            
            return True
            
        except (BrokenPipeError, OSError) as e:
            logger.error(f"Error sending command to KataGo: {e}")
            self._error_handler()
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending command: {e}")
            return False

    def select_move(self, moves: List[str], config: Dict[str, Any] = None) -> Optional[str]:
        """选择下一步走法
        
        Args:
            moves: 已下走法列表
            config: 配置参数字典
            
        Returns:
            下一步走法字符串，失败时返回 None
        """
        if config is None:
            config = {}
            
        global g_win_prob, g_response, g_response_event
        
        # 参数验证
        if not isinstance(moves, list):
            logger.error("Moves must be a list")
            return None
            
        if not self.is_alive:
            logger.error("KataGo process is not alive")
            return None
            
        logger.info(f"Selecting move for {len(moves)} moves")
        
        try:
            # 重置全局状态
            g_win_prob = -1.0
            g_response = None
            
            # 设置贴目
            komi = config.get('komi', DEFAULT_KOMI)
            if not self.set_komi(komi):
                logger.error("Failed to set komi")
                return None

            # 重置游戏状态
            if not self._katagoCmd('clear_board'):
                return None
            if not self._katagoCmd('clear_cache'):
                return None

            # 设置规则
            if not self.set_rules(komi, config):
                return None

            # 执行走法
            color = 'b'
            for idx, move in enumerate(moves):
                # 验证走法格式
                if not self._validate_move(move):
                    logger.error(f"Invalid move format: {move}")
                    return None
                    
                # 早期的 pass 可能会影响中国规则的贴目计算
                if move != 'pass' or idx > 20:
                    if not self._katagoCmd(f'play {color} {move}'):
                        return None
                        
                color = 'w' if color == 'b' else 'b'

            # 请求新走法
            self.last_move_color = color
            cmd = f'genmove {color}'
            
            if not self._katagoCmd(cmd):
                return None
                
            # 等待响应
            logger.debug("Waiting for move response")
            success = g_response_event.wait(MOVE_TIMEOUT)
            g_response_event.clear()
            
            if not success:
                logger.error("KataGo select move response timeout")
                self._error_handler()
                return None
                
            result = g_response
            g_response = None
            
            if result:
                logger.info(f"KataGo selected move: {result}")
                return result
            else:
                logger.error("No response from KataGo")
                return None
                
        except Exception as e:
            logger.error(f"Error in select_move: {e}")
            return None
            
    def _validate_move(self, move: str) -> bool:
        """验证走法格式
        
        Args:
            move: 走法字符串
            
        Returns:
            是否为有效走法
        """
        if not isinstance(move, str):
            return False
            
        move = move.strip().lower()
        
        # pass 是有效走法
        if move == 'pass':
            return True
            
        # 检查坐标格式 (如 A1, B2, T19)
        if re.match(r'^[a-t]([1-9]|1[0-9]|2[0-5])$', move):
            return True
            
        return False

    def score(self, moves: List[str], config: Dict[str, Any] = None) -> Optional[List[float]]:
        """获取局面评估和所有权信息
        
        Args:
            moves: 已下走法列表
            config: 配置参数字典
            
        Returns:
            所有权概率列表，失败时返回 None
        """
        if config is None:
            config = {}
            
        global g_response, g_response_event
        
        # 参数验证
        if not isinstance(moves, list):
            logger.error("Moves must be a list")
            return None
            
        if not self.is_alive:
            logger.error("KataGo process is not alive")
            return None
            
        logger.info(f"Scoring position with {len(moves)} moves")
        
        try:
            # 重置响应状态
            g_response = None
            
            # 获取配置
            ownership = config.get('ownership', 'true')
            komi = config.get('komi', DEFAULT_KOMI)
            
            # 设置贴目
            if not self.set_komi(komi):
                logger.error("Failed to set komi")
                return None

            # 重置游戏状态
            if not self._katagoCmd('clear_board'):
                return None
            if not self._katagoCmd('clear_cache'):
                return None

            # 设置规则
            if not self.set_rules(komi, config):
                return None

            # 执行走法
            color = 'b'
            for idx, move in enumerate(moves):
                # 验证走法格式
                if not self._validate_move(move):
                    logger.error(f"Invalid move format: {move}")
                    return None
                    
                # 早期的 pass 可能会影响中国规则的贴目计算
                if move != 'pass' or idx > 20:
                    if not self._katagoCmd(f'play {color} {move}'):
                        return None
                        
                color = 'w' if color == 'b' else 'b'

            # 请求所有权信息
            analyze_cmd = f'kata-analyze 100 ownership {ownership}'
            if not self._katagoCmd(analyze_cmd):
                return None
                
            # 等待响应
            logger.debug("Waiting for score response")
            success = g_response_event.wait(MOVE_TIMEOUT)
            g_response_event.clear()
            
            if not success:
                logger.error("KataGo score response timeout")
                self._error_handler()
                return None
                
            if not g_response:
                logger.error("No score response from KataGo")
                return None
                
            logger.debug(f"Score response: {g_response}")
            
            # 解析所有权信息
            result = []
            if ownership == 'true' and 'ownership' in g_response:
                try:
                    ownership_part = g_response.split('ownership')[1]
                    ownership_values = ownership_part.split()
                    
                    # 转换为浮点数列表
                    result = [float(val) for val in ownership_values if self._is_float(val)]
                    
                    logger.info(f"Parsed {len(result)} ownership values")
                    
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing ownership data: {e}")
                    return None
                    
            g_response = None
            return result
            
        except Exception as e:
            logger.error(f"Error in score: {e}")
            return None
            
    def _is_float(self, value: str) -> bool:
        """检查字符串是否可以转换为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def set_rules(self, komi: float, config: Dict[str, Any] = None) -> bool:
        """设置围棋规则
        
        Args:
            komi: 贴目值
            config: 配置参数字典
            
        Returns:
            是否设置成功
        """
        if config is None:
            config = {}
            
        try:
            if not komi:
                komi = 0
                
            # 根据贴目值选择规则
            # 整数贴目或偶数贴目使用日本规则，奇数贴目使用中国规则
            rules = 'japanese'
            if komi != int(komi):  # 贴目为 n.5
                if (komi - 0.5) % 2:  # 7.5, 不是 6.5
                    rules = 'chinese'
                    
            # Kifu Cam 总是使用中国规则
            if config.get('client', '') == 'kifucam':
                rules = 'chinese'
                
            # 允许通过配置强制指定规则
            if 'rules' in config:
                rules = config['rules']
                
            logger.debug(f"Setting rules to: {rules}")
            return self._katagoCmd(f'kata-set-rules {rules}')
            
        except Exception as e:
            logger.error(f"Error setting rules: {e}")
            return False

    def set_komi(self, komi: float) -> bool:
        """设置贴目值
        
        Args:
            komi: 贴目值
            
        Returns:
            是否设置成功
        """
        try:
            if not komi:
                komi = 0
                
            # 验证贴目值范围
            if komi < 0 or komi > 20:
                logger.warning(f"Unusual komi value: {komi}")
                
            logger.debug(f"Setting komi to: {komi}")
            return self._katagoCmd(f'komi {komi:.1f}')
            
        except Exception as e:
            logger.error(f"Error setting komi: {e}")
            return False

    def diagnostics(self) -> Dict[str, Any]:
        """获取诊断信息
        
        Returns:
            包含胜率、分数、最佳走法等信息的字典
        """
        global g_win_prob, g_score, g_bot_move, g_best_ten
        
        try:
            return {
                'winprob': float(g_win_prob) if g_win_prob >= 0 else None,
                'score': float(g_score),
                'bot_move': g_bot_move,
                'best_ten': g_best_ten.copy(),  # 返回副本以避免外部修改
                'is_alive': self.is_alive,
                'last_move_color': self.last_move_color
            }
        except Exception as e:
            logger.error(f"Error getting diagnostics: {e}")
            return {
                'winprob': None,
                'score': 0.0,
                'bot_move': '',
                'best_ten': [],
                'is_alive': False,
                'last_move_color': ''
            }
