# Repository Status / 倉庫狀態

**Repository class / 倉庫分類:** Public research and reference corpus  
**Architecture maturity / 架構成熟度:** Evolving; bounded structural convergence  
**Operational status / 運作狀態:** Non-production  
**Runtime evidence / Runtime 證據:** Not established  
**Authority elevation / 權限升格:** None implied by repository content  
**Release control / 發布控制:** Explicit

## Status statement / 狀態說明

This repository contains the externally reviewable research and reference surface of the DCP framework. The corpus includes conceptual work, bounded structural models, interface candidates, validation artifacts, historical research evidence, and repository-level documentation.

本倉庫承載 DCP Framework 可供外部審閱的研究與參考表面，包含概念研究、有限結構模型、介面 Candidate、驗證成果、歷史研究證據與倉庫層文件。

Repository contents do not, by themselves, establish production deployment, autonomous decision authority, architectural promotion, regulatory compliance, or correctness beyond the evidence scope declared by each artifact.

倉庫內容本身不構成 Production Deployment、Autonomous Decision Authority、Architecture Promotion、Regulatory Compliance，也不會使任何成果超出其聲明的 Evidence Scope。

## Current public architecture surface / 現行公開架構表面

The current public surface is organized around two bounded candidates:

- **DCP Life-Chain Dependency Model** — a working architecture candidate for dependency, lifecycle state, authority, evidence, return, reconciliation, and recovery reasoning.
- **Cross-Carrier Projection Compatibility** — an interface candidate defining continuity requirements across heterogeneous documentation and workflow carriers.

現行公開表面以兩個有限 Candidate 為主要技術入口：DCP Life-Chain Dependency Model，以及 Cross-Carrier Projection Compatibility。兩者均屬研究／介面層成果，不代表已部署 Runtime。

## Evidence and maturity model / 證據與成熟度模型

Maturity is evaluated per artifact and per claim. Evidence of a structural rule, interface property, validation result, or implementation artifact is not automatically evidence of deployment, owner acceptance, production readiness, or domain-wide applicability.

成熟度依 Artifact 與 Claim 分別判定。Structural Rule、Interface Property、Validation Result 或 Implementation Artifact 的證據，不自動證明 Deployment、Owner Acceptance、Production Readiness 或跨 Domain 適用性。

Historical material may remain in the repository for provenance, comparison, failure analysis, and reproducibility. Historical retention does not make an artifact current.

歷史材料可因 Provenance、比較、Failure Analysis 與 Reproducibility 需求繼續保存；保存本身不會使其成為 Current Artifact。

## Source and authority boundary / 來源與權限邊界

The repository is not a native data root. Native source ownership, access rights, retention, mutation, and publication remain governed by the lawful source and its applicable authority chain.

本倉不是 Native Data Root。Native Source 的所有權、存取權、Retention、Mutation 與 Publication 仍由合法來源及其適用 Authority Chain 管理。

Public documentation contains only release-appropriate representations. Protected implementation details, privileged routing, private evidence lineage, sensitive source relationships, and restricted native bodies remain outside the public corpus.

公開文件只承載適合發布的表徵；受保護的 Implementation Detail、Privileged Routing、Private Evidence Lineage、敏感 Source Relationship 與 Restricted Native Body 不屬於公開語料。

## Representation and release status / 表徵與發布狀態

Public documentation follows the repository representation architecture:

- **Human Profile / 人類閱讀層:** Traditional Chinese
- **External Profile / 外部交換層:** English
- **Canonical Machine Profile / 機器規範層:** stable identifiers, typed states, versions, and release-safe evidence references

The profiles must remain semantically equivalent for stable identity, lifecycle state, authority scope, claim/evidence ceiling, successor relation, and release classification.

三個表徵層在 Stable Identity、Lifecycle State、Authority Scope、Claim／Evidence Ceiling、Successor Relation 與 Release Classification 上必須維持語義等價。

Disclosure and publication controls are specified in `PUBLIC-SURFACE-POLICY.md`.

揭露與發布控制見 `PUBLIC-SURFACE-POLICY.md`。

## Reading guidance / 閱讀指引

Use `README.md` for human orientation, `CURRENT-SURFACE-MANIFEST.json` for Current-for-purpose, and this status document for maturity and disclosure scope. Artifact-specific lifecycle state and evidence scope should then be read from the relevant issue, document, release, or provenance reference.

請以 `README.md` 作人類定位、`CURRENT-SURFACE-MANIFEST.json` 解析 Current-for-purpose，本文件判定 Maturity 與 Disclosure Scope；再依具體 Issue、Document、Release 或 Provenance Reference 判讀各 Artifact 的 Lifecycle State 與 Evidence Scope。

Repository location, filename, branch presence, issue state, search ranking, and modification time are navigation metadata; none establishes architectural truth or operational maturity on its own.

Repository 位置、檔名、Branch Presence、Issue State、Search Ranking 與 Modification Time 均屬 Navigation Metadata，不能單獨建立 Architecture Truth 或 Operational Maturity。

## Current development focus / 現階段研究重點

Current work emphasizes:

- reducing duplicated interpretation and reader load;
- improving evidence reuse and provenance continuity;
- preserving identity across carrier and placement changes;
- strengthening return, reconciliation, and recovery semantics;
- validating bounded change propagation and affected-scope reconstruction;
- maintaining explicit source, authority, evidence, and release boundaries.

現階段工作聚焦於降低重複判讀與 Reader Load、提升 Evidence Reuse 與 Provenance Continuity、維持跨 Carrier 的 Identity Continuity、改善 Return／Reconciliation／Recovery 語義，以及驗證有限變更傳播與受影響範圍重建。

This status page is descriptive. It is not a promotion decision, runtime receipt, release authorization, or authority grant.

本狀態頁僅描述目前可支持的 Claim Ceiling；不構成 Promotion Decision、Runtime Receipt、Release Authorization 或 Authority Grant。
