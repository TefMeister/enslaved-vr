# 2026-09-01 — Enslaved creates a plain D3D9 device, and that decides the submission design

**Date:** 2026-09-01, dev machine, `/pd` session. **The game was not launched, and nothing here has
been run.** Static reads of shipped files only.

---

## Why the question mattered

`/gr` filed an inbox drop pointing out that this project's §9 open risk — "the compositor submission
path from a D3D9 game needs a D3D9Ex/D3D11 texture-sharing bridge" — was already researched by
`far-cry-2-vr`, a different engine on the same Direct3D 9. The technique is documented Windows
interop: create the texture on the D3D11 side with `D3D11_RESOURCE_MISC_SHARED`, take its `HANDLE`
from `IDXGIResource::GetSharedHandle`, open it from D3D9Ex with
`IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)`. No CPU round-trip.

The drop closed with the one thing to check first, because it decides whether any of it applies:
**the interop path requires D3D9Ex, and plain D3D9 cannot open a shared handle.** The dossier did
not record which this game creates.

## The answer: plain D3D9

`[inferred-static 2026-09-01, n=3 independent checks]` — three checks that would fail in different
ways, so their agreement carries weight:

1. **Import table.** `Enslaved.exe` imports exactly four names from `d3d9.dll`: `Direct3DCreate9`
   and three `D3DPERF_*` markers. No `…Ex`, in either the normal or the delay-import directory.
   This reproduces `dev-archive/recon/enslaved_exe_imports_d3d9.txt`, dumped by an earlier session
   with a different tool — so the import read itself is at n=2.
2. **String scan.** `Direct3DCreate9Ex` does not appear anywhere in the 34 MB executable. That rules
   out reaching it by `GetProcAddress`, which an import-table read alone cannot exclude.
3. **IID scan.** The `IDirect3D9Ex`, `IDirect3DDevice9Ex` and `IDirect3DSwapChain9Ex` interface GUIDs
   occur **zero** times. That rules out a `QueryInterface` upgrade on a legacy-created device.

Checks 2 and 3 exist precisely because check 1 is the one everybody runs and is the weakest of the
three on its own.

## What follows

The sibling technique **does not apply to the game's device as it stands.** The route that remains is
to upgrade the device inside our own proxy, and it is cheap on paper: we already own `d3d9.dll`, and
its `.def` already exports `Direct3DCreate9Ex`. Because `IDirect3D9Ex` derives from `IDirect3D9`
(and `IDirect3DDevice9Ex` from `IDirect3DDevice9`), the proxy can create the Ex object itself and
hand it back through the legacy interface; the game is compiled against the base vtable and need not
know. `[reported]` — interface inheritance. Not built, not run.

## 🪤 The trap that decides whether that is a one-line change or a project

**`D3DPOOL_MANAGED` does not exist on a D3D9Ex device.** Any `CreateTexture` /
`CreateVertexBuffer` / `CreateIndexBuffer` requesting it fails. So the upgrade is viable only if
UE3's D3D9 RHI never asks for MANAGED on this build — **and that is unverified.** It is the first
thing to establish, because the two outcomes are a proxy tweak versus a resource-remapping exercise.

I could not settle it statically: pool arguments are values passed at runtime, not names in a table,
so there is nothing on disk to read. It needs one instrumented launch.

Second trap, carried over from the drop: **`D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` has no D3D9
equivalent** — there is no `IDirect3D9KeyedMutex`. The synchronisation primitive every tutorial
recommends is simply unavailable to a D3D9Ex producer. The established substitute is an
`IDirect3DQuery9` event query plus double/triple buffering. `[reported]`

And for whatever eventually submits: **OpenVR issue #1253** (open) — SteamVR keeps only the pose from
the *last* `Submit`, so per-eye `Submit_TextureWithPose` ghosts. Submit both eyes together. `[reported]`

## What is NOT established

- That the Ex upgrade works here. Nothing was built or run for it this session.
- That UE3 avoids `D3DPOOL_MANAGED`. Unknown, and load-bearing.
- Anything new about the stereo work at `c0`, which is unchanged and still awaiting its first launch.

## The cheap test, whenever this game is next up

The existing proxy already logs `CreateDevice`. Extending it to log the `D3DPOOL` of every resource
creation would answer the MANAGED question in one launch — **but note the proxy currently deployed in
`Binaries\Win32` has no such logging, and no `d3d9_proxy_log.txt` exists in the game folder**, so
this needs a rebuild before it can be run. Left deliberately unbuilt: the stereo wiggle test is the
higher-value use of the next Enslaved launch, and adding resource logging to the same build risks
disturbing a proxy that is about to be tested for something else.
