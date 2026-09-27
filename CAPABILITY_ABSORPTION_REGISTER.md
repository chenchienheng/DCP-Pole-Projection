# Capability Absorption Batch — 2026-09-27

State: WORKING_ABSORPTION_REGISTER
Runtime: false
Canon: false
Merge authority: user-authorized bounded repository metabolism

## Absorbed in this batch

### PR #392 — capability-based Issue / PR entry
Target files:
- .github/ISSUE_TEMPLATE/capability_task_packet.md
- .github/ISSUE_TEMPLATE/qinyi_task_packet.md
- .github/pull_request_template.md

Absorption condition: exact file content from PR #392 head is carried by this batch branch. After main merge + exact-main readback, PR #392 may be retired as a carrier; its lineage remains in Git history.

### PR #386 — CoreTri R2 DCP falsification return
Target:
- experiments/coretri-r2-dcp-native-result.md

Absorption condition: exact evidence artifact from PR #386 head is carried by this batch branch. It remains EXPERIMENT_RETURN / Runtime=false / Canon=false. After main merge + exact-main readback, PR #386 may be retired as a carrier without promoting the experiment.

## Kernel absorption queue

The following are not merged by age or PR number. They depend on a coherent `dcp_kernel` substrate that current main does not yet carry.

1. FOUNDATION_RECONCILE — PR #324
   - broad existence-first lifecycle/kernel lineage;
   - source of many shared models/contracts/tests;
   - too broad and diverged for blind merge;
   - use as source lineage for a selective current-main kernel package, not as automatic topology migration.

2. CAPABILITY_ACTIVATION — PR #384
   - unique capability_activation.py / capability_activation_decoupled.py + tests;
   - depends on dcp_kernel.models and Decision semantics.

3. CURRENT_RETURN_REGRESSION — PR #387
   - unique test_native_backlog_retest.py;
   - depends on models/resolution/return_state.

4. RETURN_REENTRY_SCHEMA — PR #393
   - platform.py + dedicated schema-drift regression;
   - depends on action_gate, activation, decision_chain, models, resolution, return_state, transition, write_intent.

5. CARRIER_CONSEQUENCE — PR #395
   - carrier_binding/consequence semantic deltas + tests;
   - reconcile against #324 base before absorption.

6. REALITY_INTAKE — PR #396
   - unique reality_intake implementation + tests.

7. VISION_PROVIDER — PR #397
   - overlaps #396 reality_intake and adds unique vision_provider + tests;
   - absorb reality_intake once, then qualify only the unique vision-provider delta.

## Broad-transition holds

### PR #383
Reader/Current cleanup is partly superseded by current main reader/status/manifest work. Mixed routing, adapter, register and legacy-surface deltas remain. Keep HOLD until unique delta is split from already-absorbed entry changes.

### GLModel PR #8
Ordinary reader/status correction is superseded by current main, but the PR also contains semantic-core verifier/rebuild changes and a broad historical corpus contraction. Keep HOLD; do not infer safe retirement from README/STATUS supersession.

### Ideas PR #7
Ordinary reader/status correction is superseded by current main, but broad world/placement/corpus deltas remain. Keep HOLD; do not infer safe retirement from README/STATUS supersession.

## Rules

- absorbed file != absorbed meaning unless exact-main readback confirms the intended successor;
- PR retirement != evidence deletion;
- experiment absorption != Canon/Runtime promotion;
- no kernel PR is merged until its dependency package and execution evidence are coherent;
- overlap is reconciled once, not duplicated across successors.
