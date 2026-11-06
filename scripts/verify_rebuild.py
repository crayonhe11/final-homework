"""Black-box reconstruction checks: standard library, no project imports or paid AI."""
import argparse
import http.cookiejar
import json
import sys
import unittest
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
from urllib.parse import urlsplit

BASE=''
def empty():
    return dict(version=1,reads=[],attempts=[],drafts={},codeAttempts=[])

class ReconstructionContractTests(unittest.TestCase):
    def setUp(self):
        self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self,path,body=None):
        request=Request(BASE+path,data=None if body is None else json.dumps(body).encode(),
                        headers={'Origin':BASE,'Content-Type':'application/json'})
        with self.client.open(request,timeout=5) as response:
            self.assertEqual(response.status,200)
            return json.load(response)

    def test_get_state_contract(self):
        data=self.request('/api/state')
        self.assertEqual(data['state'],empty())
        self.assertEqual(data['revision'],0)
        self.assertIn('boundary',data['summary']['courses'])
        self.assertEqual(data['summary']['schedule'],{})

    def test_post_state_contract(self):
        before=self.request('/api/state');state=empty();state['reads']=['__intro__']
        saved=self.request('/api/state',dict(revision=before['revision'],state=state))
        self.assertEqual(saved['revision'],1)
        self.assertEqual(self.request('/api/state')['state'],state)
        with self.assertRaises(HTTPError) as err:self.request('/api/state',dict(revision=0,state=state))
        self.assertEqual(err.exception.code,409)

    def test_post_grade_contract(self):
        for choice,correct in [('A',True),('B',False),('C',False)]:
            result=self.request('/api/grade',dict(question_id='boundary_1',choice=choice))
            self.assertEqual(result['correct'],correct)
            self.assertEqual(result['feedback']['source'],'rule')
            self.assertEqual(result['feedback']['concept'],'none' if correct else 'boundary')
        with self.assertRaises(HTTPError) as err:self.request('/api/grade',dict(question_id='missing',choice='A'))
        self.assertEqual(err.exception.code,400)

    def test_post_recommend_contract(self):
        data=self.request('/api/recommend',dict(question_id='boundary_1',diagnosis='boundary',state=empty()))
        rows=data['questions'];self.assertEqual(len(rows),9)
        self.assertEqual(rows[0]['id'],'boundary_2')
        self.assertNotIn('boundary_1',[q['id'] for q in rows])
        self.assertTrue(all(q['topic']=='条件判断' for q in rows))

    def test_post_import_contract(self):
        state=empty();state['attempts']=[dict(id='contract-import',question_id='boundary_1',choice='B',
            reason='I thought equality was included.',correct=True,diagnosis='none',created_at='2026-01-01T00:00:00Z',
            hints_used=0,course_concept=None)]
        result=self.request('/api/import',dict(state=state))['state']
        self.assertFalse(result['attempts'][0]['correct'])
        self.assertEqual(result['attempts'][0]['feedback']['source'],'rule')
        self.assertEqual(self.request('/api/state')['state'],empty())

    def test_get_diagnose_contract(self):
        result=self.request('/api/diagnose')
        self.assertEqual(set(result),{'configured'})
        self.assertIs(type(result['configured']),bool)

    def test_post_diagnose_safe_shortcut_contract(self):
        # Correct answer bypasses model access; never send a paid wrong-reason request.
        result=self.request('/api/diagnose',dict(question_id='boundary_1',choice='A',reason='known answer',language='en'))
        self.assertEqual(result['source'],'rule')
        self.assertEqual(result['concept'],'none')

    def test_post_agent_unconfigured_contract(self):
        if self.request('/api/diagnose')['configured']:
            self.skipTest('Run an AI-disabled test server to verify 503 without a paid request.')
        with self.assertRaises(HTTPError) as err:
            self.request('/api/agent',dict(goal='start',history=[],language='en',state=empty()))
        self.assertEqual(err.exception.code,503)


def main():
    global BASE
    parser=argparse.ArgumentParser(description='Check a fresh reconstruction via its HTTP interface; no implementation imports or paid model calls.')
    parser.add_argument('--url',required=True,help='Fresh temporary test server origin, e.g. http://127.0.0.1:8021')
    args=parser.parse_args();BASE=args.url.rstrip('/')
    parsed=urlsplit(BASE)
    if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.path:
        parser.error('Use an origin without a path.')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReconstructionContractTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':
    raise SystemExit(main())
