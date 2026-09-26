from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from dcp_kernel.reference_census import DependencySignal, scan_text_map


TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".toml", ".ini", ".cfg", ".sh",
}
FAMILIES = (
    "00_meta",
    "00_mother-law",
    "01_native-board",
    "01_runtime-spine",
    "02_runtime-ops",
    "02_translation-layer",
    "03_board-orchestration",
    "03_field-governance",
    "04_adapter-layer",
    "04_interface-layer",
    "05_XLEN_Reserve_Unenabled",
    "05_topology",
)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "artifacts"}


def collect_text_files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        try:
            result[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return result


def build_payload(root: Path) -> dict[str, object]:
    observations = scan_text_map(collect_text_files(root), FAMILIES)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    dependency_by_family: dict[str, Counter[str]] = defaultdict(Counter)
    rows = []
    for item in observations:
        classification = item.classification.value
        dependency_signal = item.dependency_signal.value
        by_family[item.target_family][classification] += 1
        dependency_by_family[item.target_family][dependency_signal] += 1
        rows.append(
            {
                "caller_path": item.caller_path,
                "target_family": item.target_family,
                "classification": classification,
                "dependency_signal": dependency_signal,
                "excerpt": item.excerpt,
            }
        )

    summary = {}
    for family in FAMILIES:
        counts = by_family[family]
        dependency_counts = dependency_by_family[family]
        live = counts.get("LIVE_CALLER", 0)
        unknown = counts.get("UNKNOWN_HOLD", 0)
        rebuild_relevant = (
            dependency_counts.get(DependencySignal.REBUILD_RELEVANT.value, 0)
            + dependency_counts.get(DependencySignal.REBUILD_AND_WAKE_RELEVANT.value, 0)
            + dependency_counts.get(DependencySignal.UNKNOWN.value, 0)
        )
        wake_relevant = (
            dependency_counts.get(DependencySignal.WAKE_ROUTING_RELEVANT.value, 0)
            + dependency_counts.get(DependencySignal.REBUILD_AND_WAKE_RELEVANT.value, 0)
            + dependency_counts.get(DependencySignal.UNKNOWN.value, 0)
        )
        summary[family] = {
            "live_caller_count": live,
            "audit_reference_count": counts.get("AUDIT_REFERENCE", 0),
            "lineage_pointer_count": counts.get("LINEAGE_POINTER", 0),
            "self_reference_count": counts.get("SELF_REFERENCE", 0),
            "unknown_hold_count": unknown,
            "rebuild_relevant_reference_count": rebuild_relevant,
            "wake_routing_relevant_reference_count": wake_relevant,
            "caller_absence_on_scanned_text_surface": live == 0 and unknown == 0,
            "rebuild_withdrawal_candidate_on_scanned_text_surface": rebuild_relevant == 0,
            "wake_routing_withdrawal_candidate_on_scanned_text_surface": wake_relevant == 0,
            "reclaim_ready": False,
        }

    return {
        "artifact_role": "BOUNDED_REFERENCE_AND_WITHDRAWAL_CENSUS_EVIDENCE",
        "runtime": False,
        "promotion": False,
        "destructive_action_authorized": False,
        "families": list(FAMILIES),
        "summary": summary,
        "observations": rows,
        "claim_boundary": [
            "SEARCH_HIT_IS_NOT_CURRENT",
            "AUDIT_REFERENCE_IS_NOT_LIVE_CALLER",
            "UNKNOWN_REFERENCE_IS_HOLD",
            "KEYWORD_RELEVANCE_IS_REVIEW_SIGNAL_NOT_PROVEN_OPERATIONAL_DEPENDENCY",
            "CALLER_ABSENCE_ONLY_COVERS_SCANNED_TEXT_SURFACE",
            "REBUILD_OR_WAKE_KEYWORD_ABSENCE_DOES_NOT_PROVE_RUNTIME_DEPENDENCY_ABSENCE",
            "NON_TEXT_PLACEMENT_OR_RUNTIME_WAKE_REQUIRES_SEPARATE_PHYSICAL_REVIEW",
            "RECLAIM_READY_IS_NEVER_INFERRED_BY_THIS_CENSUS",
        ],
        "required_followup": [
            "review live and unknown observations",
            "review rebuild/wake relevant observations",
            "confirm non-text/runtime/generated dependencies where applicable",
            "confirm workflow/template/physical placement wake where applicable",
            "resolve family-specific provenance retention debt",
            "pair each withdrawn legitimate capability with successor operability evidence or OPERABILITY_GAP",
            "only then consider pooled reclaim review",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = build_payload(root)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
