# Research index

**Last `/gr` pass: 2026-09-02 (estate sweep) — FULL** (dossier read in full, both topics re-read, board read)**.** Inbox was empty. The board's blocking question — does UE3's D3D9 RHI ever request `D3DPOOL_MANAGED` — has **no public answer** and should not be searched again; the instrumented launch stands. What the pass adds is a reframing: the trap belongs to the D3D9Ex *route*, and the game ships a **D3D10 RHI behind a public `-d3d10` argument** with native DXGI sharing, at the cost of a cbuffer-style injection. One topic; pointer in `engine-research/inbox/`. The console question (§7) stays a live check — the one public thread 403s.

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-02 | [The `D3DPOOL_MANAGED` question has no public answer — but the compiled-in D3D10 path would sidestep it entirely](topics/2026-09-02-the-managed-pool-question-has-no-public-answer-but-the-d3d10-path-sidesteps-it.md) | 🆕 new | No public source states what UE3's D3D9 RHI does with the managed pool `[checked]`; keep the instrumented launch. But §9's trap is a property of the D3D9Ex route: the shipped D3D10 RHI (`AllowD3D10` / public `-d3d10` argument) shares surfaces natively through DXGI, with keyed mutexes, and needs no Ex upgrade — at the cost of redoing the camera injection as a constant-buffer patch (playbook §3.5) with the SM4 shader cache as the reflection source. A route decision for after the rock test, not a change to it. |
| 2026-09-01 | [The D3D9→VR-runtime bridge is already solved in a sibling project](topics/2026-09-01-the-d3d9-to-vr-runtime-bridge-is-already-solved-in-a-sibling-project.md) | 🆕 new | Answers §9's *"D3D9 + modern VR runtimes… known-solvable, but extra plumbing to plan for"* without a single search: `far-cry-2-vr` already published it. The route is Microsoft's documented **D3D9Ex ↔ D3D11** surface sharing (`D3D11_RESOURCE_MISC_SHARED` → `IDXGIResource::GetSharedHandle` → `IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)`), no CPU round-trip. 🪤 **The gotcha:** `..._SHARED_KEYEDMUTEX`, the primitive normally recommended for exactly this, **has no D3D9-side equivalent at all** — use an `IDirect3DQuery9` event query plus double/triple buffering instead. Also carries **OpenVR issue #1253**: SteamVR keeps only the *last* submitted per-eye pose, so alternate-eye designs that tag each eye with its own pose ghost badly — submit both eyes together. ⚠️ **Check first whether this game creates D3D9 or D3D9Ex** — the technique requires Ex, and the dossier does not record which. All `[reported]`; neither project has run it. |
| 2026-08-24 | [UE3 native stereo + community tooling recon](topics/2026-08-24-ue3-native-stereo-and-community-tooling.md) | 🆕 new | UE3's built-in `AllowNvidiaStereo3d` is driver-side automatic parallax (no head tracking, known to break shaders in sibling UE3 titles) — not a shortcut, skip it. No public camera/stereo mod exists for this game; only a config-based FOV/HUD fix and stock cheat trainers (no camera hack) were found. Confirms greenfield: the live d3d9 capture remains the only path to the SHARED-vs-per-object-matrix answer. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
