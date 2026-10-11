"""只检查环境，不读密钥、不下载、不运行学生代码。"""
import argparse,platform,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.runner import runner_backend
from edu.docker_runner import IMAGE,docker_environment


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--docker',action='store_true',help='检查Docker后端，即使本机为macOS')
    args=parser.parse_args()
    print('操作系统：'+platform.system());print('Python：'+platform.python_version())
    try: import tkinter
    except ImportError: print('图形界面缺少Tkinter，请按跨平台说明安装。')
    else: print('Tkinter模块可导入；图形会话是否可用需实际启动程序检查。')
    backend='docker' if args.docker else runner_backend()
    if backend=='native':
        print('可使用macOS系统沙盒；实际是否可运行请在编程区运行示例。');return
    docker=shutil.which('docker')
    if not docker:
        print('未检测到Docker：选择题/AI可用，代码判题需安装并启动Docker。');raise SystemExit(1)
    try:
        result=subprocess.run([docker,'info','--format','{{.OSType}}'],capture_output=True,text=True,timeout=8,env=docker_environment())
        if result.returncode or result.stdout.strip()!='linux':
            print('Docker服务不可用，或当前不是Linux容器模式。');raise SystemExit(1)
        result=subprocess.run([docker,'image','inspect',IMAGE],capture_output=True,text=True,timeout=8,env=docker_environment())
        if result.returncode:
            print('请先下载执行镜像：docker pull '+IMAGE);raise SystemExit(1)
        print('Docker Linux服务与镜像可用。可在编程区运行示例，完成实际判题验收。')
    except (OSError,subprocess.TimeoutExpired):
        print('Docker检查失败或超时，请启动Docker后重试。');raise SystemExit(1)

if __name__=='__main__': main()
