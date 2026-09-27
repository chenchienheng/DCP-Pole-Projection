from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from dcp_kernel.metabolism import assess_paths
from tools.check_current_surfaces import read_manifest_basis


def repository_paths(root: Path) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    ]


def load_reader_basis(root: Path, manifest: Path) -> tuple[frozenset[str], dict]:
    """Compatibility entry using the same structural reader parser as CI."""
    _data, paths, metadata = read_manifest_basis(root, manifest)
    return paths, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path,
                        default=Path("CURRENT-SURFACE-MANIFEST.json"))
    parser.add_argument("--source-ref", default=None,
                        help="Caller-declared source ref; not independently Git-verified")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    reader_paths, reader_basis = load_reader_basis(root, args.manifest)
    paths = [name for name in repository_paths(root)
             if (root / name).resolve() != output.resolve()]
    assessments = assess_paths(paths, current_reader_paths=reader_paths)
    role_counts = Counter(item.role.value for item in assessments)
    disposition_counts = Counter(
        item.proposed_disposition.value
        for item in assessments
    )
    risk_counts = Counter(
        risk.value
        for item in assessments
        for risk in item.name_risks
        if risk.value != "NAME_NEUTRAL"
    )

    payload = {
        "scan_id": "DCP-REPOSITORY-METABOLISM-SCAN-R1",
        "repository_role": "PUBLIC_DCP_PROJECTION_CARRIER",
        "branch": None,
        "source_ref": args.source_ref,
        "source_ref_evidence": ("CALLER_DECLARED_NOT_GIT_VERIFIED"
                                if args.source_ref else "UNKNOWN"),
        "reader_basis": reader_basis,
        "runtime": False,
        "promotion": False,
        "destructive_action_authorized": False,
        "method": "path_role_hints_with_explicit_local_reader_basis",
        "limitations": [
            "name/path classification cannot prove semantic equivalence",
            "manifest reader membership is not Native Current or external authority",
            "missing or invalid reader basis grants no normal-reader eligibility",
            "active caller and rebuild dependency require later graph inspection",
            "reclaim candidate never authorizes deletion",
            "GitHub placement does not establish Native owner or Current",
        ],
        "summary": {
            "artifact_count": len(assessments),
            "role_counts": dict(sorted(role_counts.items())),
            "disposition_counts": dict(
                sorted(disposition_counts.items())
            ),
            "name_risk_counts": dict(sorted(risk_counts.items())),
        },
        "artifacts": [
            item.to_dict()
            for item in assessments
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
