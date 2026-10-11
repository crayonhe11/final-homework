import unittest, tempfile, os, json
from pathlib import Path
from datetime import datetime,timezone,timedelta
from edu.coding import load_tasks,validate_source
from edu.runner import run_code,same_value
from edu.storage import Store
from edu.charts import daily_metrics

class CodingTests(unittest.TestCase):
    def test_specs_and_solutions_parse(self):
        tasks=load_tasks();self.assertEqual(len(tasks),6)
        for t in tasks.values(): validate_source(t['solution']);self.assertGreaterEqual(len(t['tests']),6)
    def test_reject_unsafe(self):
        for code in ['import os','open("x")','eval("1")','().__class__','getattr(1,"real")','class X: pass','f = lambda: 1','print.__globals__']:
            with self.subTest(code=code),self.assertRaises(ValueError): validate_source(code)
    def test_syntax_line(self):
        r=run_code(next(iter(load_tasks().values())),'def x(:');self.assertEqual(r['status'],'syntax_error');self.assertEqual(r['line'],1)
    def test_nested_types(self):
        self.assertFalse(same_value([True],[1]));self.assertTrue(same_value([3,2,1],[3,2,1]))
    def test_draft_and_records(self):
        with tempfile.TemporaryDirectory() as d:
            s=Store(Path(d)/'db');self.assertIsNone(s.get_draft('a'));s.save_draft('a','hello');s.save_draft('a','');self.assertEqual(s.get_draft('a'),'')
            s.save_code_attempt('a','def x(): pass','submit',{'passed':False,'status':'ok'});self.assertEqual(len(s.code_history()),1);self.assertEqual(s.history(),[])
    def test_metrics_date_gaps_filters(self):
        now=datetime(2026,10,3,12,tzinfo=timezone(timedelta(hours=8)))
        h=[{'question_id':'q','correct':1,'created_at':'2026-10-02T18:00:00+00:00'}]
        code=[{'task_id':'t','mode':m,'passed':1,'result_json':json.dumps({'status':status}),'created_at':now.isoformat()} for m,status in [('example','ok'),('submit','ok'),('submit','unavailable')]]
        bank={'q':{'topic':'循环'}};tasks={'t':{'topic':'循环'}}
        r=daily_metrics(h,code,bank,tasks,7,now=now)
        self.assertIsNone(r[-2]['accuracy']);self.assertEqual(r[-1]['accuracy'],100);self.assertEqual(r[-1]['submissions'],1)
        self.assertEqual(sum(x['questions'] for x in daily_metrics(h,code,bank,tasks,7,'条件判断',now)),0)

@unittest.skipUnless(os.getenv('EDU_RUN_SANDBOX_TESTS')=='1','需在macOS隔离可用环境显式运行')
class SandboxTests(unittest.TestCase):
    def test_reference_solutions(self):
        for t in load_tasks().values():
            with self.subTest(task=t['id']): self.assertTrue(run_code(t,t['solution'])['passed'])
    def test_wrong_print_and_loop(self):
        t=load_tasks()['rocket_countdown']
        self.assertFalse(run_code(t,'def countdown(start):\n    return []')['passed'])
        self.assertFalse(run_code(t,'def countdown(start):\n    return tuple(range(start,0,-1))')['passed'])
        self.assertFalse(run_code(t,'def countdown(start):\n    print(list(range(start,0,-1)))')['passed'])
        self.assertIn(run_code(t,'def countdown(start):\n    while True:\n        pass',timeout=.3)['status'],('timeout','resource_limit'))
    def test_system_file_network_boundary(self):
        import subprocess,sys
        from edu.runner import PROFILE,SANDBOX
        with tempfile.TemporaryDirectory() as d:
            canary=Path(d)/'canary';canary.write_text('test-only')
            scripts=[f'open({str(canary)!r}).read()',f'open({str(canary)!r},"w").write("changed")','import socket; socket.socket().bind(("127.0.0.1",0))']
            for script in scripts:
                r=subprocess.run([SANDBOX,'-p',PROFILE,sys.executable,'-I','-S','-c',script],cwd='/',capture_output=True,text=True,timeout=4)
                self.assertNotEqual(r.returncode,0);self.assertIn('PermissionError',r.stderr)
            self.assertEqual(canary.read_text(),'test-only')
