import json,unittest,tempfile,subprocess,sys
from pathlib import Path
from unittest.mock import patch
from edu.ai import AIHelper,checked_feedback
from edu.bank import load_bank
from edu.engine import recommend

class AIFeatureTests(unittest.TestCase):
    def setUp(self):
        self.questions,self.concepts=load_bank();self.q=self.questions['range_end_2']
        self.result={'concept':'range_end','quote':'包含5','answer_key':'B',
                     'knowledge_quote':self.q['explanation'],'explanation':'你把5也列进去了。range的终点不包含，因此输出2、3、4。','hint':'换一个终点，再列出序列。'}
    def test_personalized_feedback_and_fallback(self):
        self.assertEqual(checked_feedback(self.result,self.q)['status'],'ok')
        for change in [{'answer_key':'A'},{'knowledge_quote':'不存在的解析'},{'hint':'x'*241},{'explanation':None}]:
            feedback=checked_feedback({**self.result,**change},self.q)
            self.assertEqual(feedback['status'],'fallback');self.assertEqual(feedback['explanation'],self.q['explanation'])
    def test_ai_result_has_feedback_metadata_no_secret(self):
        config={'EDU_AI_PROVIDER':'kimi','MOONSHOT_API_KEY':'fake-secret'}
        with patch('edu.ai.ai_config',return_value=config),patch('edu.ai.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.result)}}],'usage':{'prompt_tokens':100,'completion_tokens':80,'total_tokens':180,'secret':'not-saved'}}).encode()
            out=AIHelper().analyze(self.q,'A','我以为包含5',self.concepts)
        self.assertEqual(out['status'],'ok');self.assertEqual(out['feedback']['status'],'ok');self.assertTrue(out['response_received'])
        self.assertEqual(out['usage']['total_tokens'],180);self.assertNotIn('fake-secret',json.dumps(out));self.assertNotIn('not-saved',json.dumps(out))
    def test_feedback_failure_preserves_valid_diagnosis(self):
        with patch('edu.ai.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps({'message':{'content':json.dumps({**self.result,'answer_key':'A'})}}).encode()
            out=AIHelper('test').analyze(self.q,'A','我以为包含5',self.concepts)
        self.assertEqual(out['status'],'ok');self.assertEqual(out['feedback']['status'],'fallback')
    def test_unknown_changes_ranking_and_stays_in_bank(self):
        q={'id':'current','topic':'循环','concept':'range_end','difficulty':2}
        bank={q['id']:q,'hard':{**q,'id':'hard'},'easy':{**q,'id':'easy','concept':'other','difficulty':1},'outside':{**q,'id':'outside','topic':'函数与返回值','difficulty':1}}
        baseline=recommend(q,bank,[],limit=2)
        neutral=recommend(q,bank,[],limit=2,ai={'status':'ok','concept':'unknown'})
        self.assertEqual(baseline[0]['question']['id'],'hard');self.assertEqual(neutral[0]['question']['id'],'easy')
        self.assertEqual(neutral[0]['strategy'],'neutral_verification')
        self.assertEqual({r['question']['id'] for r in neutral},{'easy','hard'})
        for ai in [{'status':'fallback','concept':'unknown'},{'status':'ok','concept':'invented'}]:
            self.assertEqual(recommend(q,bank,[],limit=2,ai=ai),baseline)
    def test_targeted_reason_and_no_repetition(self):
        r=recommend(self.q,self.questions,[],ai={'status':'ok','concept':'range_end'})
        self.assertEqual(r[0]['strategy'],'ai_targeted');self.assertEqual(r[0]['question']['concept'],'range_end')
        self.assertNotIn(self.q['id'],[v['question']['id'] for v in r])
    def test_evaluation_budget_stops_before_call(self):
        from evaluation import evaluate
        import contextlib,io
        errors=io.StringIO()
        with patch('evaluation.evaluate.AIHelper') as helper,patch('sys.argv',['evaluate','--ai','--max-calls','1']),contextlib.redirect_stderr(errors):
            helper.return_value.model='mock'
            with self.assertRaises(SystemExit): evaluate.main()
            helper.return_value.analyze.assert_not_called()
        self.assertIn('尚未发起调用',errors.getvalue())
    def test_offline_report_has_no_fabricated_ai_result(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'report.json'
            r=subprocess.run([sys.executable,'evaluation/evaluate.py','--output',str(output)],capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stderr);report=json.loads(output.read_text())
            self.assertIsNone(report['combined_agreement']);self.assertEqual(report['ai_valid_count'],0)
            self.assertIsNone(report['cases'][0]['human_review']['knowledge_correct'])

    def test_online_evaluation_logic_with_mock_not_network(self):
        from evaluation import evaluate
        import contextlib,io
        cases=[{'id':'a','question_id':'range_end_2','choice':'A','reason':'包含5','expected':'range_end'},
               {'id':'b','question_id':'range_end_2','choice':'A','reason':'我点错了','expected':'unknown'}]
        with tempfile.TemporaryDirectory() as d:
            data=Path(d)/'cases.json';data.write_text(json.dumps(cases));out=Path(d)/'report.json'
            with patch('evaluation.evaluate.AIHelper') as helper,patch('sys.argv',['evaluate','--ai','--dataset',str(data),'--output',str(out),'--max-calls','2']),contextlib.redirect_stdout(io.StringIO()):
                helper.return_value.model='mock';helper.return_value.provider='mock'
                helper.return_value.analyze.side_effect=[{'status':'ok','concept':'range_end','feedback':{'status':'ok'}},{'status':'ok','concept':'unknown','feedback':{'status':'fallback'}}]
                evaluate.main();self.assertEqual(helper.return_value.analyze.call_count,2)
            r=json.loads(out.read_text());self.assertEqual(r['rule_agreement'],.5);self.assertEqual(r['combined_agreement'],1)
            self.assertEqual(r['improved_ids'],['b']);self.assertEqual(r['feedback_valid_count'],1)
    def test_connection_check_default_does_not_call_model(self):
        from evaluation import check_connection
        import contextlib,io
        with patch('evaluation.check_connection.AIHelper') as helper,patch('sys.argv',['check_connection']),contextlib.redirect_stdout(io.StringIO()):
            helper.return_value.model='mock';check_connection.main();helper.return_value.analyze.assert_not_called()
