# Research index

**Last `/gr` pass: 2026-09-01 — CHECK-IN.** Inbox was empty. One new topic, and it cost no web
searches: §9's D3D9→VR-runtime open risk is **already researched in a sibling project on this
account** (`far-cry-2-vr`, different engine, same Direct3D 9), down to a gotcha that would otherwise
cost a day. Found by holding every project's dossier in one sweep.

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-01 | [The D3D9→VR-runtime bridge is already solved in a sibling project](topics/2026-09-01-the-d3d9-to-vr-runtime-bridge-is-already-solved-in-a-sibling-project.md) | 🆕 new | Answers §9's *"D3D9 + modern VR runtimes… known-solvable, but extra plumbing to plan for"* without a single search: `far-cry-2-vr` already published it. The route is Microsoft's documented **D3D9Ex ↔ D3D11** surface sharing (`D3D11_RESOURCE_MISC_SHARED` → `IDXGIResource::GetSharedHandle` → `IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)`), no CPU round-trip. 🪤 **The gotcha:** `..._SHARED_KEYEDMUTEX`, the primitive normally recommended for exactly this, **has no D3D9-side equivalent at all** — use an `IDirect3DQuery9` event query plus double/triple buffering instead. Also carries **OpenVR issue #1253**: SteamVR keeps only the *last* submitted per-eye pose, so alternate-eye designs that tag each eye with its own pose ghost badly — submit both eyes together. ⚠️ **Check first whether this game creates D3D9 or D3D9Ex** — the technique requires Ex, and the dossier does not record which. All `[reported]`; neither project has run it. |
| 2026-08-24 | [UE3 native stereo + community tooling recon](topics/2026-08-24-ue3-native-stereo-and-community-tooling.md) | 🆕 new | UE3's built-in `AllowNvidiaStereo3d` is driver-side automatic parallax (no head tracking, known to break shaders in sibling UE3 titles) — not a shortcut, skip it. No public camera/stereo mod exists for this game; only a config-based FOV/HUD fix and stock cheat trainers (no camera hack) were found. Confirms greenfield: the live d3d9 capture remains the only path to the SHARED-vs-per-object-matrix answer. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
