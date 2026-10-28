// Python runs in a disposable browser worker, never on the web server.
import { loadPyodide } from '/pyodide/pyodide.mjs';
const bootstrap = `
import json, builtins, io, contextlib, traceback
class LimitedOutput(io.StringIO):
    def write(self, text):
        if self.tell() + len(text) > 8000: raise ValueError('输出超过 8,000 字符')
        return super().write(text)
def check_value(value, depth=0):
    if depth > 30: raise ValueError('返回值嵌套过深')
    if type(value) in (str,int,float,bool,type(None)): return
    if type(value) is list:
        for item in value: check_value(item, depth+1)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values(): check_value(item, depth+1)
        return
    raise TypeError('请返回基础值或列表；元组不能代替列表')
def same_value(a,b):
    if type(a) is bool or type(b) is bool: return type(a) is type(b) and a == b
    if type(a) in (int,float) and type(b) in (int,float): return a == b
    if type(a) is not type(b): return False
    if type(a) is list: return len(a)==len(b) and all(same_value(x,y) for x,y in zip(a,b))
    if type(a) is dict: return a.keys()==b.keys() and all(same_value(a[k],b[k]) for k in a)
    return a == b
def judge(payload_json):
    payload=json.loads(payload_json); output=LimitedOutput(); rows=[]
    try:
        tree=validate_source(payload['source']); program=compile(tree, 'student.py', 'exec')
        safe={name:getattr(builtins,name) for name in SAFE_CALLS}
        with contextlib.redirect_stdout(output):
            for test in payload['tests']:
                namespace={'__builtins__':dict(safe)}
                exec(program, namespace, namespace)
                fn=namespace.get(payload['function'])
                if not callable(fn): raise ValueError('请保留题目指定的函数名称')
                value=fn(*test['args']); check_value(value)
                encoded=json.dumps(value,ensure_ascii=False)
                if len(encoded)>16000: raise ValueError('返回值过大')
                # Numeric equality is allowed, but True cannot stand in for 1.
                passed=same_value(value,test['expected'])
                rows.append({'args':test['args'],'expected':test['expected'],'actual':value,'passed':passed})
        reply={'rows':rows,'stdout':output.getvalue(),'passed':all(r['passed'] for r in rows)}
    except Exception as exc:
        line=getattr(exc,'lineno',None)
        for frame in traceback.extract_tb(exc.__traceback__):
            if frame.filename=='student.py': line=frame.lineno
        reply={'error':str(type(exc).__name__)+': '+str(exc)[:400],'line':line,'stdout':output.getvalue(),'passed':False}
    return json.dumps(reply,ensure_ascii=False)
`;
try {
 const validator=await (await fetch('/validator.py')).text();
 const py=await loadPyodide({indexURL:'/pyodide/'});
 py.runPython(validator+'\n'+bootstrap);
 // Student imports, internal attributes and indirect calls are also rejected by AST checks.
 self.fetch=()=>Promise.reject(new Error('练习期间不能访问网络'));
 self.XMLHttpRequest=undefined; self.WebSocket=undefined;
 self.postMessage({type:'ready'});
 self.onmessage=({data})=>{try{py.globals.set('payload_json',JSON.stringify(data));const result=JSON.parse(py.runPython('judge(payload_json)'));self.postMessage({type:'result',result});}catch{self.postMessage({type:'result',result:{passed:false,error:'运行失败，请检查代码后重试。'}})}};
}catch{self.postMessage({type:'init-error',error:'Python 环境加载失败，请确认项目完整解压并刷新网页。'});}
