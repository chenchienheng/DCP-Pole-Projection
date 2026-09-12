# Failure Evolution Policy R1-00
State: BOUNDED_PUBLIC_PROJECTION_POLICY
Runtime: false
Canon: false

Success rate is not the primary evolution KPI.

Every material failure should preserve:
- cause
- affected scope
- correction
- regression fixture
- re-entry trigger
- successor pointer

Normal behavior:
- unchanged blocker -> memoized sleep, no busy loop
- stale/history retrieval -> lineage read only, never Current by search hit
- equivalent return/evidence -> semantic dedup
- local conflict -> local hold
- disjoint delta -> commute/merge
- producer return -> receiver-owned disposition/rebuild required

Evolution metrics:
Failure Recurrence Rate; Regression Escape Rate; Time-to-Detect; Time-to-Localize;
Affected-Scope Accuracy; Recovery Cost; Wrong-Wake Rate; Duplicate-Read Rate;
Second-run Cost; Manual-Routing Count; Successor Coverage;
Failure-to-Rule/Test/Reusable-Evidence Conversion.

Claim ceiling:
This file governs the public projection carrier's reading/return behavior only.
It does not establish Native authority, runtime, canon, legal approval, or professional approval.
