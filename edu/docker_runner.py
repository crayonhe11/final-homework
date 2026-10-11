"""Windows/Linux共用的Linux容器执行后端；不挂载宿主目录，不转发API密钥。"""
import os
import shutil
import subprocess
import uuid

IMAGE='python:3.13-slim'


def docker_environment():
    keys={'PATH','HOME','USERPROFILE','SystemRoot','SYSTEMROOT','WINDIR','APPDATA','LOCALAPPDATA','TEMP','TMP',
          'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_CONFIG','DOCKER_CERT_PATH','DOCKER_TLS_VERIFY'}
    return {k:v for k,v in os.environ.items() if k in keys}


def create_command(executable,name,worker):
    return [executable,'create','--name',name,'--pull','never','--interactive',
            '--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true',
            '--memory','128m','--memory-swap','128m','--cpus','1','--pids-limit','32',
            '--user','65534:65534','--ipc','none','--log-driver','none','--workdir','/tmp',
            IMAGE,'python','-I','-S','-B','-c',worker]


def run_container(worker,payload,timeout):
    executable=shutil.which('docker')
    if not executable:
        return {'error_status':'unavailable','error':'代码运行需要Docker。Windows请安装并启动Docker Desktop（Linux容器模式）；Linux请启动Docker Engine。详见“跨平台使用说明”。'}
    env=docker_environment();name='edu-python-'+uuid.uuid4().hex
    process=None;result=None;cleanup_failed=False
    try:
        created=subprocess.run(create_command(executable,name,worker),capture_output=True,text=True,
                               encoding='utf-8',errors='replace',env=env,timeout=12)
        if created.returncode:
            result={'error_status':'unavailable','error':'Docker或Python镜像尚未准备好。请运行 python tools/check_environment.py 检查；程序没有执行学生代码。'}
        else:
            process=subprocess.Popen([executable,'start','--attach','--interactive',name],stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',env=env)
            try:
                stdout,stderr=process.communicate(payload,timeout=timeout)
                result={'returncode':process.returncode,'stdout':stdout,'stderr':stderr}
            except subprocess.TimeoutExpired:
                result={'error_status':'timeout','error':'运行超过时间限制，请检查循环是否结束。'}
    except subprocess.TimeoutExpired:
        result={'error_status':'unavailable','error':'Docker启动超时，请确认Docker服务正在运行。'}
    except OSError:
        result={'error_status':'unavailable','error':'无法启动Docker，请检查安装与权限。'}
    finally:
        # 仅清理本次随机命名的容器；停止容器后再停止附着的CLI，避免遗留学生进程。
        try:
            cleanup=subprocess.run([executable,'rm','--force',name],capture_output=True,text=True,
                                   encoding='utf-8',errors='replace',env=env,timeout=5)
            cleanup_failed=cleanup.returncode!=0 and 'No such container' not in cleanup.stderr
        except (OSError,subprocess.TimeoutExpired): cleanup_failed=True
        if process is not None and process.poll() is None:
            process.kill()
            try: process.communicate(timeout=2)
            except subprocess.TimeoutExpired: cleanup_failed=True
    if cleanup_failed:
        return {'error_status':'unavailable','error':'Docker未确认清理完成。请重启Docker并检查本次容器：'+name}
    return result
