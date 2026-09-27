import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from edu.bank import load_bank
from edu.engine import diagnose, recommend, progress
from edu.storage import Store
from edu.ai import AIHelper


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.questions,cls.concepts=load_bank()

    def test_all_30_reference_answers(self):
        # 只执行仓库维护者编写的固定题目，不接收学生代码。每题独立进程，超时 2 秒。
        self.assertEqual(len(self.questions),30)
        for q in self.questions.values():
            with self.subTest(question=q['id']):
                output=subprocess.run([sys.executable,'-I','-c',q['code']],capture_output=True,text=True,timeout=2,check=True)
                self.assertEqual(output.stdout.rstrip('\n'),q['options'][q['answer']])
                self.assertEqual(len(set(q['options'].values())),3)

    def test_all_answer_options(self):
        for q in self.questions.values():
            for choice in q['options']:
                result=diagnose(q,choice)
                self.assertEqual(result['correct'],choice==q['answer'])
                self.assertEqual(result['concept'],None if result['correct'] else q['concept'])
        with self.assertRaises(ValueError): diagnose(next(iter(self.questions.values())),'D')

    def test_topics_and_paired_concepts(self):
        from collections import Counter
        self.assertEqual(set(Counter(q['topic'] for q in self.questions.values()).values()),{10})
        self.assertEqual(set(Counter(q['concept'] for q in self.questions.values()).values()),{2})

    def test_targeted_recommendation_for_every_question(self):
        for q in self.questions.values():
            result=recommend(q,self.questions,[])
            self.assertEqual(result[0]['question']['concept'],q['concept'])
            self.assertNotIn(q['id'],[r['question']['id'] for r in result])
            self.assertTrue(all(r['question']['topic']==q['topic'] for r in result))
            self.assertEqual(result,recommend(q,self.questions,[]))

    def test_unseen_first_and_exhausted_bank(self):
        q=self.questions['range_end_1']
        result=recommend(q,self.questions,[{'question_id':'range_end_2'}])
        self.assertNotEqual(result[0]['question']['id'],'range_end_2')
        history=[{'question_id':qid} for qid in self.questions]
        result=recommend(q,self.questions,history)
        self.assertTrue(all(r['reason'].startswith('复习题') for r in result))
        self.assertEqual(result[0]['question']['id'],'range_end_2')

    def test_sqlite_persists_reason_and_ai(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'learning.sqlite3'; store=Store(path)
            q=self.questions['range_end_1']; reason="我觉得包含 4'; DROP TABLE attempts; --"
            store.save(q['id'],'B',reason,diagnose(q,'B'),{'status':'fallback'})
            history=Store(path).history()
            self.assertEqual(len(history),1)
            self.assertEqual(history[0]['reason'],reason)
            self.assertEqual(json.loads(history[0]['ai_json'])['status'],'fallback')
            self.assertFalse(history[0]['correct'])

    def test_progress_requires_different_questions(self):
        history=[{'question_id':'range_end_1','correct':1}]*3
        row=next(r for r in progress(self.questions,history,self.concepts) if r['concept']=='range_end')
        self.assertEqual(row['state'],'本次答对，待验证')
        history.append({'question_id':'range_end_2','correct':1})
        row=next(r for r in progress(self.questions,history,self.concepts) if r['concept']=='range_end')
        self.assertEqual(row['state'],'初步稳定，继续巩固')
        history.append({'question_id':'range_end_2','correct':0})
        row=next(r for r in progress(self.questions,history,self.concepts) if r['concept']=='range_end')
        self.assertEqual(row['state'],'仍需练习')

    def analyze(self,payload):
        raw=json.dumps({'message':{'content':json.dumps(payload,ensure_ascii=False)}}).encode()
        with patch('edu.ai.urlopen') as mock:
            mock.return_value.__enter__.return_value.read.return_value=raw
            return AIHelper('mock').analyze(self.questions['range_end_1'],'B','我知道不含4，点错了',self.concepts)

    def test_ai_abstains_from_careless_error(self):
        result=self.analyze({'concept':'unknown','quote':'点错了'})
        self.assertEqual(result['status'],'ok'); self.assertEqual(result['concept'],'unknown')

    def test_ai_valid_concept(self):
        result=self.analyze({'concept':'range_end','quote':'不含4'})
        self.assertEqual(result['status'],'ok')
        # 结构检查无法保证语义正确，本测试不把模型结论当作金标准。

    def test_ai_rejects_hallucinations(self):
        for payload in [{'concept':'made_up','quote':'点错了'}, {'concept':'range_end','quote':'包含终点'},
                        {'concept':'range_end','quote':''}, [], {'concept':None,'quote':'点错了'}]:
            with self.subTest(payload=payload): self.assertEqual(self.analyze(payload)['status'],'fallback')

    def test_ai_timeout_and_invalid_json_fallback(self):
        with patch('edu.ai.urlopen',side_effect=TimeoutError):
            result=AIHelper('mock').analyze(self.questions['range_end_1'],'B','包含4',self.concepts)
            self.assertEqual(result['status'],'fallback')
        with patch('edu.ai.urlopen') as mock:
            mock.return_value.__enter__.return_value.read.return_value=b'not json'
            self.assertEqual(AIHelper('mock').analyze(self.questions['range_end_1'],'B','包含4',self.concepts)['status'],'fallback')

    def test_ai_disabled_or_no_reason_no_network(self):
        q=self.questions['range_end_1']
        with patch('edu.ai.urlopen') as mock:
            self.assertEqual(AIHelper('').analyze(q,'B','包含4',self.concepts)['status'],'disabled')
            self.assertEqual(AIHelper('mock').analyze(q,'B','',self.concepts)['status'],'skipped')
            self.assertEqual(AIHelper('mock').analyze(q,'A','不含4',self.concepts)['status'],'skipped')
            mock.assert_not_called()

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test.sqlite3'
            run=subprocess.run([sys.executable,'main.py','--cli','--db',str(path)],input='2\nB\n测试理由\nn\nq\n',capture_output=True,text=True,timeout=5)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(len(Store(path).history()),1)

if __name__=='__main__': unittest.main()
