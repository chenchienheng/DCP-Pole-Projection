# AGENTS.md｜Repository Agent Rules

## Repository Role

This repository is a public DCP-oriented CoreTri projection carrier. It preserves repository revisions and bounded public evidence; it is not the DCP Native Source Root, Native Current, Canon, or Architecture Authority.

Agents working here are scope-bounded review, cleanup, test, and minimal-patch carriers. These repository instructions apply only to authorized work in this repository; they do not set another project's role or grant new authority.

## Allowed Work

Agents may:
- inspect pull request diffs;
- list changed files;
- identify mergeability blockers;
- identify out-of-scope file changes;
- preserve already-merged content from `main`;
- keep pull requests within the requested scope;
- propose minimal safe patches;
- apply minimal edits only when explicitly requested;
- run safe local checks when available.

## Not Allowed

Agents must not:
- redefine core architecture;
- create new architecture axes;
- rewrite core doctrine;
- modify identity-core documents unless explicitly requested;
- convert documentation into runtime behavior;
- introduce API, database, background execution, or automation semantics unless explicitly requested;
- merge pull requests automatically;
- remove architecture content without explicit instruction;
- promote pending concepts into finalized doctrine.

## Governance Roles

- Task-selected models and agents are replaceable, scope-bounded carriers; their names do not establish permanent roles or Authority.
- Repository maintenance executors may inspect, patch, test, and return evidence only within the granted task scope.
- GitHub is the repository revision/evidence carrier and pull-request gate; it is not the Native Source Root or Architecture Authority.
- User: final approval and merge authority.

## Review Gates

Before editing, resolve the repository full name, selected ref, actual HEAD, and named environment when one is used. For PR work, resolve the repository's current base ref separately from the PR's recorded base SHA; a recorded base SHA can lag the current branch.

If a historical ref is missing, inspect its linked PR/commit provenance and current task need before proposing a replacement. Do not blindly retry or recreate the old branch. If the PR targets a candidate branch, preserve that dependency rather than silently retargeting it to main.

Then check:
1. What pull request or branch is the target?
2. What files are in scope?
3. What files are outside scope?
4. What already-merged content must be preserved?
5. What is the minimum safe patch?

## Scope Rules

If a pull request includes files outside scope:
- report diff pollution;
- propose removing the file from the pull request diff;
- do not rewrite the file unless explicitly instructed.

If a pull request conflicts with latest `main`:
- preserve all already-merged content;
- update or rebase only if the task asks for cleanup;
- do not overwrite prior merged artifacts.

If wording implies runtime, API, database, or automatic system execution:
- flag it as a scope risk;
- suggest neutral documentation, register, review-note, or calibration wording.

## Local Blockers and Evidence

A blocker holds only actions that depend on it. Continue already-authorized independent work; do not widen scope or replace a required approval to avoid a blocker.

Keep saved configuration, session-loaded instructions, and observed runtime behavior as separate evidence states. A repository patch or environment setup success does not prove an existing session loaded the revision.

Keep local completion, delivery, receiver readback, and actual receiver use separate. Do not infer approval from a candidate, CI success, a saved file, or a producer's own receipt.

## Default Output Format

Lead with the outcome and its practical impact in clear Traditional Chinese. Prefer concise paragraphs or at most three top-level points; expand only when the task requires it. Avoid ASCII diagrams, nested lists, and forced report templates unless the requested deliverable needs them.

Preserve the material status, changed files, out-of-scope changes, risks, minimal patch, verification limits, and any human decision needed without forcing a fixed checklist into every response.

Synthetic examples and one-task constraints remain examples and local constraints; do not promote them into repository-wide or cross-project rules.

## Final Rule

Do not merge automatically. Final approval remains with the user.
