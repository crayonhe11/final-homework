import json,os,subprocess,unittest
from unittest.mock import patch,MagicMock
from edu.runner import runner_backend,run_code
from edu.docker_runner import create_command,docker_environment,run_container
from edu.coding import load_tasks

class CrossPlatformTests(unittest.TestCase):
    def test_backend_selection_and_fail_closed(self):
        with patch.dict(os.environ,{'EDU_CODE_BACKEND':'auto'}),patch('edu.runner.shutil.which',return_value='docker'):
            for name in ('Windows','Linux'):
                with patch('edu.runner.platform.system',return_value=name): self.assertEqual(runner_backend(),'docker')
            with patch('edu.runner.platform.system',return_value='Darwin'),patch('edu.runner.Path.exists',return_value=True): self.assertEqual(runner_backend(),'native')
        with patch.dict(os.environ,{'EDU_CODE_BACKEND':'native'}),patch('edu.runner.platform.system',return_value='Windows'):
            self.assertIsNone(runner_backend())
    def test_no_docker_does_not_execute(self):
        with patch('edu.runner.runner_backend',return_value=None),patch('edu.runner.subprocess.Popen') as launch:
            t=next(iter(load_tasks().values()));self.assertEqual(run_code(t,t['solution'])['status'],'unavailable');launch.assert_not_called()
    def test_container_controls_and_no_secret_environment(self):
        cmd=create_command('docker','edu-python-test','print(1)')
        for key,value in [('--network','none'),('--memory','128m'),('--memory-swap','128m'),('--user','65534:65534'),('--pull','never'),('--pids-limit','32')]:
            self.assertEqual(cmd[cmd.index(key)+1],value)
        self.assertIn('--read-only',cmd);self.assertNotIn('--mount',cmd);self.assertNotIn('--privileged',cmd)
        with patch.dict(os.environ,{'MOONSHOT_API_KEY':'fake-secret','PATH':'path','SystemRoot':'C:/Windows'},clear=True):
            env=docker_environment();self.assertNotIn('MOONSHOT_API_KEY',env);self.assertEqual(env['SystemRoot'],'C:/Windows')
    def test_docker_result_is_judged_and_container_cleaned(self):
        t=load_tasks()['rocket_countdown'];fake=MagicMock();fake.returncode=0
        fake.communicate.return_value=(json.dumps({'status':'ok','values':[c['expected'] for c in t['tests']],'stdout':''}),'');fake.poll.return_value=0
        with patch('edu.runner.runner_backend',return_value='docker'),patch('edu.docker_runner.shutil.which',return_value='docker'),patch('edu.docker_runner.subprocess.run',return_value=subprocess.CompletedProcess([],0,'','')) as run,patch('edu.docker_runner.subprocess.Popen',return_value=fake):
            result=run_code(t,t['solution']);self.assertTrue(result['passed'])
            self.assertEqual(run.call_args_list[-1].args[0][1:3],['rm','--force'])
            self.assertEqual(len(json.loads(fake.communicate.call_args.args[0])['args']),len(t['tests']))
    def test_timeout_removes_container_and_kills_cli(self):
        fake=MagicMock();fake.communicate.side_effect=[subprocess.TimeoutExpired('docker',.1),('','')];fake.poll.return_value=None
        with patch('edu.docker_runner.shutil.which',return_value='docker'),patch('edu.docker_runner.subprocess.run',return_value=subprocess.CompletedProcess([],0,'','')) as run,patch('edu.docker_runner.subprocess.Popen',return_value=fake):
            result=run_container('worker','payload',.1);self.assertEqual(result['error_status'],'timeout')
            fake.kill.assert_called_once();self.assertEqual(run.call_args.args[0][1:3],['rm','--force'])
    def test_unavailable_engine_and_cleanup_failure(self):
        with patch('edu.docker_runner.shutil.which',return_value='docker'),patch('edu.docker_runner.subprocess.run',return_value=subprocess.CompletedProcess([],1,'','daemon unavailable')),patch('edu.docker_runner.subprocess.Popen') as launch:
            result=run_container('worker','payload',1);self.assertEqual(result['error_status'],'unavailable');self.assertIn('清理',result['error']);launch.assert_not_called()

@unittest.skipUnless(os.getenv('EDU_RUN_DOCKER_TESTS')=='1','需要已运行的Docker及预先下载的镜像')
class DockerIntegrationTests(unittest.TestCase):
    def test_real_reference_answers_and_timeout(self):
        with patch.dict(os.environ,{'EDU_CODE_BACKEND':'docker'}):
            for t in load_tasks().values():
                result=run_code(t,t['solution']);self.assertTrue(result['passed'],result)
            t=load_tasks()['rocket_countdown'];result=run_code(t,'def countdown(start):\n    while True:\n        pass',timeout=.5)
            self.assertIn(result['status'],('timeout','resource_limit'))
    def test_real_container_write_and_network_limits(self):
        worker="""import socket
try:
    open('/tmp/edu-test','w').write('test')
    print('write-allowed')
except OSError: print('write-denied')
s=socket.socket();s.settimeout(1)
try:
    s.connect(('1.1.1.1',53));print('network-allowed')
except OSError: print('network-denied')
"""
        result=run_container(worker,'',4)
        self.assertNotIn('error_status',result,result);self.assertEqual(result['returncode'],0)
        self.assertIn('write-denied',result['stdout']);self.assertIn('network-denied',result['stdout'])
