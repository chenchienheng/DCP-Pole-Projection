"""Shared local reader-basis parsing and bounded CI checks; no admission claim."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def strict_json_loads(raw: bytes | str):
    """Reject ambiguous object keys and non-JSON numeric constants."""
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'DUPLICATE_JSON_KEY:{key}')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f'INVALID_JSON_CONSTANT:{value}')

    return json.loads(raw, object_pairs_hook=unique_keys,
                      parse_constant=invalid_constant)


def validated_paths(root: Path, entries, label: str,
                    *, nonempty: bool = False) -> frozenset[str]:
    """Validate one declaration; overlap between separate views is allowed."""
    if not isinstance(entries, list) or (nonempty and not entries):
        raise ValueError(f'CURRENT_SURFACE_POINTER_LIST_INVALID:{label}')
    paths = set()
    for entry in entries:
        if not isinstance(entry, str) or not entry or entry != entry.strip():
            raise ValueError(f'CURRENT_SURFACE_POINTER_INVALID:{label}')
        path = PurePosixPath(entry)
        if (path.is_absolute() or '..' in path.parts or '\\' in entry
                or ':' in entry):
            raise ValueError(f'CURRENT_SURFACE_POINTER_OUTSIDE_REPOSITORY:{entry}')
        if path.as_posix() != entry or entry == '.':
            raise ValueError(f'CURRENT_SURFACE_POINTER_NONCANONICAL:{entry}')
        if entry in paths:
            raise ValueError(f'CURRENT_SURFACE_POINTER_DUPLICATE:{label}:{entry}')
        target = (root / entry).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f'CURRENT_SURFACE_POINTER_OUTSIDE_REPOSITORY:{entry}')
        if not target.is_file():
            raise ValueError(f'CURRENT_SURFACE_POINTER_MISSING:{entry}')
        paths.add(entry)
    return frozenset(paths)


def read_manifest_basis(root: Path, manifest: Path):
    """Read/hash the same bytes once; shared by CI and the metabolism scanner.

    Validity is repository-local only, not external Current or authority. The CI
    caller separately checks public boundaries, additional views and candidate
    presence. A scanner can therefore use a minimal reader-only declaration.
    """
    root = root.resolve()
    requested = manifest if manifest.is_absolute() else root / manifest
    metadata = {'status': 'UNRESOLVED', 'manifest': None, 'sha256': None}
    try:
        resolved = requested.resolve()
        metadata['manifest'] = resolved.relative_to(root).as_posix()
        raw = resolved.read_bytes()
        metadata['sha256'] = hashlib.sha256(raw).hexdigest()
        data = strict_json_loads(raw)
        if not isinstance(data, dict):
            raise ValueError('CURRENT_SURFACE_MANIFEST_NOT_OBJECT')
        paths = validated_paths(root, data.get('reader_priority'),
                                'reader_priority', nonempty=True)
        metadata['status'] = 'LOCAL_DECLARATION_VALID_NOT_NATIVE_ADMISSION'
        return data, paths, metadata
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        metadata['status'] = 'UNRESOLVED_NO_READER_ELIGIBILITY'
        metadata['error'] = type(exc).__name__ + ': ' + str(exc)
        return None, frozenset(), metadata


def main() -> None:
    root = Path.cwd().resolve()
    manifest, readers, basis = read_manifest_basis(
        root, Path('CURRENT-SURFACE-MANIFEST.json'))
    if manifest is None:
        raise SystemExit('CURRENT_SURFACE_BASIS_INVALID:' + basis['error'])
    for key in ('runtime', 'native_source_root', 'repo_is_pole_authority'):
        if manifest.get(key) is not False:
            raise SystemExit(f'PUBLIC_PROJECTION_BOUNDARY_INVALID:{key}')
    surfaces = manifest.get('current_public_surfaces')
    if not isinstance(surfaces, dict):
        raise SystemExit('CURRENT_PUBLIC_SURFACES_INVALID')
    paths = set(readers)
    try:
        for label, entries in surfaces.items():
            paths.update(validated_paths(root, entries, label))
        for entry in sorted(paths):
            if Path(entry).suffix == '.json':
                strict_json_loads((root / entry).read_bytes())
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        raise SystemExit(f'CURRENT_SURFACE_INVALID:{exc}') from exc
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


if __name__ == '__main__':
    main()
