"""Bounded pointer/JSON and candidate-presence checks; no semantic/runtime claim."""
import json
import os
from pathlib import Path

manifest = json.loads(Path('CURRENT-SURFACE-MANIFEST.json').read_text(encoding='utf-8'))
for key in ('runtime', 'native_source_root', 'repo_is_pole_authority'):
    if manifest.get(key) is not False:
        raise SystemExit(f'PUBLIC_PROJECTION_BOUNDARY_INVALID:{key}')
paths = set(manifest['reader_priority'])
for entries in manifest['current_public_surfaces'].values():
    paths.update(entries)
if not paths:
    raise SystemExit('CURRENT_SURFACE_POINTERS_EMPTY')
root = Path.cwd().resolve()
for entry in sorted(paths):
    path = Path(entry)
    if path.is_absolute() or '..' in path.parts or not path.resolve().is_relative_to(root):
        raise SystemExit(f'CURRENT_SURFACE_POINTER_OUTSIDE_REPOSITORY:{entry}')
    if not path.is_file():
        raise SystemExit(f'CURRENT_SURFACE_POINTER_MISSING:{entry}')
    if path.suffix == '.json':
        json.loads(path.read_text(encoding='utf-8'))
print(f'CURRENT_SURFACE_POINTERS_CHECKED:{len(paths)}; NOT_SEMANTIC_OR_RUNTIME_PASS')

required = ('dcp_kernel', 'contracts', 'fixtures', 'tests', 'pyproject.toml')
present = [p for p in required if Path(p).exists()]
if present and len(present) != len(required):
    raise SystemExit(f'INCOMPLETE_CANDIDATE_SURFACE:present={present}')
candidate = bool(present)
if candidate:
    for directory, pattern in [('dcp_kernel', '*.py'), ('contracts', '*.json'),
                               ('fixtures', '*.json'), ('tests', 'test*.py')]:
        if not Path(directory).is_dir() or not any(Path(directory).rglob(pattern)):
            raise SystemExit(f'EMPTY_OR_INVALID_CANDIDATE_SURFACE:{directory}')
    if not Path('pyproject.toml').is_file():
        raise SystemExit('INVALID_CANDIDATE_PROJECT_FILE')
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'candidate={str(candidate).lower()}\n')
print('CANDIDATE_TESTS_REQUIRED' if candidate else 'CANDIDATE_ABSENT:NOT_APPLICABLE_NOT_PASS')
