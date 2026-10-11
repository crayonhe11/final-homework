"""受控判题：macOS系统沙盒；Windows/Linux Docker。隔离不可用时拒绝执行。"""
import json
import os
import platform
import signal
import subprocess
import sys
import time
import shutil
from pathlib import Path
from .coding import validate_source
from .docker_runner import run_container

SANDBOX='/usr/bin/sandbox-exec'
PROFILE='''(version 1)
(allow default)
(deny network*)
(deny file-write*)
(deny file-read-data (subpath "/Users") (subpath "/private") (subpath "/Volumes")
 (subpath "/tmp") (subpath "/var") (subpath "/etc") (subpath "/opt"))
'''


def runner_backend():
    choice=os.environ.get('EDU_CODE_BACKEND','auto').lower()
    if choice not in ('auto','native','docker'): return None
    if choice!='docker' and platform.system()=='Darwin' and Path(SANDBOX).exists(): return 'native'
    if choice!='native' and shutil.which('docker'): return 'docker'
    return None


def supports_runner():
    # 仅表示执行工具存在，不能据此断言Docker服务、镜像或系统沙盒已可用。
    return runner_backend() is not None


def run_code(task,source,mode='submit',timeout=4):
    if mode not in ('example','submit'): raise ValueError('未知判题模式')
    try: validate_source(source)
    except SyntaxError as exc:
        return {'status':'syntax_error','error':exc.msg,'line':exc.lineno,'passed':False,'cases':[]}
    except (ValueError,RecursionError) as exc:
        return {'status':'restricted','error':str(exc),'passed':False,'cases':[]}
    backend=runner_backend()
    if backend is None:
        return {'status':'unavailable','error':'判题隔离环境未准备好。Windows/Linux需要Docker；请运行 python tools/check_environment.py。可编辑和保存，暂不执行代码。','passed':False,'cases':[]}
    cases=task['tests'][:2] if mode=='example' else task['tests']
    payload={'source':source,'function':task['function'],'args':[c['args'] for c in cases]}
    worker=(Path(__file__).parent/'coding_worker.py').read_text(encoding='utf-8')
    env={'PATH':'/usr/bin:/bin','LANG':'en_US.UTF-8','PYTHONIOENCODING':'utf-8'}
    try:
        if backend=='docker':
            execution=run_container(worker,json.dumps(payload,ensure_ascii=False),timeout)
            if 'error_status' in execution:
                return {'status':execution['error_status'],'error':execution['error'],'passed':False,'cases':[]}
            returncode=execution['returncode'];stdout=execution['stdout'];stderr=execution['stderr']
        else:
            process=subprocess.Popen([SANDBOX,'-p',PROFILE,sys.executable,'-I','-S','-B','-c',worker],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',
                cwd='/',env=env,start_new_session=True)
            deadline=time.monotonic()+timeout
            incoming=json.dumps(payload,ensure_ascii=False)
            while True:
                try:
                    stdout,stderr=process.communicate(incoming,timeout=min(.05,max(.001,deadline-time.monotonic())))
                    break
                except subprocess.TimeoutExpired:
                    incoming=None
                    # macOS不提供可靠的Python硬内存配额；这里是轮询保护，仍不适合公开不可信判题服务。
                    try:
                        usage=subprocess.run(['/bin/ps','-o','rss=','-p',str(process.pid)],capture_output=True,text=True,timeout=.2)
                        memory_exceeded=int(usage.stdout.strip() or '0')>256*1024
                    except (ValueError,OSError,subprocess.TimeoutExpired): memory_exceeded=False
                    timed_out=time.monotonic()>=deadline
                    if memory_exceeded or timed_out:
                        try: os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                        process.communicate()
                        return {'status':'resource_limit' if memory_exceeded else 'timeout',
                                'error':'运行超过内存保护阈值。' if memory_exceeded else '运行超过时间限制，请检查循环是否会结束。',
                                'passed':False,'cases':[]}
            returncode=process.returncode
        if returncode:
            status='unavailable' if 'sandbox_apply' in stderr or (backend=='docker' and returncode in (1,125,126,127)) else 'resource_limit'
            return {'status':status,'error':'系统隔离不可用，执行已停止。' if status=='unavailable' else '进程超过资源限制或异常退出，请简化计算。','passed':False,'cases':[]}
        if len(stdout)>150000: raise ValueError('判题结果过长')
        result=json.loads(stdout)
        if result['status']!='ok': return {**result,'passed':False,'cases':[]}
        if len(result['values'])!=len(cases): raise ValueError('返回数量不匹配')
        outcomes=[]
        for case,actual in zip(cases,result['values']):
            expected=case['expected']
            passed=same_value(actual,expected)
            outcomes.append({'args':case['args'],'expected':expected,'actual':actual,'passed':passed})
        return {'status':'ok','passed':all(c['passed'] for c in outcomes),'cases':outcomes,
                'stdout':result.get('stdout',''),'mode':mode}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'status':'unavailable','error':'判题环境未能正常运行：'+str(exc)[:200],'passed':False,'cases':[]}


def same_value(actual, expected):
    if type(actual) is not type(expected): return False
    if isinstance(expected,list):
        return len(actual)==len(expected) and all(same_value(a,b) for a,b in zip(actual,expected))
    if isinstance(expected,dict):
        return actual.keys()==expected.keys() and all(same_value(actual[k],expected[k]) for k in expected)
    return actual==expected
