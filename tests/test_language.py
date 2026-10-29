"""Translation completeness and English-model prompting without network calls."""
import io
import json
import unittest
from backend.domain import LearningEngine,ROOT
from backend.ai import analyze

class LanguageTests(unittest.TestCase):
    def test_all_learning_prose_has_english_translation(self):
        translations=json.loads((ROOT/'web/src/en.json').read_text(encoding='utf-8'))
        skip={'code','example_code','example_output','options','starter','tests','review_status','evidence'}
        def walk(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    if key not in skip:walk(item)
            elif isinstance(value,list):
                for item in value:walk(item)
            elif isinstance(value,str) and any('\u4e00'<=c<='\u9fff' for c in value):
                self.assertIn(value,translations,value)
        for path in (ROOT/'data').glob('*.json'):walk(json.loads(path.read_text(encoding='utf-8')))

    def test_english_prompt_preserves_original_evidence(self):
        engine=LearningEngine();question=engine.question('boundary_1');reason='I thought greater than includes equality.'
        answer=dict(concept='boundary',quote=reason,answer_key='A',knowledge_quote=question['explanation'],explanation='Strict greater-than excludes equality.',hint='Check whether the operator includes an equals sign.')
        def fake(request,timeout):
            payload=json.loads(request.data)
            self.assertEqual(request.full_url, 'https://maas.eduhk.hk/api/v1/chat/completions')
            self.assertEqual(payload['model'], 'glm-4.7')
            self.assertEqual(payload['thinking'], {'type': 'disabled'})
            self.assertIn('in English',payload['messages'][0]['content'])
            evidence=json.loads(payload['messages'][1]['content'])
            self.assertEqual(evidence['reason'],reason)
            self.assertEqual(evidence['explanation'],question['explanation'])
            return io.BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(answer)}}]}).encode())
        result=analyze(engine,question['id'],'B',reason,{'OPENAI_API_KEY':'test-only'},opener=fake,language='en')
        self.assertEqual(result['source'],'ai');self.assertEqual(result['explanation'],answer['explanation'])
