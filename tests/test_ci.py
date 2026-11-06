"""CI trust checks: failure propagation, model isolation and private archive rejection."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec=importlib.util.spec_from_file_location('ci_checks',Path(__file__).resolve().parents[1]/'scripts/ci_checks.py')
ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)

class CIPipelineTests(unittest.TestCase):
    def test_nonzero_test_exit_is_not_hidden_by_report_writing(self):
        with tempfile.TemporaryDirectory() as directory,contextlib.redirect_stdout(io.StringIO()):
            report=Path(directory)/'nested/result.txt'
            code=ci.execute([sys.executable,'-c','print("failed check"); raise SystemExit(7)'],report)
            self.assertEqual(code,7)
            self.assertIn('failed check',report.read_text(encoding='utf-8'))

    def test_staging_explicitly_disables_inherited_paid_credentials(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only-secret','TEAM_ACCESS_CODE':'test-only-team-code','PUBLIC_ORIGIN':'https://example.invalid'}):
            env=ci.isolated_environment()
            self.assertEqual(env['OPENAI_API_KEY'],'')
            self.assertEqual(env['TEAM_ACCESS_CODE'],'')
            self.assertEqual(env['PUBLIC_ORIGIN'],'')
            self.assertEqual(os.environ['OPENAI_API_KEY'],'test-only-secret')

    def test_delivery_audit_rejects_private_and_traversal_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/'delivery.zip'
            for name in ['group8/config.local.json','group8/.env','group8/runtime/learning.sqlite3','../private.txt','group8/.git/config']:
                with self.subTest(name=name):
                    with zipfile.ZipFile(archive,'w') as z:z.writestr(name,'test-only')
                    with self.assertRaises(ValueError):ci.audit_archive(archive)
            with zipfile.ZipFile(archive,'w') as z:z.writestr('group8/README.md','safe example')
            ci.audit_archive(archive)

if __name__=='__main__':unittest.main()
