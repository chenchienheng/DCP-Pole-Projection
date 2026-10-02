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
        return self.run_raw(json.dumps(self.manifest))

    def run_raw(self, raw):
        self.write('CURRENT-SURFACE-MANIFEST.json', raw)
        output = self.root / 'github-output'
        output.unlink(missing_ok=True)
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


    def test_duplicate_reader_declaration_fails(self):
        self.manifest['reader_priority'].append('README.md')
        result, output = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('POINTER_DUPLICATE', result.stderr)
        self.assertEqual(output, '')

    def test_duplicate_boundary_key_does_not_use_last_value(self):
        raw = json.dumps(self.manifest).replace('"runtime": false',
                                               '"runtime": true, "runtime": false')
        result, output = self.run_raw(raw)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DUPLICATE_JSON_KEY:runtime', result.stderr)
        self.assertEqual(output, '')

    def test_duplicate_nested_view_key_fails(self):
        raw = json.dumps(self.manifest).replace('"machine": ["data.json"]',
            '"machine": ["missing.md"], "machine": ["data.json"]')
        result, _ = self.run_raw(raw)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DUPLICATE_JSON_KEY:machine', result.stderr)

    def test_invalid_reader_shapes_fail_without_output(self):
        self.write('a', 'fixture')
        for value in ('a', [], None, True, {'a': 1}, [True], ['']):
            with self.subTest(value=value):
                self.manifest['reader_priority'] = value
                result, output = self.run_check()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output, '')

    def test_noncanonical_paths_fail(self):
        for entry in ('./README.md', 'dir//entry.md', 'README.md ', 'README.md/'):
            with self.subTest(entry=entry):
                self.manifest['reader_priority'] = [entry]
                result, output = self.run_check()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output, '')

    def test_string_view_is_not_a_list_of_character_paths(self):
        self.write('a', 'fixture')
        self.manifest['current_public_surfaces'] = {'machine': 'a'}
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('POINTER_LIST_INVALID', result.stderr)

    def test_duplicate_pointer_within_one_view_fails(self):
        self.manifest['current_public_surfaces']['machine'].append('data.json')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('POINTER_DUPLICATE', result.stderr)

    def test_shared_pointer_between_views_is_legitimate(self):
        self.manifest['current_public_surfaces'] = {
            'human': ['README.md'], 'professional': ['README.md'], 'machine': ['data.json']}
        result, output = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output, 'candidate=false\n')
        self.assertIn('POINTERS_CHECKED:2', result.stdout)

    def test_target_json_duplicate_keys_fail(self):
        self.write('data.json', '{"state":"old","state":"new"}')
        result, _ = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DUPLICATE_JSON_KEY:state', result.stderr)

    def test_non_json_constants_fail(self):
        for token in ('NaN', 'Infinity', '-Infinity'):
            with self.subTest(token=token):
                raw = json.dumps(self.manifest)[:-1] + ', "unqualified": ' + token + '}'
                result, output = self.run_raw(raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('INVALID_JSON_CONSTANT', result.stderr)
                self.assertEqual(output, '')

    def test_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / 'outside.md'
            outside.write_text('fixture')
            (self.root / 'link.md').symlink_to(outside)
            self.manifest['reader_priority'] = ['link.md']
            result, output = self.run_check()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('OUTSIDE_REPOSITORY', result.stderr)
            self.assertEqual(output, '')

    def test_import_is_side_effect_free_and_reader_only_basis_stays_supported(self):
        source = (
            'import sys; from pathlib import Path; '
            'sys.path.insert(0, sys.argv[1]); '
            'from check_current_surfaces import read_manifest_basis; '
            'data, readers, meta = read_manifest_basis(Path.cwd(), Path("reader.json")); '
            'assert readers == frozenset(["README.md"]); '
            'assert meta["status"] == "LOCAL_DECLARATION_VALID_NOT_NATIVE_ADMISSION"; '
            'assert data == {"reader_priority":["README.md"]}; '
            'print("SHARED_PARSER_IMPORTED_WITHOUT_CI_SIDE_EFFECT")')
        self.write('reader.json', '{"reader_priority":["README.md"]}')
        result = subprocess.run([sys.executable, '-c', source, str(CHECK.parent)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'SHARED_PARSER_IMPORTED_WITHOUT_CI_SIDE_EFFECT')


if __name__ == '__main__':
    unittest.main()
