from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from dcp_kernel.metabolism import assess_paths


def repository_paths(root: Path) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    assessments = assess_paths(repository_paths(root))
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
        "branch": "ideas/6d-dispatch-projection-20260816",
        "runtime": False,
        "promotion": False,
        "destructive_action_authorized": False,
        "method": "path_and_artifact_role_candidate_classification",
        "limitations": [
            "name/path classification cannot prove semantic equivalence",
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

    output = args.output
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
