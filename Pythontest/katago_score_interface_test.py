#!/usr/bin/env python3
import subprocess
import json
import tempfile
import os

def test_direct_katago():
    """尝试直接调用KataGo命令行工具进行分析"""
    print("=" * 80)
    print("直接调用KataGo分析测试")
    print("=" * 80)
    
    # 创建一个简单的SGF文件
    sgf_content = """(;FF[4]CA[UTF-8]AP[Test]SZ[19]KM[7.5]RU[Chinese]
;B[pd];W[dd];B[pq];W[dq])"""
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sgf', delete=False) as f:
        f.write(sgf_content)
        sgf_file = f.name
    
    try:
        # 尝试不同的KataGo命令
        katago_commands = [
            # Docker内的路径
            ["/app/bin/katago", "analysis", "-config", "/app/katago_gtp.cfg", "-model", "/app/model.bin.gz"],
            # 可能的系统路径
            ["katago", "analysis"],
            ["./katago", "analysis"],
            # Windows路径
            ["katago.exe", "analysis"]
        ]
        
        analysis_input = {
            "id": "test",
            "initialStones": [],
            "moves": [["B", "Q16"], ["W", "D4"], ["B", "Q3"], ["W", "D16"]],
            "rules": "chinese",
            "komi": 7.5,
            "boardXSize": 19,
            "boardYSize": 19,
            "maxVisits": 1000,
            "includeOwnership": True,
            "includePolicy": True,
            "includePVVisits": True
        }
        
        input_json = json.dumps(analysis_input) + "\n"
        
        for cmd in katago_commands:
            print(f"\n尝试命令: {' '.join(cmd)}")
            
            try:
                # 检查命令是否存在
                result = subprocess.run(
                    cmd + ["-help"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                if result.returncode == 0 or "katago" in result.stdout.lower():
                    print("✅ KataGo可执行文件找到")
                    
                    # 尝试分析
                    print("发送分析请求...")
                    process = subprocess.run(
                        cmd,
                        input=input_json,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if process.returncode == 0:
                        print("✅ 分析成功")
                        print("输出:")
                        print(process.stdout)
                        return True
                    else:
                        print(f"❌ 分析失败，返回码: {process.returncode}")
                        print(f"错误: {process.stderr}")
                else:
                    print("❌ 不是KataGo可执行文件")
                    
            except FileNotFoundError:
                print("❌ 命令未找到")
            except subprocess.TimeoutExpired:
                print("❌ 命令超时")
            except Exception as e:
                print(f"❌ 异常: {e}")
        
        return False
        
    finally:
        # 清理临时文件
        try:
            os.unlink(sgf_file)
        except:
            pass

def check_docker_environment():
    """检查是否在Docker环境中，以及KataGo的安装情况"""
    print("\n" + "=" * 80)
    print("环境检查")
    print("=" * 80)
    
    # 检查Docker环境
    docker_indicators = [
        "/.dockerenv",
        "/proc/1/cgroup"
    ]
    
    in_docker = False
    for indicator in docker_indicators:
        if os.path.exists(indicator):
            in_docker = True
            print(f"✅ Docker环境指示器发现: {indicator}")
            break
    
    if not in_docker:
        print("❌ 似乎不在Docker环境中")
    
    # 检查KataGo相关文件
    katago_files = [
        "/app/bin/katago",
        "/app/katago_gtp.cfg", 
        "/app/model.bin.gz",
        "./katago",
        "./katago.exe",
        "katago_gtp.cfg",
        "model.bin.gz"
    ]
    
    print(f"\nKataGo文件检查:")
    for file_path in katago_files:
        if os.path.exists(file_path):
            print(f"✅ 找到: {file_path}")
            try:
                stat = os.stat(file_path)
                print(f"   大小: {stat.st_size} bytes")
                print(f"   可执行: {os.access(file_path, os.X_OK)}")
            except:
                pass
        else:
            print(f"❌ 未找到: {file_path}")
    
    # 检查环境变量
    print(f"\n环境变量:")
    env_vars = ["PATH", "KATAGO_MODEL", "KATAGO_CONFIG"]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")

def suggest_solutions():
    """根据测试结果提供解决方案建议"""
    print("\n" + "=" * 80)
    print("🔧 解决方案建议")
    print("=" * 80)
    
    solutions = [
        {
            "问题": "HTTP服务器功能有限",
            "解决方案": [
                "1. 检查HTTP服务器的源代码，确认是否支持分析功能",
                "2. 查看服务器启动参数和配置文件",
                "3. 尝试直接使用KataGo命令行工具"
            ]
        },
        {
            "问题": "参数传递不正确",
            "解决方案": [
                "1. 查看HTTP服务器的API文档",
                "2. 检查服务器日志了解参数处理情况",
                "3. 尝试不同的参数格式和命名"
            ]
        },
        {
            "问题": "KataGo配置问题",
            "解决方案": [
                "1. 检查katago_gtp.cfg配置文件",
                "2. 确认模型文件是否正确加载",
                "3. 验证KataGo版本是否支持所需功能"
            ]
        },
        {
            "问题": "需要自定义实现",
            "解决方案": [
                "1. 直接调用KataGo analysis命令",
                "2. 修改现有HTTP服务器添加分析功能",
                "3. 使用其他KataGo HTTP包装器"
            ]
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['问题']}")
        for step in solution['解决方案']:
            print(f"   {step}")

if __name__ == "__main__":
    check_docker_environment()
    test_direct_katago()
    suggest_solutions()
    
    print(f"\n📋 下一步行动:")
    print(f"1. 运行 /score 接口测试脚本")
    print(f"2. 检查HTTP服务器源代码")
    print(f"3. 查看服务器启动日志")
    print(f"4. 考虑直接使用KataGo命令行接口")