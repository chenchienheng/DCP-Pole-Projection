# XuanLing-LingLuo Master Map

> Historical reference. This document preserves an earlier design or index snapshot, not current runtime, authority, writer assignment, or verified operational status. Terms such as “Active”, “current”, and “verified” below belong to that historical context. Consult the repository’s [current surface manifest](CURRENT-SURFACE-MANIFEST.json) for present source qualification. Historical content is retained unchanged; reuse requires current evidence.

## 1. Core Definition
This document serves strictly as a mapping artifact to clarify the structural
and conceptual relationships between DCP, CoreTri, XuanLing, Qinyi, and
LingLuo. It defines boundaries and positioning but does not introduce new
runtime execution, API behavior, or governing doctrine. It serves as a visual
and conceptual coordinate map to prevent layer collapse.

## 2. Layer Map
*   **DCP:** The outermost conceptual / constraint-governance framework.
*   **CoreTri:** The mother-architecture providing constraint chains, runtime
tracking, and stability axes (e.g., AXIS-01 through AXIS-05).
*   **XuanLing:** The operational model core that provides constraint adhesion,
field-semantics mapping, feasible-domain expansion, and return calibration on
top of CoreTri.
*   **Qinyi:** The public-facing, stabilized external interface submap bound by
the XuanLing architecture, managing interactions and signature boundaries.
*   **LingLuo:** The specific implementation or externalized identity
instantiation operating within the boundaries of the XuanLing operational model
and CoreTri axes.

## 3. Relationship Map
*   **DCP -> CoreTri:** DCP acts as the meta-layer vision, while CoreTri forms
the fundamental structural implementation constraints.
*   **CoreTri -> XuanLing:** XuanLing requires CoreTri's axes and constraint
chains to maintain operational stability. XuanLing is an
application/operational layer running inside CoreTri's rules.
*   **XuanLing -> Qinyi:** XuanLing manages and binds Qinyi as its public
external interface, ensuring Qinyi does not expose private core internals.
*   **XuanLing -> LingLuo:** LingLuo acts as a specific realization or specific
operational profile inside the XuanLing framework.

## 4. Why One Whitepaper Is Insufficient
Compressing all layers into a single whitepaper forces the merging of disparate
abstraction levels—meta-conceptual (DCP), structural (CoreTri), operational
(XuanLing), and interface (Qinyi/LingLuo). This compression results in:
*   Loss of explicit boundary definition between core stability and external
interfacing.
*   Inability to independently version or stabilize the operational layer
(XuanLing) without triggering mother-law rewrites (CoreTri).
*   High risk of exposing private internals through public interfaces by
blurring the lines between core architecture and external projection.

## 5. Recommended Documentation Structure
*   Maintain `XUANLING_OPERATIONAL_MODEL_CORE.md` as the definitive operational
constraints layer.
*   Maintain the current canonical Qinyi interface reference, and link to the
future Qinyi external interface submap once it is merged and registered.
*   Use this `XUANLING_LINGLUO_MASTER_MAP.md` purely as the cross-layer index
or coordinate map to orient contributors without redefining the components.
*   Avoid single monolithic documents; instead rely on distributed, highly
cohesive structural artifacts.

## 6. mismatch_or_gap
*   Historically, there has been a tendency to blend LingLuo operational
details with XuanLing core constraints.
*   Current structure ensures they are conceptually distinguished but may
require further operational boundary testing in practice.

## 7. next_single_recommended_action
*   Validate the relationships outlined in this map against existing specs,
review notes, and registered artifacts to ensure alignment with the stated
boundaries.
