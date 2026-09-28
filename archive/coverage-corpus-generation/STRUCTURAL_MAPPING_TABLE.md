# Historical snapshot — STRUCTURAL_MAPPING_TABLE.md

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Source commit: `b5575b199d8ac5bd636281dbf7c4eef9ee382adb`
> Source path: `STRUCTURAL_MAPPING_TABLE.md`
> Original Git blob: `6ee1be6e68c53dea3b34d209597208cb0b1e42c7`

This preserved body is evidence of an earlier design. Its commands, roles, schedules, status flags and next actions are historical, not instructions to execute. Use the directory [index](README.md) for successor context. The source body below is preserved verbatim.

<!-- BEGIN VERBATIM HISTORICAL BODY -->
# Structural Mapping Table

> Phase 1: Mapping Only. Full repository structural clean classification.

## 0. Status

- mapping_version: v0.1
- constraints_obeyed: true (no deletion, no rewrite, no merge)
- action_type: structural_cleanup

---

## 1. Top-Level Domain Mappings

### 1.1 DCP (Core Model / Layer 0)

*Conceptual foundation and interpretive framework.*

- `README.md`
- `STATUS.md`
- `00_mother-law/`
- `Freeze/`
- `A Constraint-Field Model for Stable Judgment*.pdf`

### 1.2 CoreTri (Core Triad / Axis)

*Structural bone and master axis layers.*

- `00_mother-law/existence-chain-master-layer.md`
- `GITHUB_CHAIN_MASTER_MAP.md`
- `REVIEW_CHAIN_MASTER_LAYER.md`
- `SPACE_CHAIN_MASTER_LAYER.md`
- `TIME_CHAIN_MASTER_LAYER.md`
- `WORLD_CHAIN_MASTER_AXIS.md` (to be created/mapped)
- `05_topology/consistent-triad-principle.md`
- `05_topology/triad-closed-loop-topology.md`

### 1.3 XLEN / XuanLing (Layer 1 / Operational / Runtime)

*Operational runtime, identity spine, and system execution environment.*

- `XUANLING_WORLD_READINESS_MILESTONES.md`
- `NETWORK_STRUCTURE_HIERARCHY_NOTE.md`
- `MODEL_FAMILY_ONCHAIN_SPEC.md`
- `MODEL_INVOCATION_CONTRACT.md`
- `CLUSTER_COVERAGE_NOTE.md`
- `THIRD_RUNTIME_ENVIRONMENT_NOTE.md`
- `DYNAMIC_CORPUS_DATABASE_NOTE.md`
- `Xuanling System_Layer 1_Operational _Interpretive Layer*.pdf`
- `LEGACY_SEED_*` (xuanling-seed-v0-1 extraction artifacts)
- `01_runtime-spine/`
- `02_runtime-ops/`
- `03_board-orchestration/`
- `04_adapter-layer/`

### 1.4 LingLuo (Layer 2 / Projection Layer Bridge)

*Mapping mentioned in mother architecture.*

- `00_mother-law/README.md` (Mapping reference)
- `Application & Expansion Reference Framework_Layer 2*.pdf`

---

## 2. Lower Domains Mapping

### 2.1 Window / Cadence Scheduling

- `WINDOW_12_MASTER_TABLE.md`
- `PLATFORM_SCHEDULER_AND_TOOL_NAMING_MAP.md`
- `SCHEDULING_EFFECT_REGISTER.md`
- `SCHEDULING_RECONCILIATION_REPORT.md`
- `SCHEDULING_EFFECTIVENESS_GAP_NOTE.md`
- `GATE_64_BINDING_NOTE.md`
- `01_runtime-spine/window_alignment_read_order.md`

### 2.2 Cloud / Family / Tool

- `ECOSYSTEM_FAMILY_ONBOARDING_ROADMAP.md`
- `EXTERNAL_NODE_ONCHAIN_SPEC.md`
- `EXTERNAL_API_VERSION_GOVERNANCE_NOTE.md`
- `JULES_TASKBOARD.md` (Bounded Execution Node Tool)
- `CHATGPT_GITHUB_BOOTSTRAP.md`
- `GITHUB_OPERATION_CAPABILITY_MATRIX.md`
- `04_adapter-layer/gamma_entry_spec.md`
- `04_adapter-layer/replit_relay_spec.md`

---

## 3. Register & Cleanup Domain (Mapping State)

- `REPOSITORY_CORPUS_INDEX.md`
- `ROLE_CLASSIFICATION_TABLE.md`
- `UNIFIED_ARTIFACT_REGISTER.md`
- `CLEANUP_QUEUE_REGISTER.md`
- `NAMING_DRIFT_RESOLUTION_REGISTER.md`
- `NAMING_DRIFT_FILE_LEVEL_DIFFS.md`
- `BRANCH_TOPOLOGY_AND_CLEANUP_REGISTER.md`
- `DISCONTINUITY_REGISTER.md`

---

## 4. Gap and Drift Analysis

### 4.1 Mismatch / Gap

- **World Chain Axis:** Defined in memory/PRs but file
  `WORLD_CHAIN_MASTER_AXIS.md` is currently missing/unlinked in the repo root.
- **DXS / XDDC / DXC / XDDL:** Mentioned in
  `00_mother-law/mother-architecture-registry-v0-1.md` as
  "not_found_in_current_repo_search" but needing location.
- **LingLuo:** Mentioned but lacks explicit dedicated mapping file besides
  the PDF/README.
- **Issue alignment:** PRs and Issues exist for new features
  (e.g., Qinyi task packet issue template) but aren't fully reflected in
  the unified registers yet.

### 4.2 Duplicated Logic

- **Registers:** The overlapping indexing logic across `REPOSITORY_CORPUS_INDEX.md`,
  `UNIFIED_ARTIFACT_REGISTER.md`, and `ROLE_CLASSIFICATION_TABLE.md` has been
  identified. `REPOSITORY_CORPUS_INVENTORY_MAP.md` now serves as a non-binding
  inventory reference for consolidation planning, while the source registers retain
  their distinct roles.
- **Scheduling/Topology:** Scheduling logic is split across
  `WINDOW_12_MASTER_TABLE.md`, `SCHEDULING_EFFECT_REGISTER.md`,
  and `PLATFORM_SCHEDULER_AND_TOOL_NAMING_MAP.md`.

### 4.3 Drifted Naming

- Legacy `01_runtime_spine/` vs canonical `01_runtime-spine/`
- Legacy `03_board_orchestration/` vs canonical `03_board-orchestration/`

---

## 5. Next Recommended Action

### Isolate Candidates

- Legacy seed documents (`LEGACY_SEED_*`) should be isolated into a dedicated
  archive.
- `xuanling-seed-v0-1` branch remaining references should be cleaned.

### Next Recommended Action

**Update Core Registers:** Incorporate this structural mapping into
`REPOSITORY_CORPUS_INDEX.md` and `UNIFIED_ARTIFACT_REGISTER.md` to
formalize the domain bindings, while observing the constraint to
not delete or merge files yet.

---

return_to_00: true
