import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from edu.ai import AIHelper
from edu.config import ai_config
from edu.bank import load_bank

class KimiTests(unittest.TestCase):
    def helper(self,**overrides):
        config={'EDU_AI_PROVIDER':'kimi','MOONSHOT_API_KEY':'test-fake-key','MOONSHOT_MODEL':'kimi-k2.6',**overrides}
        with patch('edu.ai.ai_config',return_value=config): return AIHelper()
    def run_analysis(self,helper):
        q,c=load_bank();return helper.analyze(q['range_end_1'],'B','我以为包含4',c)
    def test_config_file_priority_and_no_secret_fallback(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'MOONSHOT_API_KEY':'env-fake'},clear=True):
            p=Path(d)/'api_config.json'
            self.assertEqual(ai_config(p)['MOONSHOT_API_KEY'],'env-fake')
            p.write_text(json.dumps({'MOONSHOT_API_KEY':'file-fake','OTHER':'ignored'}))
            self.assertEqual(ai_config(p),{'EDU_AI_PROVIDER':'kimi','MOONSHOT_API_KEY':'file-fake'})
            for content in ['bad json',json.dumps({'MOONSHOT_API_KEY':12}),json.dumps({'MOONSHOT_API_KEY':''})]:
                p.write_text(content);self.assertEqual(ai_config(p)['MOONSHOT_API_KEY'],'')
    def test_request_and_response(self):
        with patch('edu.ai.urlopen') as call:
            call.return_value.__enter__.return_value.read.return_value=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'concept':'range_end','quote':'包含4'})}}]}).encode()
            result=self.run_analysis(self.helper());self.assertEqual(result['status'],'ok')
            request=call.call_args.args[0];payload=json.loads(request.data)
            self.assertEqual(request.full_url,'https://api.moonshot.cn/v1/chat/completions')
            self.assertEqual(request.get_header('Authorization'),'Bearer test-fake-key')
            self.assertEqual(payload['thinking'],{'type':'disabled'});self.assertNotIn('temperature',payload)
            self.assertNotIn('test-fake-key',json.dumps(result))
    def test_missing_key_and_untrusted_host_no_network(self):
        with patch('edu.ai.urlopen') as call:
            self.assertEqual(self.run_analysis(self.helper(MOONSHOT_API_KEY=''))['status'],'disabled')
            self.assertEqual(self.run_analysis(self.helper(MOONSHOT_BASE_URL='https://example.com'))['status'],'fallback')
            call.assert_not_called()
    def test_http_error_redacted(self):
        with patch('edu.ai.urlopen',side_effect=HTTPError('url',401,'private-error',{},None)):
            r=self.run_analysis(self.helper());self.assertEqual(r['status'],'fallback');self.assertIn('密钥无效',r['message']);self.assertNotIn('private-error',str(r))
    def test_invalid_or_incomplete_output(self):
        for finish,content in [('length','{}'),('stop','not json'),('stop',json.dumps({'concept':'range_end','quote':'虚构原文'}))]:
            with patch('edu.ai.urlopen') as call:
                call.return_value.__enter__.return_value.read.return_value=json.dumps({'choices':[{'finish_reason':finish,'message':{'content':content}}]}).encode()
                self.assertEqual(self.run_analysis(self.helper())['status'],'fallback')
