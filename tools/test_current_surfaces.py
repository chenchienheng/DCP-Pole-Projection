"""Synthetic regression checks for the same classifier invoked by CI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECK = Path(__file__).with_name('check_current_surfaces.py').resolve()


class CurrentSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {
            'runtime': False, 'native_source_root': False, 'repo_is_pole_authority': False,
            'reader_priority': ['README.md'],
            'current_public_surfaces': {'machine': ['data.json']},
        }
        self.write('README.md', 'fixture')
        self.write('data.json', '{}')

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def run_check(self):
        self.write('CURRENT-SURFACE-MANIFEST.json', json.dumps(self.manifest))
        output = self.root / 'github-output'
        result = subprocess.run([sys.executable, str(CHECK)], cwd=self.root,
                                env={**os.environ, 'GITHUB_OUTPUT': str(output)},
                                text=True, capture_output=True)
        return result, output.read_text() if output.exists() else ''

    def test_current_only_is_not_candidate_pass(self):
        result, output = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, 'candidate=false\n')
        self.assertIn('NOT_APPLICABLE_NOT_PASS', result.stdout)

    def test_complete_candidate_requires_tests(self):
        for name in ['dcp_kernel/example.py', 'contracts/a.json', 'fixtures/a.json',
                     'tests/test_example.py', 'pyproject.toml']:
            self.write(name, '{}')
        result, output = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, 'candidate=true\n')
        self.assertIn('CANDIDATE_TESTS_REQUIRED', result.stdout)

    def test_partial_candidate_fails_without_output(self):
        self.write('dcp_kernel/example.py', '')
        result, output = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('INCOMPLETE_CANDIDATE_SURFACE', result.stderr)
        self.assertEqual(output, '')

    def test_empty_candidate_directories_fail(self):
        for name in ['dcp_kernel', 'contracts', 'fixtures', 'tests']:
            (self.root / name).mkdir()
        self.write('pyproject.toml', '')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('EMPTY_OR_INVALID_CANDIDATE_SURFACE', result.stderr)

    def test_missing_declared_pointer_fails(self):
        self.manifest['reader_priority'].append('missing.md')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('CURRENT_SURFACE_POINTER_MISSING', result.stderr)

    def test_invalid_current_json_fails(self):
        self.write('data.json', '{')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)

    def test_escape_pointer_fails(self):
        self.manifest['reader_priority'].append('../outside.md')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('OUTSIDE_REPOSITORY', result.stderr)

    def test_missing_boundary_fails(self):
        del self.manifest['runtime']
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PUBLIC_PROJECTION_BOUNDARY_INVALID', result.stderr)


if __name__ == '__main__':
    unittest.main()
