"""Acceptance-focused tests. All model responses are simulated; no paid API calls."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from backend.domain import LearningEngine, empty_state, ROOT
from backend.storage import Store, ConflictError
from backend.ai import analyze, validate_output

E = LearningEngine()
def attempt(q, choice=None, at='2026-10-01T00:00:00Z', hints=0, course=True, ident=None):
    grade=E.grade(q['id'], choice or q['answer'])
    return dict(id=ident or q['id'], question_id=q['id'], choice=choice or q['answer'],reason='我以为边界不包含相等',correct=grade['correct'],diagnosis=grade['feedback']['concept'],created_at=at,hints_used=hints,course_concept=q['concept'] if course else None,feedback=grade['feedback'])

class LearningTests(unittest.TestCase):
    def test_all_question_answers(self):
        # Only repository-owned reviewed snippets are executed, never learner code.
        import subprocess, sys
        for q in E.questions:
            with self.subTest(question=q['id']):
                # -I ignores PYTHON* environment variables; enable child UTF-8 explicitly.
                result=subprocess.run([sys.executable,'-I','-X','utf8','-c',q['code']],
                    capture_output=True,text=True,encoding='utf-8',timeout=2)
                self.assertEqual(result.returncode,0,f"{q['id']}: {result.stderr}")
                output=result.stdout.strip()
                self.assertEqual(output,q['options'][q['answer']].strip())
                for choice in q['options']:
                    self.assertEqual(E.grade(q['id'],choice)['correct'],choice==q['answer'])
                    if choice!=q['answer']: self.assertIn(choice,q['misconceptions'])
    def test_entire_course_unlocks_in_order(self):
        state=empty_state();self.assertTrue(all(c['locked'] for c in E.courses(state).values()))
        state['reads']=['__intro__']
        for cid in sorted(E.concepts,key=lambda c:E.concepts[c]['order']):
            self.assertFalse(E.courses(state)[cid]['locked']);state['reads'].append(cid)
            for q in [q for q in E.questions if q['concept']==cid]:state['attempts'].append(attempt(q))
            self.assertTrue(E.courses(state)[cid]['passed'])
        self.assertEqual(sum(c['passed'] for c in E.courses(state).values()),15)
    def test_hint_and_free_practice_do_not_pass_course(self):
        state=empty_state();state['reads']=['__intro__','boundary']
        qs=[q for q in E.questions if q['concept']=='boundary']
        for hints,course in [(1,True),(0,False)]:
            state['attempts']=[attempt(q,hints=hints,course=course) for q in qs]
            self.assertFalse(E.courses(state)['boundary']['passed'])
    def test_schedule_early_repeat_not_advance(self):
        q=E.questions[0];a=attempt(q);first=E.schedule([a])[q['id']]
        second=attempt(q,at='2026-10-01T01:00:00Z',ident='second')
        self.assertEqual(first,E.schedule([a,second])[q['id']])
        third=attempt(q,at='2026-10-02T00:00:00Z',ident='third')
        self.assertEqual(E.schedule([a,third])[q['id']]['stage'],2)
        wrong=next(c for c in q['options'] if c!=q['answer']);bad=attempt(q,choice=wrong)
        self.assertEqual(E.schedule([bad])[q['id']]['due']-datetime(2026,10,1,tzinfo=timezone.utc).timestamp()*1000,600000)
    def test_recommendation_target_and_unknown(self):
        q=E.questions[0];state=empty_state()
        result=E.recommend(q['id'],q['concept'],state)
        self.assertEqual(result[0]['concept'],q['concept']);self.assertNotIn(q['id'],[r['id'] for r in result])
        self.assertTrue(all(r['topic']==q['topic'] for r in result))
        self.assertEqual(len(E.recommend(q['id'],'unknown',state)),9)
    def test_import_regrades_and_removes_untrusted_feedback(self):
        state=empty_state();q=E.questions[0];a=attempt(q,choice=next(c for c in q['options'] if c!=q['answer']))
        a['correct']=True;a['feedback']={'source':'ai','concept':'unknown','quote':a['reason'],'explanation':'伪造','hint':'伪造'}
        state['attempts']=[a];checked=E.validate_state(state,importing=True)
        self.assertFalse(checked['attempts'][0]['correct']);self.assertEqual(checked['attempts'][0]['feedback']['source'],'rule')
    def test_import_rejects_invalid_and_oversize(self):
        for field,value in [('reads',['not-a-concept']),('attempts',[{}]),('drafts',{'unknown':'x'}),('version',2)]:
            with self.subTest(field=field):
                s=empty_state();s[field]=value
                with self.assertRaises(ValueError):E.validate_state(s)
        s=empty_state();s['drafts'][E.tasks[0]['id']]='x'*20001
        with self.assertRaises(ValueError):E.validate_state(s)
    def test_sqlite_persistence_isolation_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'records.db';a=Store(path);state=empty_state();state['reads']=['__intro__']
            self.assertEqual(a.save('alice',0,state),1)
            self.assertEqual(Store(path).get('alice'),(1,state));self.assertEqual(a.get('bob'),(0,empty_state()))
            with self.assertRaises(ConflictError):a.save('alice',0,empty_state())

class AITests(unittest.TestCase):
    def setUp(self):
        self.q=E.questions[0];self.choice=next(c for c in self.q['options'] if c!=self.q['answer']);self.reason='我以为边界不包含相等'
        self.valid=dict(concept=self.q['misconceptions'][self.choice]['concept'],quote=self.reason,answer_key=self.q['answer'],knowledge_quote=self.q['explanation'],explanation='请检查等于边界的情况。',hint='关注比较符号。')
    def test_valid_and_unknown_diagnoses(self):
        self.assertTrue(validate_output(self.valid,self.q,self.choice,self.reason)['personalized'])
        self.valid['concept']='unknown';self.assertEqual(validate_output(self.valid,self.q,self.choice,self.reason)['concept'],'unknown')
    def test_bad_quote_and_label_rejected(self):
        for key,value in [('quote','没有说过的话'),('concept','invented')]:
            self.assertIsNone(validate_output(dict(self.valid,**{key:value}),self.q,self.choice,self.reason))
    def test_wrong_answer_or_anchor_uses_reviewed_explanation(self):
        for key,value in [('answer_key','Z'),('knowledge_quote','不存在的依据')]:
            result=validate_output(dict(self.valid,**{key:value}),self.q,self.choice,self.reason)
            self.assertFalse(result['personalized']);self.assertEqual(result['explanation'],self.q['explanation'])
    def test_mock_success_and_timeout_fallback(self):
        import io
        response=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.valid)}}]}).encode()
        def success(req,timeout):
            self.assertEqual(timeout,30);self.assertIn('reason',req.data.decode());return io.BytesIO(response)
        settings={'MOONSHOT_API_KEY':'test-only'}
        self.assertEqual(analyze(E,self.q['id'],self.choice,self.reason,settings,success)['source'],'ai')
        def fail(*args,**kwargs):raise TimeoutError()
        self.assertEqual(analyze(E,self.q['id'],self.choice,self.reason,settings,fail)['source'],'rule')
    def test_no_key_does_not_call_network(self):
        def forbidden(*args,**kwargs):raise AssertionError('Unexpected network')
        self.assertEqual(analyze(E,self.q['id'],self.choice,self.reason,{},forbidden)['source'],'rule')

class CodeSyntaxTests(unittest.TestCase):
    def test_restricted_syntax(self):
        spec=importlib.util.spec_from_file_location('validator',ROOT/'web/public/validator.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
        v.validate_source('def f(x):\n    return x + 1')
        from tests.reference_solutions import SOLUTIONS
        from copy import deepcopy
        for task in E.tasks:
            source=SOLUTIONS[task['id']];v.validate_source(source)
            for case in task['tests']:
                with self.subTest(task=task['id'],args=case['args']):
                    namespace={};exec(source,namespace)
                    actual=namespace[task['function']](*deepcopy(case['args']))
                    self.assertEqual(type(actual),type(case['expected']))
                    self.assertEqual(actual,case['expected'])
        for source in ['import os','open("x")','eval("1")','x.__class__','getattr(x,"a")','class A: pass']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):v.validate_source(source)

if __name__=='__main__':unittest.main()
