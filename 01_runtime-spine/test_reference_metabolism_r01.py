import unittest

from reference_metabolism_r01 import (
    ArtifactMetabolismInput,
    MetabolismDisposition,
    ReferenceEvidence,
    ReferenceRole,
    assess_artifact_transition,
)


class ReferenceMetabolismR01Tests(unittest.TestCase):
    def test_legacy_to_legacy_reference_does_not_keep_current_facing(self):
        result = assess_artifact_transition(ArtifactMetabolismInput(
            artifact_path="02_runtime-ops/task_follow_up.md",
            successor_pointer="DCP_RETURN_AND_ACTIVE_STATE",
            successor_machine_or_executable=True,
            unique_lineage_evidence=True,
            normal_reader_wake=False,
            references=(
                ReferenceEvidence(
                    "04_adapter-layer/source_map.md",
                    "02_runtime-ops/task_follow_up.md",
                    ReferenceRole.LINEAGE,
                ),
                ReferenceEvidence(
                    "01_native-board/board_index.md",
                    "02_runtime-ops/task_follow_up.md",
                    ReferenceRole.LINEAGE,
                ),
            ),
        ))
        self.assertEqual(result.disposition, MetabolismDisposition.RETAIN_EVIDENCE_ONLY)
        self.assertFalse(result.destructive_action_authorized)

    def test_live_caller_without_successor_stays_current_facing(self):
        result = assess_artifact_transition(ArtifactMetabolismInput(
            artifact_path="legacy.md",
            successor_pointer=None,
            successor_machine_or_executable=False,
            unique_lineage_evidence=False,
            normal_reader_wake=True,
            references=(ReferenceEvidence("CURRENT-SURFACE-MANIFEST.json", "legacy.md", ReferenceRole.LIVE),),
        ))
        self.assertEqual(result.disposition, MetabolismDisposition.KEEP_CURRENT_FACING)

    def test_successor_with_old_wake_requires_wake_withdrawal(self):
        result = assess_artifact_transition(ArtifactMetabolismInput(
            artifact_path="legacy.md",
            successor_pointer="machine-successor",
            successor_machine_or_executable=True,
            unique_lineage_evidence=False,
            normal_reader_wake=True,
            references=(),
        ))
        self.assertEqual(result.disposition, MetabolismDisposition.WITHDRAW_NORMAL_WAKE)

    def test_unknown_reference_holds_transition_not_whole_system(self):
        result = assess_artifact_transition(ArtifactMetabolismInput(
            artifact_path="legacy.md",
            successor_pointer="machine-successor",
            successor_machine_or_executable=True,
            unique_lineage_evidence=False,
            normal_reader_wake=False,
            references=(ReferenceEvidence("misc/map.md", "legacy.md", ReferenceRole.UNKNOWN),),
        ))
        self.assertEqual(result.disposition, MetabolismDisposition.HOLD_UNKNOWN)


if __name__ == "__main__":
    unittest.main()
