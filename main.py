"""INT6181 entry point: python main.py. Python 3.10+, standard library only."""
import argparse
from pathlib import Path
import webbrowser
from backend.domain import ROOT
from backend.server import create_server

def main(argv=None):
    parser = argparse.ArgumentParser(description='PySteps Python 学习系统：启动本机网页，无需Node.js')
    parser.add_argument('--host', default='127.0.0.1', help='默认仅本机；部署可设为0.0.0.0')
    parser.add_argument('--port', type=int, default=8010)
    parser.add_argument('--db', type=Path, default=ROOT / 'runtime/learning.sqlite3')
    parser.add_argument('--open', action='store_true', help='启动后打开浏览器')
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error('端口应在0至65535之间')
    if not (ROOT / 'web/static/index.html').is_file():
        parser.error('缺少随作业提交的网页文件，请完整解压项目。开发者可运行网页构建脚本。')
    try:
        server = create_server(args.host, args.port, args.db)
    except OSError as error:
        parser.error(f'启动失败，请检查端口占用和数据库目录权限：{error}')
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'PySteps 已启动：{url}\n使用Python标准库运行；按Ctrl+C停止。', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止。学习记录已保存在SQLite。')
    finally:
        server.server_close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
