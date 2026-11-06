"""Cross-platform CI runners: fail visibly, test a real server, audit delivery archives."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import urlopen
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def isolated_environment():
    env=dict(os.environ)
    env.update(OPENAI_API_KEY='', TEAM_ACCESS_CODE='', PUBLIC_ORIGIN='',
               AI_AGENT_MODE='json', PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    return env


def execute(command, report, env=None):
    report=Path(report)
    report.parent.mkdir(parents=True,exist_ok=True)
    result=subprocess.run(command,cwd=ROOT,env=env or isolated_environment(),
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output=result.stdout.decode('utf-8',errors='replace')
    report.write_text(output,encoding='utf-8')
    print(output,end='',flush=True)
    return result.returncode


def audit_archive(path):
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            parts=Path(name.replace('\\','/')).parts
            leaf=parts[-1] if parts else ''
            if (set(parts)&{'.git','node_modules','runtime','..'} or
                leaf in {'config.local.json','api_config.json','.DS_Store'} or
                leaf.startswith('.env') or leaf.endswith(('.db','.sqlite','.sqlite3'))):
                raise ValueError('Private or unsafe archive entry: '+name)
        if archive.testzip():
            raise ValueError('Archive CRC failure: '+str(path))


def wait_for_site(url, timeout=20):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        try:
            with urlopen(url+'/',timeout=2) as response:
                page=response.read().decode('utf-8')
            if '<div id="root">' not in page:
                raise ValueError('Built React root is missing')
            for asset in re.findall(r'(?:src|href)="(/assets/[^"]+)"',page):
                with urlopen(url+asset,timeout=5) as response:
                    if response.status!=200 or not response.read(1):
                        raise ValueError('Built asset is unavailable')
            return
        except OSError:
            time.sleep(.15)
    raise TimeoutError('Test server did not become ready')


def integration(report):
    with tempfile.TemporaryDirectory(prefix='pysteps-ci-') as directory:
        command=[sys.executable,'-X','utf8','-u','main.py','--port','0','--db',str(Path(directory)/'learning.sqlite3')]
        proc=subprocess.Popen(command,cwd=ROOT,env=isolated_environment(),stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,text=True,encoding='utf-8')
        lines=queue.Queue()
        def reader():
            for line in proc.stdout:lines.put(line)
        threading.Thread(target=reader,daemon=True).start()
        try:
            deadline=time.monotonic()+20
            url=None
            while time.monotonic()<deadline and url is None:
                if proc.poll() is not None:
                    raise RuntimeError('main.py exited before readiness')
                try:line=lines.get(timeout=.5)
                except queue.Empty:continue
                match=re.search(r'http://127\.0\.0\.1:\d+',line)
                if match:url=match.group()
            if not url:raise TimeoutError('main.py did not report its bound port')
            wait_for_site(url)
            print('Fresh built site is ready; paid models disabled.',flush=True)
            return execute([sys.executable,'-X','utf8','scripts/verify_rebuild.py','--url',url],report)
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            if proc.stdout:proc.stdout.close()


def container_check(report):
    if not shutil.which('docker'):
        raise RuntimeError('Docker is required for the container staging check.')
    if execute(['docker','build','--tag','pysteps-ci:test','.'],Path(report).with_name('docker-build.txt')):
        return 1
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    url='http://127.0.0.1:'+str(port)
    command=['docker','run','--detach','--read-only','--tmpfs','/tmp:rw,nosuid,size=64m',
             '--publish','127.0.0.1:'+str(port)+':8000','--env','OPENAI_API_KEY=',
             '--env','TEAM_ACCESS_CODE=','--env','PUBLIC_ORIGIN='+url,'pysteps-ci:test']
    container=subprocess.check_output(command,cwd=ROOT,text=True).strip()
    try:
        wait_for_site(url,30)
        return execute([sys.executable,'-X','utf8','scripts/verify_rebuild.py','--url',url],report)
    finally:
        execute(['docker','logs',container],Path(report).with_name('container-server.txt'))
        subprocess.run(['docker','rm','--force','--volumes',container],stdout=subprocess.DEVNULL,check=False)


def package_delivery(report):
    for script,args in [('scripts/package_rebuild.py',[]),('scripts/package_submission.py',['--group','8'])]:
        code=execute([sys.executable,'-X','utf8',script,*args],Path(report).with_name(Path(script).stem+'.txt'))
        if code:return code
    archives=[ROOT/'dist/group8_project.zip',ROOT/'dist/group8_rebuild_inputs.zip']
    for path in archives:audit_archive(path)
    hashes=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in archives)
    (ROOT/'dist/SHA256SUMS.txt').write_text(hashes,encoding='utf-8')
    metadata=dict(commit=os.environ.get('GITHUB_SHA','local'),run=os.environ.get('GITHUB_RUN_ID','local'),
                  archives={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in archives})
    Path(report).parent.mkdir(parents=True,exist_ok=True)
    Path(report).write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    (ROOT/'dist/release-notes.md').write_text(
        'PySteps Group 8 verified delivery / 第8组验证交付\n\n'
        'Automated delivery for this commit. Inspect its Actions run for gate outcomes. Prereleases publish only after all gates pass. '
        'It is a deployable delivery, not a running production service.\n'
        '本交付对应当前提交。各项检查结果以Actions运行记录为准；预发布仅在全部关卡通过后创建。'
        '这是可部署交付物，尚不代表生产网站已上线。\n\nCommit: '+metadata['commit']+
        '\nRun: '+metadata['run']+'\n',encoding='utf-8')
    print('Audited delivery archives and SHA256 checksums created.')
    return 0


def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['unit','integration','container','package'])
    parser.add_argument('--report',required=True,type=Path)
    args=parser.parse_args()
    try:
        if args.stage=='unit':
            return execute([sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-t','.','-v'],args.report)
        return {'integration':integration,'container':container_check,'package':package_delivery}[args.stage](args.report)
    except Exception as error:
        message=type(error).__name__+': '+str(error)
        args.report.parent.mkdir(parents=True,exist_ok=True)
        with args.report.open('a',encoding='utf-8') as output:output.write('\n'+message+'\n')
        print(message,file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
