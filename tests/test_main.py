"""Real entry-point tests; no duplicate example implementation and no paid calls."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import main as entry
from backend.domain import ROOT

class EntryPointTests(unittest.TestCase):
    def test_help_describes_real_entry_options(self):
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'main.py'),'--help'],capture_output=True,encoding='utf-8',timeout=5)
        self.assertEqual(result.returncode,0)
        for option in ['--host','--port','--db','--open']:self.assertIn(option,result.stdout)

    def test_invalid_port_is_rejected_before_server_creation(self):
        for port in ['-1','65536']:
            with self.subTest(port=port),patch('main.create_server') as create,contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as err:entry.main(['--port',port])
                self.assertEqual(err.exception.code,2)
                create.assert_not_called()

    def test_missing_web_distribution_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory,patch('main.ROOT',Path(directory)),patch('main.create_server') as create:
            error=io.StringIO()
            with contextlib.redirect_stderr(error),self.assertRaises(SystemExit) as err:entry.main([])
            self.assertEqual(err.exception.code,2)
            self.assertIn('完整解压项目',error.getvalue())
            create.assert_not_called()

    def test_bind_failure_is_reported_without_traceback(self):
        error=io.StringIO()
        with patch('main.create_server',side_effect=OSError('Address already in use')),contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit) as err:entry.main([])
        self.assertEqual(err.exception.code,2)
        self.assertIn('Address already in use',error.getvalue())
        self.assertNotIn('Traceback',error.getvalue())

    def test_open_uses_bound_port_and_keyboard_interrupt_closes_server(self):
        server=MagicMock(server_port=9876)
        server.serve_forever.side_effect=KeyboardInterrupt
        with patch('main.create_server',return_value=server) as create,patch('main.webbrowser.open') as browser,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(entry.main(['--port','0','--open']),0)
        self.assertEqual(create.call_args.args[:2],('127.0.0.1',0))
        browser.assert_called_once_with('http://127.0.0.1:9876/')
        server.server_close.assert_called_once()

    def test_host_port_and_database_are_forwarded(self):
        server=MagicMock(server_port=8011)
        server.serve_forever.side_effect=KeyboardInterrupt
        with tempfile.TemporaryDirectory() as directory,patch('main.create_server',return_value=server) as create,patch('main.webbrowser.open') as browser,contextlib.redirect_stdout(io.StringIO()):
            database=Path(directory)/'learning.sqlite3'
            self.assertEqual(entry.main(['--host','0.0.0.0','--port','8011','--db',str(database)]),0)
            create.assert_called_once_with('0.0.0.0',8011,database)
            browser.assert_not_called()
        server.server_close.assert_called_once()

if __name__=='__main__':unittest.main()
