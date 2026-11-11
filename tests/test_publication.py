import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('publication', Path(__file__).resolve().parents[1] / 'scripts/check_publication.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        for name in module.REQUIRED:
            (self.root / name).write_text('Project documentation\n')

    def check(self):
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        return module.check(self.root)

    def test_real_project_and_upstream_attribution_are_allowed(self):
        (self.root / 'README.md').write_text('# Tool\n\nA useful tool. Third-party components retain their licenses.\n')
        (self.root / 'vendor').mkdir()
        (self.root / 'vendor/README.md').write_text('/Users/upstream/build instructions\n')
        self.assertEqual([], self.check())

    def test_import_report_and_incomplete_scaffold_block_publication(self):
        (self.root / 'README.md').write_text('独立脱敏源码版本，使用中性 Studio 品牌。\n')
        (self.root / 'SANITIZED-DISTRIBUTION.md').write_text('export notes')
        self.assertEqual(2, len(self.check()))
        (self.root / 'SANITIZED-DISTRIBUTION.md').unlink()
        (self.root / 'README.md').write_text('首次对外发布前，请补全以下内容并删除提示文字。')
        self.assertEqual(1, len(self.check()))

    def test_large_bundle_and_vendor_secrets_are_not_skipped_or_echoed(self):
        value = 'ghp_' + 'A' * 36
        (self.root / 'vendor').mkdir()
        (self.root / 'vendor/bundle.js').write_text(' ' * 2_100_000 + value)
        errors = self.check()
        self.assertEqual(1, len(errors))
        self.assertNotIn(value, '\n'.join(errors))

    def test_foreign_runtime_and_missing_license_block(self):
        (self.root / 'LICENSE').unlink()
        (self.root / 'dist').mkdir()
        (self.root / 'dist/client.js').write_text('fetch("https://hm.baidu.com/track")')
        self.assertEqual(2, len(self.check()))

    def test_new_project_rejects_public_scaffold_before_any_network_call(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/new_project.py'
        import sys
        result = subprocess.run([sys.executable, str(script), 'demo', '--description', 'Demo', '--visibility', 'public'],
                                capture_output=True, text=True, cwd=self.root)
        self.assertEqual(2, result.returncode)
        self.assertIn('invalid choice', result.stderr)
        self.assertFalse((self.root / 'demo').exists())


if __name__ == '__main__':
    unittest.main()
