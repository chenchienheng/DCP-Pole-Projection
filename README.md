# DCP Pole Projection / DCP 極向投影

**Repository class / 倉庫分類：** Public pole-oriented projection carrier  
**Operational status / 運作狀態：** Non-production  
**Authority model / 權限模型：** Repository ≠ Pole Authority; no implicit runtime, promotion, or decision authority

## Overview / 概述

This repository is a GitHub projection surface shaped by the CoreTri architecture. It is **not** the DCP pole itself and does not replace the lawful DCP Native Source Root.

本倉是 CoreTri 三極架構在 GitHub 生態中的 **DCP 極向投影面**；它不是 DCP 極本體，也不取代合法的 DCP Native Source Root。

Its emphasis is Dependency / State / Authority / Admission / Evidence / Return / Reconciliation / Re-entry / Rebuild / Metabolism. The same stable existence may be represented differently in Ideas- and GLModel-oriented projections while preserving identity, lineage, authority boundaries, claim ceilings, and return relations.

本倉偏重 Dependency／State／Authority／Admission／Evidence／Return／Reconciliation／Re-entry／Rebuild／Metabolism。同一 Stable Existence 可在 Ideas 與 GLModel 極向投影中呈現不同形態，但 Identity、Lineage、Authority Boundary、Claim Ceiling 與 Return Relation 不得漂移。

## Tri-pole architecture / 三極架構

The three GitHub repositories are **not a one-repository-per-pole authority split**. All three use the same tri-pole architecture and may carry bounded representations from DCP, Ideas, and GLModel when lawful and useful. Each repository only gives different projection weight and reader entry.

三個 GitHub 倉庫不是「一倉＝一極 Authority」的切割。三倉都使用同一套三極架構，並可在合法、必要且有界的前提下承載 DCP／Ideas／GLModel 的不同表徵；差異在於投影重心與 Reader Entry，而不是建立三份 Truth。

- **DCP-Pole-Projection** — dependency/state/authority/rebuild oriented projection.
- **Ideas-Pole-Projection** — meaning/placement/navigation/experience oriented projection.
- **GLModel-Pole-Projection** — world/object/engineering/evidence/adapter oriented projection.

Cross-repository continuity should travel through bounded pointer / receipt / receiver-state / return / reconciliation / rebuild relations rather than copied native bodies. A shared belt is an interlock mechanism, not a fourth pole and not a shared authority root.

跨倉連續性應透過 bounded pointer／receipt／receiver-state／return／reconciliation／rebuild relation 互鎖，而不是複製 Native Body。Shared Belt 是三倉互鎖機制，不是第四極，也不是共同 Authority Root。

## Current reader entry / 現行讀取入口

Use this README for human orientation, then resolve Current-for-purpose from `CURRENT-SURFACE-MANIFEST.json`. Legacy root-layer families remain Historical／Compatibility unless explicitly re-admitted; repository location, filename, recency, or searchability does not establish Current.

本 README 提供人類入口與倉庫定位；Current-for-purpose 請由 `CURRENT-SURFACE-MANIFEST.json` 解析。

## On-demand artifact receiver / 按需交付接收器

The existing local host and its receiver reconciliation are available from the normal `dcp_kernel` package. For the specific task **verify that downloaded files match an expected delivery**, use `ArtifactDeliveryContract`, `prepare_artifact_delivery` and `receive_artifact_delivery`. This receiver actually opens regular files, checks exact size/SHA256 twice and then reuses the host reconciliation. Producer-provided completion flags are not an input to the receiver.

用途是核對交付位元組，不是認證文件內容、遠端身分或替其他 Native 驗收。`prepare` 只建立待核結果；`receive` 讀回檔案並接續接受驗證結果，不包含原上傳器或重做原操作。原檔不被修改，輸出 JSON 為 create-only。已有人工作用時，請在契約中保留 `manual_interventions`。

Run from a checkout containing this candidate, with Python >=3.11 on a POSIX host supporting directory-relative/no-follow file opens:

```sh
python -m tools.verify_artifact_delivery prepare --contract expected.json --root ./source --output pending.json
python -m tools.verify_artifact_delivery receive --contract expected.json --root ./downloaded --pending pending.json --output accepted.json
```

`expected.json` is a trusted-source input, not a receipt generated from whichever download happened to arrive. Required fields are `delivery_id`, `source_id`, `source_revision`, `receiver`, and a nonempty `artifacts` list. Each entry has a canonical relative `path`, lowercase 64-character `sha256`, and nonnegative integer `size_bytes`. `manual_interventions` is an optional string list. Supply actual expected values from a pinned source. Do not publish private IDs or source bodies in this repository.

Exit status: 0 means the command's own phase succeeded (prepare remains PRODUCED; receive reports its verification result), 3 means unresolved verification, 2 means invalid input or I/O/publication failure. Output files must not already exist or overlap input files. A missing/corrupted file, symbolic link, substituted source/revision/receiver, duplicate JSON key, or second-read difference does not become accepted by asserting `verified=true`.

The trusted connector or local acquisition supplies the resource identity and authorization context. The byte receiver does not independently authenticate that provider, provide an atomic multi-file snapshot, or grant external writes. Unsupported file-open primitives fail closed. This is one reusable verification consumer, not a required pipeline for unrelated work.

### Resume and source delivery / 中斷接續與可執行原碼包

The `--pending` input now accepts either `pending.json` or the complete JSON check returned by a previous `receive`. A saved success or HOLD is only re-entry context: the receiver still reopens and verifies the actual received files. Missing files can arrive later without rebuilding the prepared source observation or losing the old HOLD evidence; write the new result to a new output path.

```sh
python -m tools.verify_artifact_delivery receive --contract expected.json --root ./downloaded --pending accepted.json --output rechecked.json
python -m tools.verify_artifact_delivery receive --contract expected.json --root ./downloaded --pending accepted.json --output rechecked.json --resume
```

Without `--resume`, existing output still causes an error. With explicit `--resume`, the CLI rechecks the inputs and reuses only a regular, unchanged, byte-identical output. Different evidence, input overlap, symlinks and special files remain blocked; no existing result is overwritten. This recovers a lost publication response, not a global exactly-once protocol or a promise that source files never change.

Successful candidate-head CI now also produces `dcp-source-checkout-candidate-head`: an exact tracked Git source archive plus its checkout/hash receipt. The archive is reopened in a temporary directory and the normal CLI and resume tests run there without installing dependencies. Extract `dcp-source-checkout.zip`, then run the commands above from that source directory. This is a candidate source delivery, not a main merge, deployment or release approval. The original census artifact, triggers and token permissions remain unchanged.

## Continuity and replaceable carriers / 連續性與可替換載體

Repository, model, tool, and storage locations are **replaceable carriers**, not permanent topology. For a bounded Need, continuity depends on re-qualifying Stable Identity / Need, Current-for-purpose, Authority, Evidence, Return and Rebuild relations when a carrier changes. A newer location, successful write, clean merge, or available capability does not by itself prove continuity, admission, delivery, or use.

Repository、模型、工具與儲存位置都是**可替換載體**，不是永久拓撲。對一個有界 Need 而言，載體變更時必須重新資格化 Stable Identity／Need、Current-for-purpose、Authority、Evidence、Return 與 Rebuild 關係。較新的位置、寫入成功、可乾淨合併或能力可用，都不能單獨證明連續性、Admission、Delivery 或 Use。

DCP-oriented maturity is therefore measured by whether dependency/state/authority/evidence/return relations remain recoverable and correctly bounded across interruption or carrier replacement, not by repository, artifact, PR, model or tool count.

因此 DCP 極向的成熟度，以中斷或載體替換後，Dependency／State／Authority／Evidence／Return 關係能否正確重取、恢復並維持邊界來衡量，而不是以 Repository／Artifact／PR／Model／Tool 數量衡量。

## Representation architecture / 三極語

- **Human zh-TW** — 人類理解、判斷、風險與下一步。
- **Professional / External English** — 專業互通與經核准的外部技術表達。
- **Canonical Machine State** — Stable IDs、typed relations/states、authority、evidence pointer、revision/hash、return/rebuild relation。

Presentation may differ; Identity, State, Authority, Claim Ceiling, Release Classification, Successor/Re-entry and Rebuild relation may not silently diverge.

## Public boundary / 公開邊界

Public placement does not create unrestricted rights or authority. Protected Personal / Company / Project source bodies, credentials, privileged routing, confidential evidence lineage, or material exceeding its rights/retention/release basis must stay in their lawful domains.

公開不等於無邊界。Personal／Company／Project 受保護 Source Body、憑證、特權路由、機密 Evidence Lineage，以及超出 Rights／Retention／Release Basis 的內容仍應留在合法權域。

## Machine metadata / 機器中繼資料

```yaml
repository_class: public_pole_projection_carrier
projection_focus: DCP
repo_is_pole_authority: false
runtime: false
native_source_root: false
tri_pole_architecture: true
shared_belt_role: pointer_receipt_receiver_state_return_reconcile_rebuild
representation_profiles:
  human: zh-TW
  professional: en
  machine: canonical
release_control: explicit
```

## License / 授權

**Creative Commons Attribution–NonCommercial–NoDerivatives 4.0 International (CC BY-NC-ND 4.0).**

## Citation / 引用

Chen, Chien-Heng. *DCP Framework: A Constraint-Based Model for Structured Judgment and Layered Interpretation*. Zenodo, 2026. DOI: https://doi.org/10.5281/zenodo.18111818

For disclosure and representation controls, see `PUBLIC-SURFACE-POLICY.md`.
