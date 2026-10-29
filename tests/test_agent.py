"""Tests of real agent tool loops without network or API costs."""
import io
import json
import unittest
from backend.agent import AgentTools, run_agent
from backend.domain import LearningEngine, empty_state

class PiPoTests(unittest.TestCase):
    def setUp(self):
        self.engine = LearningEngine()
        self.settings = {'OPENAI_API_KEY': 'test-only'}

    def test_json_gateway_executes_tools_instead_of_showing_markup(self):
        settings = dict(self.settings, AI_AGENT_MODE='json')
        responses = [
            {'tool_calls': [{'name': 'lesson', 'arguments': {'concept_id': '__intro__'}}]},
            {'tool_calls': [{'name': 'open_content', 'arguments': {'kind': 'lesson', 'id': '__intro__'}}]},
            {'reply': '已打开入门导学，请先阅读这一课。'},
        ]
        requests = []
        def fake(request, timeout):
            payload = json.loads(request.data)
            requests.append(payload)
            self.assertNotIn('tools', payload)
            self.assertNotIn('tool_choice', payload)
            self.assertLessEqual(timeout, 60)
            result = responses.pop(0)
            return io.BytesIO(json.dumps({'choices': [{'finish_reason': 'stop',
                'message': {'content': '```json\n' + json.dumps(result) + '\n```'}}]}).encode())
        result = run_agent(self.engine, empty_state(), '带我开始学习', [], 'zh', settings, lambda: True, fake)
        self.assertEqual(result['actions'], [{'kind': 'lesson', 'id': '__intro__'}])
        self.assertEqual([r['tool'] for r in result['trace']], ['progress', 'lesson', 'open_content'])
        self.assertIn('observations', requests[-1]['messages'][-1]['content'])
        self.assertNotIn('<tool_call', result['reply'])

    def test_json_gateway_accepts_plain_summary_only_after_content_read(self):
        replies = [json.dumps({'tool_calls': [{'name': 'lesson', 'arguments': {'concept_id': '__intro__'}}]}),
                   '先阅读条件判断导学，再尝试练习。']
        def fake(request, timeout):
            return io.BytesIO(json.dumps({'choices': [{'finish_reason': 'stop',
                'message': {'content': replies.pop(0)}}]}).encode())
        result = run_agent(self.engine, empty_state(), '怎么开始', [], 'zh',
                          dict(self.settings, AI_AGENT_MODE='json'), lambda: True, fake)
        self.assertEqual(result['reply'], '先阅读条件判断导学，再尝试练习。')
        self.assertEqual(result['actions'], [])
        self.assertEqual(result['trace'][-1], {'tool': 'lesson', 'status': 'ok'})

    def test_json_gateway_rejects_textual_tool_markup(self):
        def fake(request, timeout):
            content = json.dumps({'reply': '<tool_call>inspect_progress()</arg_value>'})
            return io.BytesIO(json.dumps({'choices': [{'finish_reason': 'stop',
                'message': {'content': content}}]}).encode())
        with self.assertRaises(ValueError):
            run_agent(self.engine, empty_state(), '练习循环', [], 'zh',
                      dict(self.settings, AI_AGENT_MODE='json'), lambda: True, fake)

    def test_model_observes_then_selects_and_opens(self):
        seen = []
        def call(name, args, ident):
            return dict(id=ident, type='function', function=dict(name=name, arguments=json.dumps(args)))
        replies = [
            {'role': 'assistant', 'tool_calls': [call('progress', {}, '1')]},
            {'role': 'assistant', 'tool_calls': [call('lesson', {'concept_id': '__intro__'}, '2')]},
            {'role': 'assistant', 'tool_calls': [call('open_content', {'kind': 'lesson', 'id': '__intro__'}, '3')]},
            {'role': 'assistant', 'content': 'Start with the introduction.'},
        ]
        def opener(request, timeout):
            payload = json.loads(request.data); seen.append(payload)
            if len(seen) == 2:
                self.assertEqual(payload['messages'][-1]['role'], 'tool')
                self.assertIn('courses', json.loads(payload['messages'][-1]['content']))
            reply = replies[len(seen)-1]
            return io.BytesIO(json.dumps({'choices': [{'message': reply, 'finish_reason': 'tool_calls' if 'tool_calls' in reply else 'stop'}]}).encode())
        state = empty_state()
        result = run_agent(self.engine, state, 'Help me begin', [], 'en', self.settings, lambda: True, opener)
        self.assertEqual(len(seen), 4)
        self.assertEqual(result['actions'], [{'kind': 'lesson', 'id': '__intro__'}])
        self.assertEqual([x['tool'] for x in result['trace']], ['progress', 'lesson', 'open_content'])
        self.assertEqual(state, empty_state())

    def test_tools_validate_ids_locking_and_single_action(self):
        tools = AgentTools(self.engine, empty_state())
        for name, args in [('shell', {}), ('lesson', {'concept_id': 'missing'}), ('progress', {'extra': 'bad'}), ('open_content', {'kind': 'lesson', 'id': '__intro__'})]:
            with self.assertRaises(ValueError): tools.execute(name, args)
        cid = next(iter(self.engine.concepts))
        tools.execute('lesson', {'concept_id': cid})
        with self.assertRaises(ValueError): tools.execute('open_content', {'kind': 'lesson', 'id': cid})
        tools.execute('lesson', {'concept_id': '__intro__'})
        tools.execute('open_content', {'kind': 'lesson', 'id': '__intro__'})
        with self.assertRaises(ValueError): tools.execute('open_content', {'kind': 'lesson', 'id': '__intro__'})

    def test_recommendation_has_no_answer_keys(self):
        tools = AgentTools(self.engine, empty_state()); rows = tools.execute('recommend', {})
        self.assertTrue(rows)
        self.assertNotIn(self.engine.questions[0]['id'], [r['id'] for r in rows])
        self.assertTrue(all('answer' not in r and 'misconceptions' not in r for r in rows))
        self.assertTrue(tools.execute('coding', {}))

    def test_rate_limit_prevents_network(self):
        def never(*a, **k): self.fail('Network must not be called')
        with self.assertRaises(RuntimeError): run_agent(self.engine, empty_state(), 'go', [], 'zh', self.settings, lambda: False, never)

    def test_tool_budget_stops_unbounded_model(self):
        count = []
        def opener(*args, **kwargs):
            count.append(1)
            calls = [dict(id=str(i), type='function', function=dict(name='progress', arguments='{}')) for i in range(9)]
            return io.BytesIO(json.dumps({'choices': [{'message': {'tool_calls': calls}}]}).encode())
        with self.assertRaises(RuntimeError): run_agent(self.engine, empty_state(), 'go', [], 'zh', self.settings, lambda: True, opener)
        self.assertEqual(len(count), 1)


    def scripted_model(self, replies):
        """Supply observations to the real loop, retaining each outgoing request."""
        requests = []
        responses = iter(replies)
        def opener(request, timeout):
            payload = json.loads(request.data)
            requests.append(payload)
            reply = next(responses)
            if isinstance(reply, Exception):
                raise reply
            finish = 'tool_calls' if reply.get('tool_calls') else 'stop'
            return io.BytesIO(json.dumps({'choices': [{'message': reply, 'finish_reason': finish}]}).encode())
        return opener, requests

    @staticmethod
    def tool_reply(name, arguments, ident='tool-1'):
        return dict(role='assistant', tool_calls=[dict(id=ident, type='function',
                    function=dict(name=name, arguments=json.dumps(arguments)))])

    def test_rejected_action_returns_observation_and_model_recovers(self):
        """A model cannot open uninspected content, but can correct its next step."""
        opener, requests = self.scripted_model([
            self.tool_reply('open_content', dict(kind='lesson', id='__intro__'), 'bad'),
            self.tool_reply('lesson', dict(concept_id='__intro__'), 'inspect'),
            self.tool_reply('open_content', dict(kind='lesson', id='__intro__'), 'retry'),
            dict(role='assistant', content='The introduction is ready.'),
        ])
        result = run_agent(self.engine, empty_state(), 'Start', [], 'en', self.settings, lambda: True, opener)
        observation = requests[1]['messages'][-1]
        self.assertEqual(observation['role'], 'tool')
        self.assertEqual(observation['tool_call_id'], 'bad')
        self.assertIn('error', json.loads(observation['content']))
        self.assertEqual([x['status'] for x in result['trace']], ['rejected', 'ok', 'ok'])
        self.assertEqual(result['actions'], [dict(kind='lesson', id='__intro__')])

    def test_history_is_bounded_and_credentials_stay_out_of_model_payload(self):
        history = [dict(role='user', text=f'Previous message {i}') for i in range(12)]
        opener, requests = self.scripted_model([dict(role='assistant', content='What would you like to learn?')])
        settings = dict(self.settings, TEAM_ACCESS_CODE='private-team-code')
        result = run_agent(self.engine, empty_state(), 'Help', history, 'en', settings, lambda: True, opener)
        messages = requests[0]['messages']
        self.assertEqual([x['content'] for x in messages[1:-1]], [x['text'] for x in history[-8:]])
        payload = json.dumps(requests[0])
        self.assertNotIn(settings['OPENAI_API_KEY'], payload)
        self.assertNotIn(settings['TEAM_ACCESS_CODE'], payload)
        self.assertEqual(result['actions'], [])

    def test_final_round_disables_tools_and_charges_each_model_call(self):
        replies = [self.tool_reply('progress', {}, str(i)) for i in range(4)]
        replies.append(dict(role='assistant', content='Here is your next step.'))
        opener, requests = self.scripted_model(replies)
        allowances = []
        def allow():
            allowances.append(True)
            return True
        result = run_agent(self.engine, empty_state(), 'Plan', [], 'en', self.settings, allow, opener)
        self.assertEqual(len(requests), 5)
        self.assertEqual(len(allowances), 5)
        self.assertNotIn('tools', requests[-1])
        self.assertNotIn('tool_choice', requests[-1])
        self.assertEqual(requests[-1]['thinking'], {'type': 'disabled'})
        self.assertEqual(len(result['trace']), 4)

    def test_timeout_after_preparing_action_does_not_return_partial_success(self):
        """Only a completed turn may deliver browser actions; progress stays intact."""
        from copy import deepcopy
        state = empty_state(); original = deepcopy(state)
        opener, _ = self.scripted_model([
            self.tool_reply('lesson', dict(concept_id='__intro__'), 'inspect'),
            self.tool_reply('open_content', dict(kind='lesson', id='__intro__'), 'open'),
            TimeoutError('simulated model timeout'),
        ])
        with self.assertRaises(TimeoutError):
            run_agent(self.engine, state, 'Start', [], 'en', self.settings, lambda: True, opener)
        self.assertEqual(state, original)

    def test_incomplete_or_oversized_model_output_is_rejected(self):
        for content in ['', ' ' * 4, 'x' * 10001]:
            with self.subTest(length=len(content)):
                opener, _ = self.scripted_model([dict(role='assistant', content=content)])
                with self.assertRaises(ValueError):
                    run_agent(self.engine, empty_state(), 'Help', [], 'en', self.settings, lambda: True, opener)
        def oversized(*args, **kwargs):
            return io.BytesIO(b'x' * 131073)
        with self.assertRaisesRegex(ValueError, 'too large'):
            run_agent(self.engine, empty_state(), 'Help', [], 'en', self.settings, lambda: True, oversized)

if __name__ == '__main__': unittest.main()
