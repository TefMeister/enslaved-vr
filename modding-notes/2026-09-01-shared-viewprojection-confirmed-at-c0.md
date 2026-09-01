# 2026-09-01 — There IS a shared view-projection, and it is at c0. The per-object-WVP worry is dead.

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of shipped files only; nothing modified.

**Result: the project's stated pivotal open question is answered, and the working hypothesis was
wrong.** No capture session is needed to settle it.

---

## The question

The board recorded it as: *"THE PIVOTAL OPEN QUESTION — shared VP vs per-object WVP. The gameplay
VS-constant histogram shows 4×4 matrices at `c0`, `c6`, `c10` and `c231` (+`c235` = a 4×3
LocalToWorld), but every 4×4 upload is per-object; none appears once per frame — so the camera is
probably folded into a per-draw World×ViewProjection."* The proxy was rebuilt to detect a shared
matrix at runtime and has been waiting for a launch ever since.

## The answer, from the game's own shipped shader source

**Enslaved ships its UE3 HLSL sources** in `Engine/Shaders/*.usf` — not just cooked bytecode. Those
are the shaders this build was cooked from, and `Common.usf` reserves the engine registers
explicitly, with a comment stating they must match `EVertexShaderRegister` in `RHI.h`:

| Register | Contents |
|---|---|
| **`c0`–`c3`** | **`ViewProjectionMatrix`** — "View-projection matrix, transforming from World space to Projection space" |
| **`c4`** | **`CameraPosition` / `ViewOrigin`** — "World space position of the camera" |
| **`c5`** | **`PreViewTranslation`** — "Offset applied to LocalToWorld to reduce precision problems far from the world space origin" |

`LocalToWorld` and `PreviousLocalToWorld` are declared as ordinary `float4x4`s in the **vertex
factories** (`LocalVertexFactory.usf`, `GpuSkinVertexFactory.usf`), i.e. compiler-allocated, and
`GpuSkinVertexFactory.usf` also carries a `float4x3 WorldToLocal` and a `float4x3 BoneMatrices[]`.

**So `c0` is a shared, engine-reserved view-projection — by definition, not by inference — and the
per-object matrices the histogram saw at `c6`, `c10`, `c231` (and the 4×3 at `c235`) are the vertex
factories' `LocalToWorld` / `PreviousLocalToWorld` / `WorldToLocal` / bone matrices.**

`[inferred-static 2026-09-01, n=1 — from `Engine/Shaders/Common.usf`, `LocalVertexFactory.usf` and
`GpuSkinVertexFactory.usf` as shipped]`. Not observed live.

## Why the runtime histogram looked like it disproved this

Worth recording, because the reasoning error is a reusable one: **the histogram measured how often a
register was WRITTEN, not what was written to it.** UE3's D3D9 RHI re-applies the reserved view
registers around bound-shader-state changes, so `c0` is uploaded many times per frame — which looks
exactly like a per-object register if you only count uploads. It is the same value every time.

The proxy upgrade that flags registers *identical across all draws* was the right instrument and
would have caught this; it simply never ran. The static route got there first and for free.

**This is the second time in this portfolio that a claim came from a measurement whose precondition
was not checked** (see the Psychonauts 2026-08-28 method lessons). Upload frequency was never
evidence about shared-ness.

## What this unlocks

* **A clean single injection point.** `SetVertexShaderConstantF(StartRegister == 0, Vector4fCount == 4)`
  is the view-projection. Stereo is an eye offset applied there — the same shape as Far Cry 2's
  working override, and far simpler than decomposing per-draw WVPs.
* **The camera position is handed to us at `c4`.** No solving it out of the matrix (which Far Cry 2
  needed and which is where a subtle scale bug hid there). `c4` is the world-space view origin,
  directly.
* **⚠️ `PreViewTranslation` at `c5` is the trap to design around.** UE3 pre-translates the world so
  the camera sits near the origin for float precision: vertices reach the vertex shader in
  *translated* world space, and `ViewProjectionMatrix` is built to match. An eye offset written into
  `c0` must therefore be consistent with `c5`, and **anything that reasons about absolute world
  positions must add `PreViewTranslation` back.** A stereo offset that ignores it will look correct
  near the origin and drift as the player moves away from it — a bug that reads as "stereo breaks in
  some levels".

## Next

**No launch needed to start.** Rework the proxy's stereo path against `c0` directly rather than
waiting on the SHARED-matrix detector. Keep the detector: on the first real run it becomes a cheap
*confirmation* that `c0` holds one value per frame, which converts this note from
`[inferred-static]` to verified.

Remaining runtime questions, unchanged: whether the Tilde console works now the game is windowed,
and whether cutscenes use a separate camera path.

🤖 Static analysis of shipped shader sources only. The game was not launched, and no game file was
copied into this repository — only the register mapping, which is interface metadata.
