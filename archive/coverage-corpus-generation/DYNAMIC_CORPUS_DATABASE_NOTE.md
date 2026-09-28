# Historical snapshot — DYNAMIC_CORPUS_DATABASE_NOTE.md

> Lifecycle: `HISTORICAL_REFERENCE`
> Current authority: `false`
> Runtime: `false`
> Source commit: `b5575b199d8ac5bd636281dbf7c4eef9ee382adb`
> Source path: `DYNAMIC_CORPUS_DATABASE_NOTE.md`
> Original Git blob: `3872a7e310bf508ea7ceb7ebed566271e4f5dad3`

This preserved body is evidence of an earlier design. Its commands, roles, schedules, status flags and next actions are historical, not instructions to execute. Use the directory [index](README.md) for successor context. The source body below is preserved verbatim.

<!-- BEGIN VERBATIM HISTORICAL BODY -->
# Dynamic Corpus Database Note

> Durable note for the next-stage treatment of the XLEN / Xuanling text corpus.
> The repository corpus should not remain a static pile of documents.
> It must evolve toward a dynamic corpus database.

---

## 0. Core Reading

The current corpus is already large and structurally rich.
Its main problem is no longer lack of writing.
Its main risk is this:

- if it remains static, it becomes storage only
- if it becomes storage only, it risks turning into low-value residue or contamination

Therefore the next-stage requirement is:

> historical corpus must be inductively organized into a **dynamic corpus database**

---

## 1. Why Static Placement Is Not Enough

Static storage alone cannot guarantee:
- role clarity
- historical induction
- live routing
- runtime usefulness
- contamination control
- cluster coverage visibility

A static corpus can preserve memory,
but cannot by itself produce living operational value.

---

## 2. Dynamic Corpus Database Definition

A dynamic corpus database means the corpus is treated as:
- queryable
- classifiable
- updatable
- routable
- writeback-aware
- historically inductive
- cluster-aware

It is not merely a folder tree.
It is not merely a note vault.
It is not merely search.

It is a runtime-capable historical field.

---

## 3. Minimum Required Properties

### 3.1 Historical Induction
The system must not only store history.
It must derive:
- role evolution
- wording drift
- branch lineage
- contamination patterns
- recurring structural seeds

### 3.2 Dynamic Classification
Each artifact should be dynamically classifiable by:
- structural family
- chain face
- contamination status
- priority level
- handling mode
- window binding
- branch origin

### 3.3 Query and Routing Usefulness
The database should support questions such as:
- what belongs to mother architecture?
- what is clean seed vs residue?
- which artifacts bind to window 06?
- what should be extracted from the legacy seed branch first?
- which notes are bridge-only vs sovereignty-bearing?

### 3.4 Writeback Awareness
Every important update should be able to write back into the corpus state.
The database must not become read-only memory.

### 3.5 Cluster Coverage Reading
The corpus should be readable not by file count only,
but by how much of the broader structural field is actually covered and made operable.

---

## 4. Proposed Dynamic Record Schema

Each artifact record should eventually include fields such as:

- artifact_id
- path
- branch_origin
- structural_family
- network_role
- chain_face
- window_binding
- contamination_status
- priority_level
- handling_mode
- historical_lineage
- writeback_state
- cluster_coverage_tags
- last_verified_time

---

## 5. Operational Reading

The database is not an optional convenience layer.
It is the next necessary evolution because:
- the corpus has crossed the threshold where manual memory alone is insufficient
- branch divergence already exists
- contamination triage already exists
- family classification already exists
- scheduling activation is becoming necessary

Therefore a dynamic database is now a structural necessity.

---

## 6. Immediate Build Direction

The build should proceed in layers:

### Layer A — Durable Registers
Use current notes as seed registers:
- corpus index
- role classification
- discontinuity register
- contamination policy
- branch topology register
- seed branch inventory and triage
- window master table
- scheduling gap note

### Layer B — Unified Artifact Register
Create a single registry that can list artifact-level metadata.

### Layer C — Dynamic Queries and Routing
Make the registry usable for:
- extraction
- cleanup
- merge candidate selection
- scheduling ownership
- external-node binding

### Layer D — Feedback and Auto-updating
Allow writeback from new actions so the database evolves rather than freezes.

---

## 7. Main Risk if Not Built

If this step is skipped, the corpus may become:
- impressive in volume
- weak in live usefulness
- hard to navigate
- easy to contaminate
- slow to evolve coherently

That would turn a high-value seed field into a static residue mass.

---

## 8. Suggested Next Artifacts

1. `UNIFIED_ARTIFACT_REGISTER.md`
2. `ARTIFACT_RECORD_SCHEMA.md`
3. `CLUSTER_COVERAGE_MATRIX.md`
4. `SCHEDULING_EFFECT_REGISTER.md`
5. future machine-readable registry layer

---

## 9. Status

- dynamic_corpus_database_direction_persisted: true
- static_storage_risk_named: true
- unified_artifact_register_pending: true
- machine_readable_layer_pending: true
- return_to_00: true
