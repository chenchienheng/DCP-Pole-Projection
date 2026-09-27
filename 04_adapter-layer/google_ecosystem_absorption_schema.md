# Google Ecosystem Absorption Schema

> Canonical mapping and absorption rules for the Google ecosystem within the
> XLEN / Xuanling runtime.
> Purpose: Define how Google surfaces, models, and execution tools map to the
> core axis structure, without expanding the runtime or enacting direct tool
> integration.

---

## 0. Core Reading

The Google ecosystem is not treated as a sovereign center. It is a high-value
external node cluster that must be absorbed through strict structural mapping.

This schema maps the Google ecosystem to:
- Bone Chain (Structural stability)
- Event Chain (Triggers and intake)
- Writeback Chain (Durable return)
- Review Chain (Audit and alignment)

---

## 1. Structural Mapping (design.md)

Google structural surfaces map to the **Carrying Mesh** and **Time Node** roles.

| Google Tool | Core Structural Role | Absorption Rule | Writeback Constraint |
| --- | --- | --- | --- |
| Google Drive | Carrying Mesh / Historical Field | Draft transit and mirror layer. Does not replace GitHub bone. | Must link to canonical GitHub artifacts. |
| Google Calendar | Time Chain Node / Cadence | Absorbed for Window 06 / cadence binding. | Syncs with `03_board-orchestration` routing logs. |
| Google Meet | Bridge Chain / Intake | Transient intake surface for synchronous events. | Significant decisions must return to GitHub issues. |
| Google Docs | Draft Transit / Sub-bone | Staging ground for multi-party edit before commit. | Content for `main` must pass Review Chain. |

---

## 2. Stitch Skills Mapping

Stitch functions as an orchestration and routing agent. Within the DCP
framework, its skills map to the **Bridge Chain** and **Event Chain**.

| Stitch Skill Group | Framework Mapping | Execution Boundary |
| --- | --- | --- |
| Repository Read | Window 03 (Stage Sync) | Reads registry artifacts to provide context. |
| Task Board Sync | Window 00 (Schedule Hub) | Mirrors issues. Cannot close issues independently. |
| Artifact Extraction | Seed Extraction / M1 | Extracts fields from Drive/Docs into MD format. |
| Cross-link Validation | Dependency Link (Lane B) | Can flag ghost links; must not rewrite `main` rules. |

---

## 3. Jules Execution Pattern

Jules operates as a bounded execution node within the embedded `Qinyi-1` runtime
window.

### 3.1 Mapping to Core Lanes
- **Lane A:** Resolves repository-local routing through
  `CURRENT-SURFACE-MANIFEST.json`, then returns only to an explicitly
  re-admitted affected surface.
- **Lane B:** Fixes cross-link drift within the 5 Master Axes.
- **Lane C:** Normalizes naming and isolates legacy seeds.

### 3.2 Absorption Rule
- Jules is strictly bound to the **Writeback Chain**.
- Jules must never perform "flat-merge" of legacy branches.
- Jules must output execution traces to `CLEANUP_QUEUE_REGISTER.md` if issue
  mutation via API fails.
- All Jules output must pass the **Review Chain Master Layer** (AXIS-05).

---

## 4. Gemini Mirror Role

Gemini functions within the **Model / Reasoning Family** (Category F).

### 4.1 Structural Role
Gemini acts as the **Audit / Comparison Node** and **Synthesis Mirror**. It is
not the final decision-maker but the structural comparator.

### 4.2 Absorption Rule
- **Input Binding:** Gemini must be fed canonical paths (`source_map.md`)
  before analysis.
- **Output Contract:** Gemini must output structured contradiction flags or gaps
  rather than unbound text.
- **Arbitration:** If Gemini contradicts GitHub state, the GitHub state
  prevails.

---

## 5. Status

- absorption_schema_created: true
- tool_integration_expanded: false
- execution_pattern_mapped: true
- return_to_00: true
