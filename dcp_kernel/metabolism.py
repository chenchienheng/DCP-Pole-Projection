from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Iterable


class ArtifactRole(str, Enum):
    CURRENT_PROJECTION = "CURRENT_PROJECTION"
    EXECUTABLE_CANDIDATE = "EXECUTABLE_CANDIDATE"
    MACHINE_CONTRACT = "MACHINE_CONTRACT"
    TEST_EVIDENCE = "TEST_EVIDENCE"
    FIXTURE_EVIDENCE = "FIXTURE_EVIDENCE"
    HISTORICAL_LINEAGE = "HISTORICAL_LINEAGE"
    DESCRIPTIVE = "DESCRIPTIVE"
    BINARY_EVIDENCE = "BINARY_EVIDENCE"
    UNKNOWN = "UNKNOWN"


class NameRisk(str, Enum):
    AUTHORITY_IMPLICATION = "AUTHORITY_IMPLICATION_RISK"
    MATURITY_IMPLICATION = "MATURITY_IMPLICATION_RISK"
    REGISTRY_TRUTH = "REGISTRY_TRUTH_RISK"
    ACTOR_COUPLING = "ACTOR_COUPLING_RISK"
    NONE = "NAME_NEUTRAL"


class ProposedDisposition(str, Enum):
    KEEP_CURRENT_PROJECTION = "KEEP_CURRENT_PROJECTION"
    KEEP_EXECUTABLE_CANDIDATE = "KEEP_EXECUTABLE_CANDIDATE"
    KEEP_MACHINE_CONTRACT = "KEEP_MACHINE_CONTRACT"
    KEEP_TEST_OR_FIXTURE_EVIDENCE = "KEEP_TEST_OR_FIXTURE_EVIDENCE"
    EVIDENCE_ONLY = "EVIDENCE_ONLY"
    SUCCESSOR_COVERAGE_REVIEW = "SUCCESSOR_COVERAGE_REVIEW"
    BOUNDED_CLASSIFICATION_REQUIRED = "BOUNDED_CLASSIFICATION_REQUIRED"
    HOLD_UNKNOWN = "HOLD_UNKNOWN"


_CURRENT_PATHS = {
    "README.md",
    "CURRENT-SURFACE-MANIFEST.json",
    "PUBLIC-SURFACE-POLICY.md",
    "STATUS.md",
    "LIFECYCLE_DEPENDENCY_CHAIN_KERNEL.md",
}
_AUTHORITY_TERMS = {
    "master",
    "mother",
    "commander",
    "sovereignty",
    "axis",
}
_MATURITY_TERMS = {
    "runtime",
    "engine",
    "launcher",
    "control-center",
    "control_center",
}
_REGISTRY_TERMS = {
    "registry",
    "register",
    "taskboard",
    "scheduler",
    "scheduling",
}
_ACTOR_TERMS = {
    "qinyi",
    "jules",
    "agent",
    "mothertree",
    "mother-tree",
}


@dataclass(frozen=True)
class ArtifactAssessment:
    path: str
    role: ArtifactRole
    name_risks: tuple[NameRisk, ...]
    claim_ceiling: str
    normal_reader_eligible: bool
    proposed_disposition: ProposedDisposition
    reasons: tuple[str, ...]
    destructive_action_authorized: bool = False

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["role"] = self.role.value
        data["name_risks"] = [risk.value for risk in self.name_risks]
        data["proposed_disposition"] = self.proposed_disposition.value
        return data


def _tokens(path: str) -> set[str]:
    normalized = path.lower().replace("/", "-").replace(".", "-")
    return {
        piece
        for piece in normalized.replace("_", "-").split("-")
        if piece
    }


def classify_name_risks(
    path: str,
    role: ArtifactRole,
) -> tuple[NameRisk, ...]:
    lower = path.lower()
    tokens = _tokens(path)
    risks: list[NameRisk] = []

    if any(term in tokens or term in lower for term in _AUTHORITY_TERMS):
        risks.append(NameRisk.AUTHORITY_IMPLICATION)
    if any(term in lower for term in _REGISTRY_TERMS):
        risks.append(NameRisk.REGISTRY_TRUTH)
    if any(term in lower for term in _ACTOR_TERMS):
        risks.append(NameRisk.ACTOR_COUPLING)
    if (
        any(term in lower for term in _MATURITY_TERMS)
        and role
        not in {
            ArtifactRole.EXECUTABLE_CANDIDATE,
            ArtifactRole.TEST_EVIDENCE,
        }
    ):
        risks.append(NameRisk.MATURITY_IMPLICATION)

    return tuple(dict.fromkeys(risks)) or (NameRisk.NONE,)


def classify_role(path: str) -> ArtifactRole:
    p = PurePosixPath(path)
    suffix = p.suffix.lower()

    if path in _CURRENT_PATHS:
        return ArtifactRole.CURRENT_PROJECTION
    if path.startswith("dcp_kernel/") and suffix == ".py":
        return ArtifactRole.EXECUTABLE_CANDIDATE
    if path.startswith("tools/") and suffix == ".py":
        return ArtifactRole.EXECUTABLE_CANDIDATE
    if path.startswith("contracts/") and suffix == ".json":
        return ArtifactRole.MACHINE_CONTRACT
    if path.startswith("tests/") and suffix == ".py":
        return ArtifactRole.TEST_EVIDENCE
    if path.startswith("fixtures/") and suffix == ".json":
        return ArtifactRole.FIXTURE_EVIDENCE
    if path.startswith("archive/") or path.startswith("snapshots/"):
        return ArtifactRole.HISTORICAL_LINEAGE
    if suffix in {".md", ".txt", ".rst"}:
        return ArtifactRole.DESCRIPTIVE
    if suffix in {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".glb",
        ".gltf",
    }:
        return ArtifactRole.BINARY_EVIDENCE
    return ArtifactRole.UNKNOWN


def assess_artifact(path: str) -> ArtifactAssessment:
    role = classify_role(path)
    risks = classify_name_risks(path, role)
    risky = risks != (NameRisk.NONE,)

    if role is ArtifactRole.CURRENT_PROJECTION:
        disposition = ProposedDisposition.KEEP_CURRENT_PROJECTION
        ceiling = "DESCRIPTIVE_OR_MACHINE_CURRENT_PROJECTION"
        reader = True
        reasons = ("BOUNDED_CURRENT_READER_ENTRY",)
    elif role is ArtifactRole.EXECUTABLE_CANDIDATE:
        disposition = ProposedDisposition.KEEP_EXECUTABLE_CANDIDATE
        ceiling = "EXECUTABLE_CANDIDATE"
        reader = False
        reasons = ("CODE_PRESENCE_DOES_NOT_SELF_PROMOTE",)
    elif role is ArtifactRole.MACHINE_CONTRACT:
        disposition = ProposedDisposition.KEEP_MACHINE_CONTRACT
        ceiling = "MACHINE_CONTRACT"
        reader = False
        reasons = ("SCHEMA_OR_MANIFEST_IS_NOT_RUNTIME",)
    elif role in {
        ArtifactRole.TEST_EVIDENCE,
        ArtifactRole.FIXTURE_EVIDENCE,
    }:
        disposition = ProposedDisposition.KEEP_TEST_OR_FIXTURE_EVIDENCE
        ceiling = "BOUNDED_EXECUTABLE_EVIDENCE"
        reader = False
        reasons = ("LOCAL_OR_FIXTURE_PASS_IS_NOT_RUNTIME",)
    elif role is ArtifactRole.HISTORICAL_LINEAGE:
        disposition = ProposedDisposition.EVIDENCE_ONLY
        ceiling = "HISTORICAL_EVIDENCE"
        reader = False
        reasons = ("NO_NORMAL_WAKE_WITHOUT_REENTRY_PURPOSE",)
    elif risky:
        disposition = ProposedDisposition.SUCCESSOR_COVERAGE_REVIEW
        ceiling = "DESCRIPTIVE"
        reader = False
        reasons = (
            "NAME_MAY_IMPLY_AUTHORITY_OR_MATURITY_BEYOND_EVIDENCE",
            "RENAME_MOVE_ARCHIVE_IS_NOT_METABOLISM",
        )
    elif role in {
        ArtifactRole.DESCRIPTIVE,
        ArtifactRole.BINARY_EVIDENCE,
    }:
        disposition = ProposedDisposition.BOUNDED_CLASSIFICATION_REQUIRED
        ceiling = "DESCRIPTIVE_OR_EVIDENCE"
        reader = False
        reasons = ("SUCCESSOR_AND_UNIQUE_EVIDENCE_CHECK_REQUIRED",)
    else:
        disposition = ProposedDisposition.HOLD_UNKNOWN
        ceiling = "UNKNOWN"
        reader = False
        reasons = ("ARTIFACT_ROLE_UNRESOLVED",)

    return ArtifactAssessment(
        path=path,
        role=role,
        name_risks=risks,
        claim_ceiling=ceiling,
        normal_reader_eligible=reader,
        proposed_disposition=disposition,
        reasons=reasons,
    )


def assess_paths(
    paths: Iterable[str],
) -> tuple[ArtifactAssessment, ...]:
    return tuple(
        assess_artifact(path)
        for path in sorted(set(paths))
    )
