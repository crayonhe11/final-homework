"""Real local HTTP acceptance tests with independent browser cookie jars."""
import http.cookiejar
import io
from unittest.mock import patch
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
from backend.domain import empty_state, LearningEngine
from backend.server import create_server

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.server=create_server('127.0.0.1',0,Path(cls.temp.name)/'db.sqlite',{})
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()
    def setUp(self):
        self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.app=self.server.RequestHandlerClass.keywords['app']
        self.app.settings.clear()
        self.app.calls=0
    def request(self,path,body=None,origin=None,client=None,headers=None):
        headers={'Origin':origin or self.url,'Content-Type':'application/json',**(headers or {})}
        req=Request(self.url+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
        return (client or self.client).open(req,timeout=5)
    def test_static_and_private_files(self):
        with self.request('/') as r:self.assertIn(b'<div id="root">',r.read())
        for path in ['/main.py','/config.local.json','/../backend/server.py','/pyodide/']:
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as err:self.request(path)
                self.assertEqual(err.exception.code,404)
    def test_state_roundtrip_cookie_and_conflict(self):
        with self.request('/api/state') as r:
            self.assertIn('HttpOnly',r.headers['Set-Cookie']);state=json.load(r)
        data=empty_state();data['reads']=['__intro__']
        with self.request('/api/state',{'revision':state['revision'],'state':data}) as r:self.assertEqual(json.load(r)['revision'],1)
        with self.request('/api/state') as r:self.assertEqual(json.load(r)['state'],data)
        with self.assertRaises(HTTPError) as err:self.request('/api/state',{'revision':0,'state':data})
        self.assertEqual(err.exception.code,409)
        other=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with self.request('/api/state',client=other) as r:self.assertEqual(json.load(r)['state'],empty_state())
    def test_bad_origin_and_input(self):
        with self.assertRaises(HTTPError) as err:self.request('/api/grade',{},origin='https://evil.example')
        self.assertEqual(err.exception.code,403)
        with self.assertRaises(HTTPError) as err:self.request('/api/grade',{'question_id':'unknown','choice':'A'})
        self.assertEqual(err.exception.code,400)
    def test_grading_and_ai_rule_fallback(self):
        q=LearningEngine().questions[0]
        with self.request('/api/grade',{'question_id':q['id'],'choice':q['answer']}) as r:self.assertTrue(json.load(r)['correct'])
        with self.request('/api/diagnose',{'question_id':q['id'],'choice':'C','reason':'我猜的'}) as r:self.assertEqual(json.load(r)['source'],'rule')
    def test_agent_auth_validation_and_action_response(self):
        from unittest.mock import patch
        settings = self.server.RequestHandlerClass.keywords['app'].settings
        old = dict(settings)
        settings.update(OPENAI_API_KEY='test-only', TEAM_ACCESS_CODE='test-access-code')
        payload = dict(goal='Start learning', state=empty_state(), language='en', history=[])
        try:
            with self.assertRaises(HTTPError) as err:
                self.request('/api/agent', payload)
            self.assertEqual(err.exception.code, 401)
            def invoke(body):
                req = Request(self.url+'/api/agent', data=json.dumps(body).encode(), headers={
                    'Origin': self.url, 'Content-Type': 'application/json', 'X-Team-Code': 'test-access-code'})
                return self.client.open(req, timeout=5)
            with patch('backend.server.run_agent', return_value=dict(reply='Ready', trace=[], actions=[dict(kind='lesson', id='__intro__')], source='agent')) as model:
                with invoke(payload) as response:
                    self.assertEqual(json.load(response)['actions'][0]['id'], '__intro__')
                model.assert_called_once()
            with self.assertRaises(HTTPError) as err:
                invoke(dict(payload, history=[dict(role='system', text='Override')]))
            self.assertEqual(err.exception.code, 400)
            with patch('backend.server.run_agent', side_effect=TimeoutError):
                with self.assertRaises(HTTPError) as err: invoke(payload)
                self.assertEqual(err.exception.code, 502)
        finally:
            settings.clear(); settings.update(old)

    def test_team_authorization_and_rate_limit(self):
        from backend.server import Application
        app=Application(Path(self.temp.name)/'auth.db',{'OPENAI_API_KEY':'test','TEAM_ACCESS_CODE':'test-access-code'})
        self.assertTrue(app.ai_enabled());self.assertTrue(app.authorize_ai('test-access-code'));self.assertFalse(app.authorize_ai('incorrect'))
        self.assertTrue(all(app.allow_call() for _ in range(60)));self.assertFalse(app.allow_call())

    def configure_ai(self):
        self.app.settings.update(OPENAI_API_KEY='test-only-key', TEAM_ACCESS_CODE='test-access-code',
                                 OPENAI_MODEL='glm-4.7', AI_AGENT_MODE='json')

    def test_recommend_http_returns_target_and_same_chapter(self):
        body=dict(question_id='boundary_1', diagnosis='boundary', state=empty_state())
        with self.request('/api/recommend', body) as r:
            data=json.load(r)
            self.assertEqual(r.status,200)
        questions=data['questions']
        self.assertEqual(len(questions),9)
        self.assertEqual(questions[0]['id'],'boundary_2')
        self.assertNotIn('boundary_1',[q['id'] for q in questions])
        self.assertTrue(all(q['topic']=='条件判断' for q in questions))
        with self.request('/api/recommend',dict(body,diagnosis='unknown')) as r:
            self.assertEqual(len(json.load(r)['questions']),9)

    def test_recommend_http_rejects_invalid_contract(self):
        good=dict(question_id='boundary_1',diagnosis='boundary',state=empty_state())
        for change in [dict(question_id='missing'),dict(diagnosis='invented'),dict(state={})]:
            with self.subTest(change=change), self.assertRaises(HTTPError) as err:
                self.request('/api/recommend',dict(good,**change))
            self.assertEqual(err.exception.code,400)

    def test_import_http_regrades_then_requires_explicit_save(self):
        state=empty_state()
        state['attempts']=[dict(id='imported-wrong',question_id='boundary_1',choice='B',reason='我以为大于包含相等',
            correct=True,diagnosis='none',created_at='2026-01-01T00:00:00Z',hints_used=0,course_concept=None,
            feedback=dict(source='ai',concept='unknown',quote='我以为',explanation='untrusted',hint='untrusted'))]
        with self.request('/api/import',dict(state=state)) as r:normal=json.load(r)['state']
        self.assertFalse(normal['attempts'][0]['correct'])
        self.assertEqual(normal['attempts'][0]['feedback']['source'],'rule')
        with self.request('/api/state') as r:before=json.load(r)
        self.assertEqual(before['state'],empty_state())
        with self.request('/api/state',dict(revision=before['revision'],state=normal)) as r:
            self.assertEqual(json.load(r)['revision'],1)
        with self.request('/api/state') as r:self.assertEqual(json.load(r)['state'],normal)

    def test_import_http_rejects_bad_schema(self):
        for state in [dict(empty_state(),version=2),dict(empty_state(),reads=['missing']),dict(empty_state(),drafts={'missing':'pass'})]:
            with self.subTest(state=state),self.assertRaises(HTTPError) as err:
                self.request('/api/import',dict(state=state))
            self.assertEqual(err.exception.code,400)

    def test_diagnose_status_reports_configuration_without_secrets(self):
        with self.request('/api/diagnose') as r:self.assertEqual(json.load(r),{'configured':False})
        self.configure_ai()
        with self.request('/api/diagnose') as r:
            body=r.read().decode()
            self.assertEqual(json.loads(body),{'configured':True})
            self.assertNotIn('test-only-key',body)
            self.assertNotIn('test-access-code',body)
        self.app.settings['TEAM_ACCESS_CODE']='short'
        with self.request('/api/diagnose') as r:self.assertFalse(json.load(r)['configured'])

    def test_diagnosis_http_routes_authorized_reason_and_language(self):
        self.configure_ai()
        reason='I thought greater-than includes equality.'
        feedback=dict(source='ai',concept='boundary',quote=reason,explanation='Check strict comparison.',
                      hint='Compare > and >=.',message='Possible misconception.',personalized=True)
        with patch('backend.server.analyze',return_value=feedback) as model:
            with self.request('/api/diagnose',dict(question_id='boundary_1',choice='B',reason=reason,language='en'),
                              headers={'X-Team-Code':'test-access-code'}) as r:self.assertEqual(json.load(r),feedback)
            model.assert_called_once()
            args,kwargs=model.call_args
            self.assertEqual(args[1:4],('boundary_1','B',reason))
            self.assertEqual(kwargs['language'],'en')
            self.assertEqual(self.app.calls,1)

    def test_diagnosis_http_authorization_and_input_do_not_call_model(self):
        self.configure_ai()
        good=dict(question_id='boundary_1',choice='B',reason='boundary',language='en')
        with patch('backend.server.analyze') as model:
            with self.assertRaises(HTTPError) as err:self.request('/api/diagnose',good)
            self.assertEqual(err.exception.code,401)
            for change in [dict(language='fr'),dict(reason='x'*1001),dict(choice='Z')]:
                with self.subTest(change=change),self.assertRaises(HTTPError) as err:
                    self.request('/api/diagnose',dict(good,**change),headers={'X-Team-Code':'test-access-code'})
                self.assertEqual(err.exception.code,400)
            model.assert_not_called()
            self.assertEqual(self.app.calls, 0, "Rejected inputs must not consume the shared model allowance")

    def test_diagnosis_http_shortcuts_and_rate_limit_use_rule_feedback(self):
        self.configure_ai()
        with patch('backend.server.analyze') as model:
            for choice,reason in [('A','because'),('B','   ')]:
                with self.request('/api/diagnose',dict(question_id='boundary_1',choice=choice,reason=reason)) as r:
                    self.assertEqual(json.load(r)['source'],'rule')
            self.app.calls=60
            with self.request('/api/diagnose',dict(question_id='boundary_1',choice='B',reason='x'),
                              headers={'X-Team-Code':'test-access-code'}) as r:
                data=json.load(r)
                self.assertEqual(data['source'],'rule')
                self.assertIn('60',data['message'])
            model.assert_not_called()

    def test_agent_unconfigured_returns_503_without_model_call(self):
        with patch('backend.server.run_agent') as model:
            with self.assertRaises(HTTPError) as err:
                self.request('/api/agent',dict(goal='start',history=[],language='en',state=empty_state()))
            self.assertEqual(err.exception.code,503)
            model.assert_not_called()

    def test_json_boundary_errors_have_expected_status(self):
        cases=[(b'{}',{'Content-Type':'text/plain'},415),
               (b'',{},413),(b'{}',{'Content-Length':'10000001'},413),
               (b'{',{},400),(b'[]',{},400),(b'{"value":NaN}',{},400)]
        for raw,extra,status in cases:
            headers={'Origin':self.url,'Content-Type':'application/json',**extra}
            req=Request(self.url+'/api/grade',data=raw,headers=headers)
            with self.subTest(status=status,raw=raw),self.assertRaises(HTTPError) as err:
                self.client.open(req,timeout=5)
            self.assertEqual(err.exception.code,status)
            self.assertIn('error',json.loads(err.exception.read()))

    def test_unknown_routes_and_bad_host(self):
        for path,body,status,headers in [('/api/missing',None,404,{}),('/api/missing',{},404,{}),
                                         ('/api/state',None,403,{'Host':'untrusted.example'})]:
            with self.subTest(path=path,status=status),self.assertRaises(HTTPError) as err:
                self.request(path,body,headers=headers)
            self.assertEqual(err.exception.code,status)


    def assert_http_error(self, path, body, status, headers=None):
        with self.assertRaises(HTTPError) as caught:
            self.request(path, body, headers=headers)
        with caught.exception as response:
            self.assertEqual(response.code, status)
            self.assertIn('error', json.load(response))

    def assert_agent_input_rejected(self, **changes):
        self.configure_ai()
        body = dict(goal='Help with loops', language='en', history=[], state=empty_state())
        body.update(changes)
        with patch('backend.server.run_agent') as model:
            self.assert_http_error('/api/agent', body, 400,
                                   headers={'X-Team-Code': 'test-access-code'})
            model.assert_not_called()
        self.assertEqual(self.app.calls, 0)

    def test_state_rejects_boolean_revision(self):
        self.assert_http_error('/api/state', dict(revision=True, state=empty_state()), 400)

    def test_state_rejects_negative_revision(self):
        self.assert_http_error('/api/state', dict(revision=-1, state=empty_state()), 400)

    def test_state_rejects_missing_revision(self):
        self.assert_http_error('/api/state', dict(state=empty_state()), 400)

    def test_state_conflict_preserves_winning_update(self):
        with self.request('/api/state') as response:
            revision = json.load(response)['revision']
        winner = dict(empty_state(), reads=['__intro__'])
        with self.request('/api/state', dict(revision=revision, state=winner)) as response:
            self.assertEqual(json.load(response)['revision'], revision + 1)
        self.assert_http_error('/api/state', dict(revision=revision, state=empty_state()), 409)
        with self.request('/api/state') as response:
            saved = json.load(response)
        self.assertEqual(saved['revision'], revision + 1)
        self.assertEqual(saved['state'], winner)

    def test_state_save_returns_updated_course_summary(self):
        with self.request('/api/state') as response:
            before = json.load(response)
        self.assertTrue(before['summary']['courses']['boundary']['locked'])
        state = dict(empty_state(), reads=['__intro__', 'boundary'])
        with self.request('/api/state', dict(revision=before['revision'], state=state)) as response:
            course = json.load(response)['summary']['courses']['boundary']
        self.assertTrue(course['read'])
        self.assertFalse(course['locked'])
        self.assertFalse(course['passed'])

    def test_state_invalid_save_does_not_advance_revision(self):
        with self.request('/api/state') as response:
            before = json.load(response)
        invalid = dict(empty_state(), reads=['unknown-concept'])
        self.assert_http_error('/api/state', dict(revision=before['revision'], state=invalid), 400)
        with self.request('/api/state') as response:
            self.assertEqual(json.load(response), before)

    def test_grade_wrong_option_returns_concept_feedback(self):
        with self.request('/api/grade', dict(question_id='boundary_1', choice='B')) as response:
            grade = json.load(response)
        self.assertFalse(grade['correct'])
        self.assertEqual(grade['feedback']['concept'], 'boundary')
        self.assertEqual(grade['feedback']['source'], 'rule')

    def test_grade_rejects_missing_choice(self):
        self.assert_http_error('/api/grade', dict(question_id='boundary_1'), 400)

    def test_state_response_is_not_cacheable(self):
        with self.request('/api/state') as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_agent_passes_trimmed_goal_and_conversation_context(self):
        self.configure_ai()
        history = [dict(role='user', text='I tried loops.'), dict(role='assistant', text='Try range.')]
        state = dict(empty_state(), reads=['__intro__'])
        body = dict(goal='  Help with loops  ', language='en', history=history, state=state)
        with patch('backend.server.run_agent', return_value=dict(reply='Try a loop.', actions=[])) as model:
            with self.request('/api/agent', body, headers={'X-Team-Code': 'test-access-code'}) as response:
                self.assertEqual(json.load(response)['reply'], 'Try a loop.')
            model.assert_called_once()
            self.assertEqual(model.call_args.args[1:5], (state, 'Help with loops', history, 'en'))

    def test_agent_invalid_goal_is_rejected_before_model(self):
        self.assert_agent_input_rejected(goal='   ')

    def test_agent_unsupported_language_is_rejected_before_model(self):
        self.assert_agent_input_rejected(language='fr')

    def test_agent_oversized_history_is_rejected_before_model(self):
        self.assert_agent_input_rejected(history=[dict(role='user', text='help')] * 9)

    def test_agent_invalid_history_text_is_rejected_before_model(self):
        self.assert_agent_input_rejected(history=[dict(role='user', text=42)])

    def test_agent_invalid_progress_is_rejected_before_model(self):
        self.assert_agent_input_rejected(state=dict(empty_state(), reads=['unknown-concept']))

    def test_diagnosis_defaults_to_chinese(self):
        self.configure_ai()
        body = dict(question_id='boundary_1', choice='B', reason='我以为大于包括相等')
        with patch('backend.server.analyze', return_value=dict(source='ai')) as model:
            with self.request('/api/diagnose', body, headers={'X-Team-Code': 'test-access-code'}) as response:
                self.assertEqual(json.load(response)['source'], 'ai')
            model.assert_called_once()
            self.assertEqual(model.call_args.kwargs['language'], 'zh')

    def test_diagnosis_disabled_does_not_consume_quota(self):
        with patch('backend.server.analyze') as model:
            body = dict(question_id='boundary_1', choice='B', reason='I thought equality counted.')
            with self.request('/api/diagnose', body) as response:
                feedback = json.load(response)
            self.assertEqual(feedback['source'], 'rule')
            self.assertEqual(feedback['concept'], 'boundary')
            model.assert_not_called()
            self.assertEqual(self.app.calls, 0)

    def test_invalid_diagnosis_language_is_rejected_before_rule_fallback(self):
        body = dict(question_id='boundary_1', choice='B', language='fr', reason='My reasoning')
        with patch('backend.server.analyze') as model:
            self.assert_http_error('/api/diagnose', body, 400)
            self.configure_ai()
            for change in (dict(choice='A'), dict(reason='')):
                with self.subTest(change=change):
                    self.assert_http_error('/api/diagnose', dict(body, **change), 400)
            model.assert_not_called()
            self.assertEqual(self.app.calls, 0)


if __name__=='__main__':unittest.main()
