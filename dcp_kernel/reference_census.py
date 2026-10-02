from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Iterable

from .metabolism import _reader_path_set


class ReferenceClass(str, Enum):
    LIVE_CALLER = "LIVE_CALLER"
    AUDIT_REFERENCE = "AUDIT_REFERENCE"
    LINEAGE_POINTER = "LINEAGE_POINTER"
    SELF_REFERENCE = "SELF_REFERENCE"
    UNKNOWN_HOLD = "UNKNOWN_HOLD"


class DependencySignal(str, Enum):
    NONE = "NONE"
    REBUILD_RELEVANT = "REBUILD_RELEVANT"
    WAKE_ROUTING_RELEVANT = "WAKE_ROUTING_RELEVANT"
    REBUILD_AND_WAKE_RELEVANT = "REBUILD_AND_WAKE_RELEVANT"
    UNKNOWN = "UNKNOWN"


EXECUTABLE_PREFIXES = (
    "dcp_kernel/",
    "contracts/",
    ".github/",
)

AUDIT_EXACT_PATHS = {
    "dcp_kernel/reference_census.py",
    "contracts/implementation-manifest.json",
    "tools/census_legacy_references.py",
    "tests/test_reference_census.py",
    "tests/test_family_metabolism.py",
    "tests/test_successor_coverage.py",
    "tests/test_retirement.py",
    "tests/test_metabolism.py",
}

AUDIT_PREFIXES = (
    "fixtures/repository/",
)

LINEAGE_BASENAMES = {
    "REPOSITORY_CORPUS_INDEX.md",
    "NAMING_DRIFT_FILE_LEVEL_DIFFS.md",
    "NAMING_DRIFT_NORMALIZATION_PROPOSAL.md",
    "UNIFIED_ARTIFACT_REGISTER.md",
}

LEGACY_PREFIXES = (
    "00_meta/",
    "00_mother-law/",
    "01_native-board/",
    "01_runtime-spine/",
    "02_runtime-ops/",
    "02_translation-layer/",
    "03_board-orchestration/",
    "03_field-governance/",
    "04_adapter-layer/",
    "04_interface-layer/",
    "05_XLEN_Reserve_Unenabled/",
    "05_topology/",
    "archive/",
)

REBUILD_TOKENS = (
    "rebuild", "re-entry", "reentry", "reconcile", "reconciliation",
    "successor", "restore", "loader", "current_revision", "last_good",
)

WAKE_ROUTING_TOKENS = (
    "wake", "routing", "route", "reader", "dispatch", "launcher",
    "entry", "activation", "priority", "current-surface",
)


@dataclass(frozen=True)
class ReferenceObservation:
    caller_path: str
    target_family: str
    classification: ReferenceClass
    excerpt: str
    dependency_signal: DependencySignal = DependencySignal.NONE
    matched_line_numbers: tuple[int, ...] = ()


def classify_reference(
    caller_path: str,
    target_family: str,
    *,
    current_reader_paths: Iterable[str] = (),
) -> ReferenceClass:
    """Classify a text reference using an explicit local reader basis.

    LIVE_CALLER is a bounded source-review category, not execution evidence.
    Historical filenames and path normalization never establish reader status.
    """
    readers = _reader_path_set(current_reader_paths)
    try:
        normalized = next(iter(_reader_path_set((caller_path,))))
    except (TypeError, ValueError):
        return ReferenceClass.UNKNOWN_HOLD
    target = target_family.rstrip("/") + "/"

    if normalized.startswith(target):
        return ReferenceClass.SELF_REFERENCE
    if normalized in AUDIT_EXACT_PATHS or normalized.startswith(AUDIT_PREFIXES):
        return ReferenceClass.AUDIT_REFERENCE
    if normalized in readers or normalized.startswith(EXECUTABLE_PREFIXES):
        return ReferenceClass.LIVE_CALLER
    if PurePosixPath(normalized).name in LINEAGE_BASENAMES:
        return ReferenceClass.LINEAGE_POINTER
    if normalized.startswith(LEGACY_PREFIXES):
        return ReferenceClass.LINEAGE_POINTER
    return ReferenceClass.UNKNOWN_HOLD


def classify_dependency_signal(
    *,
    caller_path: str,
    classification: ReferenceClass,
    excerpt: str,
) -> DependencySignal:
    """Mark whether a reference may participate in rebuild or wake/routing behavior.

    Audit/self/lineage references are non-operational by definition for this
    census. Keyword presence on a live/unknown surface is only a review signal,
    not proof of an operational dependency.
    """

    if classification in {
        ReferenceClass.AUDIT_REFERENCE,
        ReferenceClass.SELF_REFERENCE,
        ReferenceClass.LINEAGE_POINTER,
    }:
        return DependencySignal.NONE
    if classification is ReferenceClass.UNKNOWN_HOLD:
        return DependencySignal.UNKNOWN

    haystack = f"{caller_path} {excerpt}".lower()
    rebuild = any(token in haystack for token in REBUILD_TOKENS)
    wake = any(token in haystack for token in WAKE_ROUTING_TOKENS)

    if rebuild and wake:
        return DependencySignal.REBUILD_AND_WAKE_RELEVANT
    if rebuild:
        return DependencySignal.REBUILD_RELEVANT
    if wake:
        return DependencySignal.WAKE_ROUTING_RELEVANT
    return DependencySignal.NONE


def scan_text_map(
    files: dict[str, str],
    families: tuple[str, ...],
    *,
    current_reader_paths: Iterable[str] = (),
) -> tuple[ReferenceObservation, ...]:
    readers = _reader_path_set(current_reader_paths)
    observations: list[ReferenceObservation] = []
    for caller_path, text in files.items():
        for family in families:
            needle = family.rstrip("/") + "/"
            if needle not in text:
                continue
            matches = tuple(
                (number, line.strip())
                for number, line in enumerate(text.splitlines(), start=1)
                if needle in line
            )
            # Keep one bounded display excerpt and one row per caller/family,
            # but inspect every matching line before declaring signal absence.
            excerpt = matches[0][1]
            matched_text = "\n".join(line for _number, line in matches)
            classification = classify_reference(
                caller_path, family, current_reader_paths=readers)
            observations.append(
                ReferenceObservation(
                    caller_path=caller_path,
                    target_family=family,
                    classification=classification,
                    excerpt=excerpt[:240],
                    dependency_signal=classify_dependency_signal(
                        caller_path=caller_path,
                        classification=classification,
                        excerpt=matched_text,
                    ),
                    matched_line_numbers=tuple(number for number, _line in matches),
                )
            )
    return tuple(observations)


def has_proven_live_caller(observations: tuple[ReferenceObservation, ...], family: str) -> bool:
    return any(
        item.target_family == family and item.classification is ReferenceClass.LIVE_CALLER
        for item in observations
    )


def has_unknown_hold(observations: tuple[ReferenceObservation, ...], family: str) -> bool:
    return any(
        item.target_family == family and item.classification is ReferenceClass.UNKNOWN_HOLD
        for item in observations
    )


def has_rebuild_relevant_reference(observations: tuple[ReferenceObservation, ...], family: str) -> bool:
    return any(
        item.target_family == family
        and item.dependency_signal in {
            DependencySignal.REBUILD_RELEVANT,
            DependencySignal.REBUILD_AND_WAKE_RELEVANT,
            DependencySignal.UNKNOWN,
        }
        for item in observations
    )


def has_wake_routing_relevant_reference(observations: tuple[ReferenceObservation, ...], family: str) -> bool:
    return any(
        item.target_family == family
        and item.dependency_signal in {
            DependencySignal.WAKE_ROUTING_RELEVANT,
            DependencySignal.REBUILD_AND_WAKE_RELEVANT,
            DependencySignal.UNKNOWN,
        }
        for item in observations
    )
