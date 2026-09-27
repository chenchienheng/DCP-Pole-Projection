# [CoreTri] Task Orchestration Bridge Spec

> Define a bridge layer that coordinates task creation, execution feedback,
> review status, and human approval between ChatGPT, Jules, and GitHub.

---

## 1. Core Definition
- **User** = final approval / premise holder
- **ChatGPT** = field coordinator / structural reviewer
- **Jules** = execution node
- **GitHub** = traceable memory and merge surface

## 2. Task Lifecycle
1. **propose**: Initial formulation by ChatGPT.
2. **issue_created**: Task logged into GitHub for tracking.
3. **jules_started**: Jules node begins execution against the repo.
4. **pr_opened**: Changes pushed to a traceable branch/PR.
5. **review_ready**: ChatGPT evaluates structural alignment.
6. **human_approved**: User confirms premise holds.
7. **merged**: Changes absorbed into main branch.
8. **return_to_00**: Execution concludes, trace closed or documented.

## 3. State Contract
Each task must explicitly declare:
- **task_id**: Unique identifier for tracking.
- **source_issue**: Linked GitHub issue number.
- **target_files**: Expected file footprint.
- **expected_output**: Intended structural/content outcome.
- **constraints**: Defined limitations and non-goals.
- **review_required**: Boolean gating merge.
- **merge_condition**: Exact state needed to absorb.
- **return_path**: Defined route back to completion status.
- **failure_route**: Fallback handler.

## 4. Bridge Rule
No task should be treated as complete unless:
- PR exists.
- Changed files match the expected scope.
- Review status is confirmed.
- Merge state is verified.

## 5. Failure Handling
- **no PR visible** -> `return_failed` -> `AXIS-05`
- **PR diff mismatch** -> `return_failed` -> `AXIS-05`
- **draft stuck** -> `review_required`
- **duplicate task** -> manual review

## 6. Human Role Reduction
This bridge specifies how the user transitions from:
- **Task Messenger**: Manually copying instructions between layers.
to:
- **Final Approval / Exception Handler**: Approving pre-coordinated structures.

## 7. mismatch_or_gap
None currently identified. This document specifies structural routing without
expanding the runtime or establishing new master axes.

## 8. unresolved_risks
Potential execution drift if the Jules node operates without first confirming
the expected task constraints with the ChatGPT review node.

## 9. next_single_recommended_action
Do not append this definition to historical indexes or registers. If the
material is affected, route through `CURRENT-SURFACE-MANIFEST.json` and the
explicitly re-admitted affected surface.
