# Seed provenance — purpose-bound historical entry

> Applicability: historical reference; not an ordinary Current source or execution instruction.
> Runtime / Canon / new authority: not established by this document.

Retain the historical seed branch and shadow-board pointer as provenance. The predecessor instruction to read the shadow board first is not the normal entry for current work. Absence from main does not prove historical absence; historical existence does not establish Current or authority.

Normal repository reading starts with `CURRENT-SURFACE-MANIFEST.json` and its explicit reader declaration. A seed lookup needs a concrete provenance, compatibility, failure-analysis or recovery purpose and an independently qualified source/ref. Do not recreate or wake a branch from this pointer alone.

## Provenance and preservation

Applicability reviewed against candidate `a53ea529e237f5a7e281c6cbb5d7380ca55f07e3` and its explicit manifest. This is a bounded candidate edit, not main adoption or source retirement.
Selected source: #324 at `00999341ff600a65ab3de641e4ce5615d6e9690d`, same path, blob `ad58c20b85562fa47a1b760dfd0168b9c5b3862a`. Only the purpose/authority distinction stated above is adopted; no whole-PR import.
Preserved predecessor: same path at `a53ea529e237f5a7e281c6cbb5d7380ca55f07e3`, blob `2abddaf83f422347fa04203b06891ca3dba11cd2`; SHA256 `d179f1f71add7dfac26076f1b92606cf5a34ede95473956f0f6edff8c32c6a1d`.

<details>
<summary>Complete predecessor text — historical assertions, not current instructions</summary>

# Seed Shadow Pointer

一句核心：
main 保持穩定參照；若需接入 seed 中已成形、但尚未併幹的主骨，請先讀 seed 的 shadow board，而不是直接假設 seed 不存在。

## Read Path
- Branch: `xuanling-seed-v0-1`
- Suggested entry: `01_native-board/main-shadow-sync-board-v0-1.md`

## Why
- main 承接穩定可讀骨
- seed 承接高頻鍛造與候選結構
- shadow board 提供其他窗口與閱讀者的最小接入面

## Rule
- 不以 main 缺少某內容，判定 seed 不存在
- 需先讀 shadow board，再決定是否下探 seed source path

## Status
Pointer only

</details>
