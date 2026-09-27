# External Ecosystem Absorption Schema (Proposal)

> Proposal for structurally mapping external nodes (Google ecosystem and agents)
> to the core framework axes without direct integration or runtime expansion.

---

## 1. Node Absorption Mapping

### 1.1 Google Drive (Carrying Mesh)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-04 (Space Chain)
- **input:** Drafts, historical field artifacts, raw reference material.
- **output:** Extracted Markdown texts, mirror snapshot links.
- **execution_boundary:** Acts as a mirror and draft layer. May not replace or
  override canonical GitHub bone files.
- **review_path:** Content destined for main must pass through `Qinyi-1`
  embedded Jules reviews.
- **return_path:** Markdown extraction via `04_adapter-layer/drive-adapter.md`.
- **fallback:** If synchronization or extraction fails, log to AXIS-05
  (Review Chain) via GitHub issues/registers.

### 1.2 Google Calendar (Time Node)
- **primary_axis:** AXIS-03 (Time Chain)
- **secondary_axis:** AXIS-01 (World Chain)
- **input:** Scheduling bounds, cadence window definitions (e.g., Window 06).
- **output:** Time-window alignment blocks, stage sync triggers.
- **execution_boundary:** Absorbed for cadence binding. Cannot independently
  initiate structural sweeps.
- **review_path:** Window alignment verified via `03_board-orchestration`.
- **return_path:** Syncs via routing logs in
  `04_adapter-layer/calendar-adapter.md`.
- **fallback:** If time alignment fails, revert to manual cadence gating and log
  to AXIS-05.

### 1.3 Google Meet (Bridge Surface)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** none
- **input:** Synchronous communication, multi-party verbal negotiation.
- **output:** Written decisions, action items.
- **execution_boundary:** Transient intake surface only.
- **review_path:** Notes must be synthesized into a proposal document before PR.
- **return_path:** Decisions written back to GitHub issues or PRs.
- **fallback:** If unrecorded, no decision is valid. Escalate to AXIS-05.

### 1.4 Google Docs (Sub-bone)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** none
- **input:** Multi-party live text editing.
- **output:** Canonical text blocks for extraction.
- **execution_boundary:** Staging ground only.
- **review_path:** Must pass Review Chain Master Layer before merge.
- **return_path:** Structured export to `.md` via Seed Extraction (M1).
- **fallback:** Discard unverified drafts, flag to AXIS-05.

### 1.5 Stitch (Orchestration Agent)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-03 (Time Chain)
- **input:** Repository registry artifacts, GitHub issues, Window bindings.
- **output:** Routing assignments, mirrored task boards, isolated seeds.
- **execution_boundary:** Cannot autonomously rewrite `main` branch rules or
  independently close issues.
- **review_path:** Taskboard sync outputs reviewed via PRs or Issue checks.
- **return_path:** Commits cross-link validations and mirror updates to GH.
- **fallback:** Halt orchestration loop, return control to AXIS-05.

### 1.6 Jules (Execution Agent)
- **primary_axis:** AXIS-02 (Existence Chain)
- **secondary_axis:** AXIS-01 (World Chain)
- **input:** Execution lanes (Lane A, B, C), specific issue task packets.
- **output:** Normalization commits, registry reconciliations, cleanup queues.
- **execution_boundary:** Bound to Writeback Chain. Must not flat-merge legacy.
- **review_path:** All outputs must pass Review Chain (AXIS-05).
- **return_path:** PR submission and `CLEANUP_QUEUE_REGISTER.md` logging.
- **fallback:** Output traces to queue if API fails; escalate to AXIS-05.

### 1.7 Gemini (Audit Mirror)
- **primary_axis:** AXIS-05 (Review Chain)
- **secondary_axis:** AXIS-01 (World Chain)
- **input:** Canonical source paths (`source_map.md`), repository state diffs.
- **output:** Contradiction flags, mismatch gaps, synthesis summaries.
- **execution_boundary:** Structural comparator only, not a decision-maker.
- **review_path:** Output fed back into Human/Jules review loops.
- **return_path:** PR comments or issue updates.
- **fallback:** If output contradicts GitHub bone state, GH state prevails.
  Log contradiction to AXIS-05.

### 1.8 ChatGPT_Image_2 (Image Generation Node)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-05 (Review Chain)
- **input:** Prompt (text description), style constraint (style language).
- **output:** Image (image result), variation (different versions).
- **execution_boundary:** Generates images only. Not responsible for brand
  consistency decisions.
- **review_path:** Checks style compliance (color / light / composition).
  Checks for character deviation (Qin-Yi).
- **return_path:** Returns to main chain (as an asset node).
- **fallback:** AXIS-05 (Review / Regeneration).

### 1.9 Claude_Code (Code Orchestration Node)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-02 (Existence Chain)
- **input:** Issue packets, codebase context, architecture documentation.
- **output:** Pull requests, architectural drafts, structural updates.
- **execution_boundary:** Operates on code and architecture definition. Must
  not unilaterally redefine doctrine or bypass review chains.
- **review_path:** Output passes through PR review by Human/Jules.
- **return_path:** Commits to GitHub branch, updates to registers.
- **fallback:** AXIS-05 (Review Chain).

### 1.10 GPT-5.5 (Advanced Reasoning Node)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-05 (Review Chain)
- **input:** Complex ambiguity blocks, high-level structural proposals.
- **output:** Synthesis reports, resolution schemas, contradiction mappings.
- **execution_boundary:** Used for high-level reasoning and synthesis, not for
  unsupervised execution or state mutation.
- **review_path:** Requires human oversight or cross-model audit.
- **return_path:** Markdown reports or PR comments.
- **fallback:** AXIS-05 (Review Chain).

### 1.11 OPF (Privacy Filter)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-05 (Review Chain)
- **input:** Outbound data streams, prompts, structural payloads.
- **output:** Sanitized payloads, redacted prompts.
- **execution_boundary:** Must intercept before external network calls.
  Cannot generate content, only filter.
- **review_path:** Filter rules audited through rule-definition PRs.
- **return_path:** Forwards sanitized payload to target node.
- **fallback:** Block transmission and log to AXIS-05 (Review Chain).

### 1.12 Whisper (Audio Intake Node)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** none
- **input:** Voice recordings, synchronous audio streams.
- **output:** Raw text transcripts.
- **execution_boundary:** Transcription only. Does not interpret or synthesize
  meaning from text.
- **review_path:** Transcripts passed to reasoning node (e.g., Gemini) for
  structuring.
- **return_path:** Text appended to intermediate storage or PRs.
- **fallback:** AXIS-05 (Review Chain).

### 1.13 Image_2 (Supplemental Vision Node)
- **primary_axis:** AXIS-01 (World Chain)
- **secondary_axis:** AXIS-05 (Review Chain)
- **input:** Visual assets, diagrams, structural screenshots.
- **output:** OCR text, structural analysis, bounding boxes.
- **execution_boundary:** Reads images for state extraction. Does not mutate
  state independently.
- **review_path:** Output verified against known text registers.
- **return_path:** Extracted state written back to MD logs.
- **fallback:** AXIS-05 (Review Chain).

---

## 2. Structural Analysis

### 2.1 mismatch_or_gap
- The OPF (Privacy Filter) node requires a formal rule engine and dictionary
  definition that currently does not exist.
- Advanced reasoning models (GPT-5.5, Claude_Code) require specific API
  invocation contracts to prevent autonomous capability drift.
- The physical `AXIS_TO_EXTERNAL_ABSORPTION_HANDOFF.md` document is not present
  in the repository.
- There is currently no active automated pipeline enforcing these boundaries,
  leaving them as manual rule-checking disciplines.
- Some tools (Meet, Docs) lack formal adapter schemas comparable to Drive or
  Calendar.

### 2.2 unresolved_risks
- **Data Leakage Risk:** If OPF logic fails or is bypassed, sensitive structural
  data might leak to external model APIs.
- **Autonomous Drift Risk:** Extremely capable nodes like GPT-5.5 and
  Claude_Code might attempt to rewrite fundamental doctrine if their boundaries
  aren't strictly verified.
- **Capture Risk:** Without rigid enforcement, Google Drive or Docs might still
  be treated as the definitive source of truth by users bypassing the bone.
- **API Failure:** Dependency on manual logging (e.g., if `$GITHUB_TOKEN` fails)
  may cause `CLEANUP_QUEUE_REGISTER.md` to bottleneck.

### 2.3 next_single_recommended_action
- This proposal carries no approval or active-register binding. If materially
  affected, route through `CURRENT-SURFACE-MANIFEST.json` to an explicitly
  re-admitted affected surface; any separate handoff remains independently gated.
