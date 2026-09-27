# [CoreTri] Redundant Load Reduction Spec

> Purpose: Define how CoreTri reduces repeated context loading, duplicated
> review work, and repeated task interpretation across ChatGPT, Jules, GitHub,
> and external execution nodes.

---

## 1. Core Definition

Redundant load occurs when multiple execution layers or nodes re-evaluate the
same premise, reload identical contextual data without structural bounds, or
re-review tasks that have already passed previous structural verification.
This specification aims to establish methods to reduce this load without
modifying doctrine, expanding runtime, or establishing new axes.

## 2. Redundant Load Sources

- **Context Re-loading**: Providing the entire repository context instead of
  narrowing down to specific execution boundaries.
- **Interpretation Drift**: Re-evaluating the definition of rules or boundaries
  across different nodes.
- **Duplicate Review**: Requesting human oversight for processes previously
  verified by intermediate nodes.
- **Execution Overlaps**: Parallel execution traces generating unmerged
  artifacts that require repeated review.

## 3. Delta-only Transmission Rule

To prevent unbounded context loading, nodes must transmit and consume only the
structural delta. This means:
- Do not provide full context histories if an explicit anchor point exists.
- Re-read existing specs to fetch constraints instead of rewriting them.
- Any change packet should contain the difference from the canonical surface
  rather than full-state duplication.

## 4. Shared Coordinate Rule

Nodes must use `CURRENT-SURFACE-MANIFEST.json` for repository-local routing
and open only the explicitly re-admitted affected surface. Nodes must avoid
generating parallel reader orders or treating historical registers as shared coordinates
their operational framework.

## 5. Single Review Surface Rule

A task should not undergo duplicated review processes if it has successfully
passed the designated review layer. The structural review conducted by the
coordinating node acts as the bridge; once confirmed structurally aligned,
the output should proceed to final validation without redundant re-checks.

## 6. Return-to-Register Rule

To ensure that progress is preserved and redundant effort is minimized, all
completed tasks and successfully reduced loads must document their final state
in a designated registry. This allows future operations to refer to the
registered state instead of re-calculating it.

## 7. Failure Route: return_failed -> AXIS-05

If a process fails to correctly reduce load, encounters an ambiguity in the
delta, or fails to properly write back to the shared coordinate, the node must
halt and direct the failure exactly via:
`return_failed -> AXIS-05`

## 8. mismatch_or_gap

- Current registries track files but may not consistently track context
  boundaries, leading to minor overlap.
- Unmerged execution branches could still trigger redundant load during
  topology sweeps.

## 9. unresolved_risks

- Over-reducing context could result in node amnesia, causing the node to lose
  critical domain understanding.
- Delta-only parsing relies on nodes having a perfect base state, which may
  be misaligned.

## 10. next_single_recommended_action

Do not append this specification to a historical register or corpus index.
If materially affected, route through `CURRENT-SURFACE-MANIFEST.json` and the
explicitly re-admitted affected surface.
