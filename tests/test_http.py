"""Real local HTTP acceptance tests with independent browser cookie jars."""
import http.cookiejar
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
    def setUp(self):self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def request(self,path,body=None,origin=None,client=None):
        headers={'Origin':origin or self.url,'Content-Type':'application/json'}
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
    def test_team_authorization_and_rate_limit(self):
        from backend.server import Application
        app=Application(Path(self.temp.name)/'auth.db',{'MOONSHOT_API_KEY':'test','TEAM_ACCESS_CODE':'test-access-code'})
        self.assertTrue(app.ai_enabled());self.assertTrue(app.authorize_ai('test-access-code'));self.assertFalse(app.authorize_ai('incorrect'))
        self.assertTrue(all(app.allow_call() for _ in range(60)));self.assertFalse(app.allow_call())

if __name__=='__main__':unittest.main()
