"""仅由 runner 在系统沙盒子进程中运行；不直接暴露CLI入口给学生。"""
import builtins
import contextlib
import io
import json
import resource
import sys
import traceback

# 在接收代码之前设置资源上限。运行器另有墙钟超时。
resource.setrlimit(resource.RLIMIT_CPU,(2,2))
resource.setrlimit(resource.RLIMIT_FSIZE,(0,0))
resource.setrlimit(resource.RLIMIT_NOFILE,(32,32))
# macOS不保证RLIMIT_DATA可用；不宣称硬内存隔离。
resource.setrlimit(resource.RLIMIT_NPROC,(0,0))

class LimitedOutput(io.StringIO):
    def write(self,text):
        if self.tell()+len(text)>8000: raise ValueError('打印输出超过8,000字符限制')
        return super().write(text)


def check_value(value):
    if type(value) in (str,int,float,bool,type(None)): return
    if type(value) is list:
        for item in value: check_value(item)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values(): check_value(item)
        return
    raise TypeError('请返回题目要求的基础值或列表；元组等类型不能代替列表')


def main():
    payload=json.loads(sys.stdin.read(100000))
    names=('abs','all','any','bool','dict','enumerate','float','int','len','list','max','min','print','range','reversed','round','sorted','str','sum','tuple','zip')
    safe={name:getattr(builtins,name) for name in names}
    output=LimitedOutput();results=[]
    try:
        program=compile(payload['source'],'student.py','exec')
        with contextlib.redirect_stdout(output):
            for args in payload['args']:
                namespace={'__builtins__':safe}
                exec(program,namespace,namespace)
                fn=namespace.get(payload['function'])
                if not callable(fn): raise ValueError('请保留题目指定的函数名称')
                value=fn(*args)
                check_value(value)
                encoded=json.dumps(value,ensure_ascii=False)
                if len(encoded)>16000: raise ValueError('返回值过大')
                results.append(value)
        reply={'status':'ok','values':results,'stdout':output.getvalue()}
    except Exception as exc:
        line=None
        for frame in traceback.extract_tb(exc.__traceback__):
            if frame.filename=='student.py': line=frame.lineno
        reply={'status':'error','error':f'{type(exc).__name__}: {str(exc)[:400]}','line':line,'stdout':output.getvalue()}
    sys.stdout.write(json.dumps(reply,ensure_ascii=False))

main()
