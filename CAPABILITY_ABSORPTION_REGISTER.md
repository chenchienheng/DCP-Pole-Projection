# Capability Absorption Register — common comparison basis

Recorded: 2026-09-27 (Asia/Taipei)
State: CURRENT_WORKING_REGISTER_CANDIDATE
Runtime: false
Canon: false
Authority: user-requested bounded PR/context reconciliation; not merge or deletion approval

## What this register now covers

The previous register's blanket zero-execution queue was stale. This revision binds every open PR to the same observation window and its repository's pinned main, while retaining historical source bases, different purposes, derived changes, and unresolved non-executable content. It is a review projection, not central truth, Native Current, a permanent topology or a universal integration order.

Live GET-only snapshot: 2026-09-27T05:47:46.220571Z–05:48:05.132097Z. Sixty-three requests exhausted all PR pages and all open-PR changed-file pages. Recursive trees were not truncated. Revalidation found unchanged main and open-PR head/base bindings within each repository's acquisition window. This does not establish a globally atomic snapshot.

| Repository | Pinned main | All PR metadata records | Open PRs |
|---|---|---:|---:|
| DCP-Pole-Projection | f61bf2f2383f0520a8dc5f2f015cd0f9e98aa9ac | 204 | 10 |
| GLModel-Pole-Projection | bc0ea081c16f44ae837e4a216b932c4f44eb9c0d | 23 | 1 |
| Ideas-Pole-Projection | 1638d4e1545d3e0bc2783cb3fd5298863a164f1b | 17 | 0 |

Total: 244 PR records; 11 open PRs. Historical titles/bodies/status/ref metadata were acquired; this is NOT a semantic review of every closed historical diff. All changed paths and available patches of the open set were acquired. Matching bytes is not semantic acceptance; missing paths are not proof of lost purpose.

Evidence: [run36298224235](https://github.com/chenchienheng/DCP-Pole-Projection/actions/runs/36298224235), [artifact10924732409](https://github.com/chenchienheng/DCP-Pole-Projection/actions/runs/36298224235/artifacts/10924732409). ZIP716052bytes, independently verified SHA256 `530ec27e44aac49aaf106f53379ba814a9087471eb9184ef36011ae0f30261b8`. `baseline.json` preserves the complete pre-edit PR bodies, pinned source/main relations, patches, policy contents and request hashes. Artifact retention is finite; retain the exported archive for long-term recovery.

## Every open PR, classified by purpose rather than PR number

DCP selected comparison candidate: existing #406 at audited head `282bf789f7be55d3f4b8ecaa07895ccb1b33d8fd`. Later register/cleanup revisions must not retroactively alter this snapshot.

| PR | Purpose/current role | Observed relation to comparison candidate | Remaining work |
|---|---|---|---|
| DCP #324 | Broad source with executable and non-executable subsets | 307 paths; executable127 present (118exact/9derived); other180 split below | Non-executable purpose/loss review; kernel integration acceptance; no broad merge |
| DCP #384 | Capability activation source | 4/4 exact blob+mode | #406 integration acceptance, then source lifecycle decision |
| DCP #387 | Current/Affected Cone/Return regression source | 1/1 exact | Same existing #406; not another active build |
| DCP #391 | Independent NFN/World orchestration semantics | 36 paths not in main or #406 | Its own review/acceptance and a real caller interface when required |
| DCP #393 | Return/re-entry schema repair source | 2/2 exact | Same existing #406; old source failure not a current regression |
| DCP #395 | Carrier choice / next-condition versus next-Need source | 4/4 exact | Same existing #406; no invented selection policy |
| DCP #396 | Mixed-reality intake source | 2exact; __init__ intentionally derived | Preserve integrated exports; do not overwrite with older whole file |
| DCP #397 | Replaceable vision-provider bridge source | 3exact, including1 shared reality-intake file | Two unique files plus shared provenance; do not duplicate the shared implementation |
| DCP #406 | Existing kernel integration candidate | 141 changed paths in snapshot; self-comparison exact | Review/explicit acceptance; real caller/receiver effects, not another execution-discovery cycle |
| DCP #419 | Current-surface and kernel-present/absent qualification source | 2exact; workflow differs only after the temporary inventory extension | Preserve both routing cases; cleanup restores source workflow; acceptance/lifecycle separate |
| GLModel #25 | Viewer claim/load-error repair candidate | Own main:2different+1new | Its own acceptance/browser/use scope; never substitute DCP tests |

## #324: the missing scope split

Source #324 head: `00999341ff600a65ab3de641e4ce5615d6e9690d`. Historical base `ba744cb3c385782ee4873f1764850f27d19f3f8d` is not present main.

Selected executable subset: all127 paths exist in #406; 118 exact and9 derived. Nine differences: dcp_kernel/__init__.py, carrier_binding.py, consequence.py, fixtures.py, platform.py; tests/test_carrier_binding.py, test_consequence.py, test_current_surface_alignment.py, test_gui_lu_fixture.py. Earlier122/122 non-overlay coverage belonged to an earlier source/target scope; it is not the current whole-source count.

Non-executable/broad subset: 180 paths = 3exact +87different +37absent by path +53proposed deletions not applied. The37 include the candidate lifecycle kernel document, legacy-design disposition, and historical primitive/lineage specimens. The53 retained source paths are not authorized for deletion. Different or absent bytes do not establish a material gap until purpose, newer successors, losses and applicability are reviewed.

Priority within this subset: assess lifecycle/design-disposition content against current-main Need-relative/carrier-neutral boundaries before any import. Historical fixed lifecycle/role/pole/order formulations must not silently become current instructions. Lineage specimens labelled non-current need not all be installed as live documents. Preserve their original proposals and denied/deferred deletion evidence; do not declare the180 absorbed merely because tests pass.

## Execution evidence, kept separate from acceptance

- #391 head afca39fc9311762ea67d6ab8eefe80a949a5f0d3: push36293354922 and PR36293357302; original121 R2 tests plus17 preserved World cases on exact head and named provider merge candidate. These are138 cases twice, not276 independent definitions.
- #406 head9a0f7a9f3e487ef9907b32aacd22c804ef72308e: run36296906394;8surface+255kernel tests in exact-head and provider-merge scopes, with compile/JSON/census/artifact evidence. Source blobs and artifact hashes are recorded in comment5852975822.
- #406 audit head282bf789f7be55d3f4b8ecaa07895ccb1b33d8fd: run36298224235 completed both jobs successfully; full inventory succeeded. This report does not newly attest unread full logs; the provider job/step outcomes and acquired artifact were directly verified.
- #419 source0a350bf0dab909e63ca8cb002369df0ea1e9c707: run36296718666 explicitly follows CANDIDATE_ABSENT:NOT_APPLICABLE_NOT_PASS on its no-kernel branch. Kernel steps skipped, not kernel PASS. Its source behavior has separately been used in the complete #406 candidate.
- GLModel #25 head1c87f644e268ea427d597c2d23653cc19406333b: its recorded Semantic Core Verify run36288540979 is independent viewer/semantic CI evidence, not browser/runtime or DCP acceptance.

No whole #324 execution, all-repository semantic equivalence, actual main merge, receiver acceptance, Runtime, Canon or destructive-action approval is inferred.

## Already absorbed/closed lineage, not today's task queue

- #392 entry templates → #404; #386 falsification evidence → #405. #407 was a zero-change duplicate merge, not new absorption.
- #383 reader/semantic deltas → #411; source closed-unmerged with historical evidence retained.
- GLModel #8 non-removal deltas → #22/#23/#24; Ideas #7 non-removal deltas → #17/#18. Broad deletion was not promoted.
- #408/#409/#413 remain closed duplicate/inferior kernel successors. Do not recreate them because an old description is encountered.
- Public entry progression #401/#402/#403, GLModel#19/#20/#21, Ideas#14/#15/#16 remains separate from executable adoption.
- #410 CI entry, #412 register and #415–#418 execution/static/coverage records are time-bound evidence. Their old zero-run or selected-source counts do not override later exact evidence.

## Temporary audit cleanup and recovery

The added network inventory is not a standing scheduler or a required kernel dependency. This revision restores `.github/workflows/dcp-kernel-candidate.yml` to exact #419 source blob `30d2345eb5470231438faa0ec12000cb86284955`, removing the temporary baseline acquisition/upload steps. The reusable GET-only `tools/snapshot_pr_baseline.py` remains on demand; it is not auto-invoked by the restored workflow. Existing8surface/255kernel verification, matrix, permissions and census remain.

The failed first audit run36298026708 is preserved: its URL allowlist rejected GitHub's numeric-repository pagination form, while existing kernel steps succeeded. The bounded fix allowed only the three already-verified repository IDs; no credentials, private repositories or write endpoints were added.

Recover the exact previous register from [this fixed source](https://github.com/chenchienheng/DCP-Pole-Projection/blob/282bf789f7be55d3f4b8ecaa07895ccb1b33d8fd/CAPABILITY_ABSORPTION_REGISTER.md), blob `d94c054086f8f186a958ddd8e254ef413433b7cb`. It contains the full previous static/zero-run/coverage history. Do not copy its historical Next back into current work. Recover pre-edit PR bodies from the archived baseline before reconciling any later edits; never blindly overwrite a newer body.

This batch changes the existing candidate/register and affected ordinary PR metadata only. Main, source branch bases, PR lifecycle states, account rights, schedules and UI modes are not changed. A local acceptance HOLD does not stop unrelated authorized work.
