from __future__ import annotations

import argparse
import json
import hashlib
import os
import stat
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from dcp_kernel.reference_census import DependencySignal, scan_text_map
from tools.check_current_surfaces import read_manifest_basis


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


def collect_text_snapshot(
    root: Path, *, excluded_paths: Iterable[Path] = (),
) -> tuple[dict[str, str], dict[str, object]]:
    """Collect a bounded local snapshot, exposing rather than hiding gaps.

    Exclusions are relative to the selected root, not its parent directory
    names. Symlink files/directories are not followed. This is not an atomic
    filesystem snapshot, a sandbox, or proof against adversarial directory
    replacement while scanning.
    """
    root = root.resolve()
    excluded = {
        Path(os.path.abspath(path if path.is_absolute() else root / path))
        for path in map(Path, excluded_paths)
    }
    result: dict[str, str] = {}
    gaps: list[dict[str, str]] = []
    policy_skipped: list[str] = []
    output_skipped = sorted(path.relative_to(root).as_posix()
                            for path in excluded if path.is_relative_to(root))

    def record_gap(path: Path, reason: str) -> None:
        # Report only paths in the selected root; never copy a link target or
        # exception message that might reveal an external filesystem location.
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = "."
        gaps.append({"path": rel, "reason": reason})

    def walk_error(error: OSError) -> None:
        record_gap(Path(error.filename) if error.filename else root,
                   "DIRECTORY_READ_ERROR")

    if not root.is_dir():
        record_gap(root, "ROOT_NOT_DIRECTORY")
    else:
        for directory, dirnames, filenames in os.walk(
                root, topdown=True, onerror=walk_error, followlinks=False):
            directory = Path(directory)
            descend = []
            for name in sorted(dirnames):
                path = directory / name
                if name in SKIP_DIRS:
                    policy_skipped.append(path.relative_to(root).as_posix())
                elif path.is_symlink():
                    record_gap(path, "SYMLINK_DIRECTORY_NOT_SCANNED")
                else:
                    descend.append(name)
            dirnames[:] = descend
            for name in sorted(filenames):
                path = directory / name
                if path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                rel = path.relative_to(root).as_posix()
                if path in excluded:
                    continue
                try:
                    if path.is_symlink():
                        record_gap(path, "SYMLINK_FILE_NOT_SCANNED")
                        continue
                    if not path.resolve(strict=True).is_relative_to(root):
                        record_gap(path, "OUTSIDE_SELECTED_ROOT")
                        continue
                    if not stat.S_ISREG(path.stat().st_mode):
                        record_gap(path, "NON_REGULAR_TEXT_NOT_SCANNED")
                        continue
                    # O_NOFOLLOW also rejects a last-component symlink swap on
                    # platforms that support it; no global isolation is implied.
                    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                    with os.fdopen(descriptor, "rb") as stream:
                        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                            record_gap(path, "NON_REGULAR_TEXT_NOT_SCANNED")
                            continue
                        raw = stream.read()
                    result[rel] = raw.decode("utf-8")
                except UnicodeDecodeError:
                    record_gap(path, "NON_UTF8_TEXT_NOT_SCANNED")
                except (OSError, RuntimeError):
                    record_gap(path, "TEXT_READ_ERROR")

    return result, {
        "scope": "SELECTED_LOCAL_TEXT_POLICY_NOT_ATOMIC_OR_RUNTIME",
        "complete_within_policy": not gaps,
        "gaps": sorted(gaps, key=lambda item: (item["path"], item["reason"])),
        "policy_excluded_directories": sorted(policy_skipped),
        "explicit_output_exclusions": sorted(output_skipped),
    }


def collect_text_files(root: Path) -> dict[str, str]:
    """Compatibility view; absence decisions must use build_payload coverage."""
    files, _coverage = collect_text_snapshot(root)
    return files


def build_payload(root: Path, *, excluded_paths: Iterable[Path] = ()) -> dict[str, object]:
    root = root.resolve()
    files, collection = collect_text_snapshot(root, excluded_paths=excluded_paths)
    _, readers, reader_basis = read_manifest_basis(
        root, Path("CURRENT-SURFACE-MANIFEST.json"))
    basis_resolved = reader_basis["status"] == "LOCAL_DECLARATION_VALID_NOT_NATIVE_ADMISSION"
    missing_readers = sorted(readers.difference(files))
    manifest_text = files.get(reader_basis.get("manifest"))
    manifest_matches_snapshot = (
        basis_resolved and manifest_text is not None
        and hashlib.sha256(manifest_text.encode("utf-8")).hexdigest() == reader_basis["sha256"]
    )
    negative_evidence_eligible = (
        basis_resolved and collection["complete_within_policy"]
        and not missing_readers and manifest_matches_snapshot
    )
    observations = scan_text_map(files, FAMILIES, current_reader_paths=readers)
    source_files = [
        {"path": path, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        for path, text in sorted(files.items())
    ]
    source_digest = hashlib.sha256(json.dumps(
        source_files, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
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
                "matched_line_numbers": list(item.matched_line_numbers),
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
            "caller_absence_on_scanned_text_surface": negative_evidence_eligible and live == 0 and unknown == 0,
            "rebuild_withdrawal_candidate_on_scanned_text_surface": negative_evidence_eligible and rebuild_relevant == 0,
            "wake_routing_withdrawal_candidate_on_scanned_text_surface": negative_evidence_eligible and wake_relevant == 0,
            "reclaim_ready": False,
        }

    return {
        "artifact_role": "BOUNDED_REFERENCE_AND_WITHDRAWAL_CENSUS_EVIDENCE",
        "runtime": False,
        "promotion": False,
        "destructive_action_authorized": False,
        "reader_basis": reader_basis,
        "source_snapshot": {
            "scope": "COLLECTED_UTF8_TEXT_ONLY_NOT_GIT_OR_RUNTIME_VERIFICATION",
            "collection": collection,
            "missing_declared_readers": missing_readers,
            "manifest_matches_snapshot": manifest_matches_snapshot,
            "negative_evidence_eligible": negative_evidence_eligible,
            "file_count": len(source_files),
            "manifest_of_hashes_sha256": source_digest,
            "files": source_files,
        },
        "families": list(FAMILIES),
        "summary": summary,
        "observations": rows,
        "claim_boundary": [
            "SEARCH_HIT_IS_NOT_CURRENT",
            "EXPLICIT_LOCAL_READER_BASIS_NOT_NATIVE_ADMISSION",
            "UNRESOLVED_READER_BASIS_CANNOT_PROVE_ABSENCE_OR_WITHDRAWAL",
            "CENSUS_IMPLEMENTATION_REFERENCES_ARE_AUDIT_NOT_LIVE_CALLERS",
            "SOURCE_SNAPSHOT_BINDS_SCANNED_TEXT_NOT_ATOMIC_GIT_STATE",
            "INCOMPLETE_TEXT_OR_READER_COVERAGE_CANNOT_PROVE_ABSENCE_OR_WITHDRAWAL",
            "SYMLINKS_NOT_FOLLOWED_NO_SANDBOX_OR_ADVERSARIAL_RACE_PROOF",
            "DEPENDENCY_SIGNAL_AGGREGATES_ALL_MATCHING_LINES_NOT_ONLY_DISPLAY_EXCERPT",
            "AUDIT_REFERENCE_IS_NOT_LIVE_CALLER",
            "UNKNOWN_REFERENCE_IS_HOLD",
            "KEYWORD_RELEVANCE_IS_REVIEW_SIGNAL_NOT_PROVEN_OPERATIONAL_DEPENDENCY",
            "CALLER_ABSENCE_ONLY_COVERS_SCANNED_TEXT_SURFACE",
            "REBUILD_OR_WAKE_KEYWORD_ABSENCE_DOES_NOT_PROVE_RUNTIME_DEPENDENCY_ABSENCE",
            "NON_TEXT_PLACEMENT_OR_RUNTIME_WAKE_REQUIRES_SEPARATE_PHYSICAL_REVIEW",
            "RECLAIM_READY_IS_NEVER_INFERRED_BY_THIS_CENSUS",
        ],
        "required_followup": [
            "resolve reported text collection and declared-reader coverage gaps",
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
    # The explicitly selected output is a result, not another input on rerun.
    output = args.output.absolute() if args.output is not None else None
    payload = build_payload(root, excluded_paths=(output,) if output is not None else ())
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
