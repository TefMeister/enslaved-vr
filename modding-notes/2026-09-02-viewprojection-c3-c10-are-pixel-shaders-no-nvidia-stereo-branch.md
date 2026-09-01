# The `c3`/`c10` view-projection is in PIXEL shaders, and this build has no NVIDIA stereo branch

*2026-09-02, home PC, `/pd` (static lane). **The game was not launched; nothing here has been run.***

A `/gr` inbox drop asked two things of this project: does Enslaved's shader cache carry NVIDIA's
3D Vision branch of UE3 (`NvStereoEnabled` / `NvStereoFixTexture`, as Alice: Madness Returns does),
and is the dossier's `c3` view-projection acceptance stage-qualified? Both were answerable from disk.

## 1. No NVIDIA stereo branch here — a clean negative `[inferred-static 2026-09-02, n=8 files]`

Case-insensitive byte search for `nvstereo` over everything that could hold it:

| File | Hits |
|---|---|
| `RefShaderCache-PC-D3D-SM2.upk` (36 MB), `-SM3.upk` (71 MB), `-SM4.upk` (281 MB) | 0, 0, 0 |
| `GlobalShaderCache-PC-D3D-SM2/SM3/SM4.bin` | 0, 0, 0 |
| `Binaries\Win32\Enslaved.exe` (also `NvAPI_Stereo`, `nvapi`) | 0 |
| `Engine\Shaders\*.usf` (the shipped HLSL sources) | 0 files |

`AllowNvidiaStereo3d` occurs in **no** file under the game folder, and the only `NVCHANGE_BEGIN/END`
markers in the shipped sources are in `MeshInstancedVertexFactory.usf`, tagged *"Jiayuan - Color
Over Life"* — a particle-colour change. So an NVIDIA engineer did touch this UE3 branch, but the
stereo branch is not in it. Nothing for a proxy to drive; the per-eye work stays ours.

The byte grep is stronger than a name grep: it covers the SM4 cache too, which `d3d9-ctab.py`
cannot parse (D3D10 shaders carry `RDEF`, not `CTAB`), and it would have caught the sampler name as
well as the constant. A negative this cheap is worth having in writing so nobody re-derives it.

## 2. The 310 "other-register" view-projections are all PIXEL shaders — the 9% claim was mis-staged

The dossier (§4, 2026-09-01) read the cooked SM3 cache and reported `ViewProjectionMatrix` at
`c0 x4 (3325)`, `c3 x4 (288)`, `c10 x4 (22)` — "about 9% of shader variants read it from `c3` or
`c10`" — and the proxy was widened to accept those registers. That reading never recorded the shader
**stage**. Re-walking every `CTAB` block with the version token that sits eight bytes before it
(`0xFFFE` = vertex, `0xFFFF` = pixel): `[inferred-static 2026-09-02, n=34,046 tables]`

| Constant | Vertex shaders | Pixel shaders |
|---|---|---|
| `ViewProjectionMatrix` | **`c0` x4 — 3325 (all of them)** | `c3` x4 — 288 · `c10` x4 — 22 |
| `CameraPosition` | `c4` — 2824 | — |
| `PreViewTranslation` | `c5` — 1089 | — |
| `LocalToWorld` | `c6` x4 — 2308 · `c231` x4 — 469 · `c10` x4 — 264 | — |
| `LocalToView` | `c14` x4 — 132 · `c10` x4 — 103 | — |
| `ScreenPositionScaleBias` | — | `c1` — 11644 |
| `MinZ_MaxZRatio` | — | `c2` — 12849 |

(The SM2 cache agrees: VS `c0` 1977, PS `c3` 152, nothing else.) Exactly the layout the inbox
predicted from Alice: `c1`/`c2`/`c3` are UE3's reserved **pixel-shader** view registers.

**What this changes.**

- **On the vertex side — the only side `SetVertexShaderConstantF` sees — the view-projection is at
  `c0` and nowhere else.** The proxy's `c3`/`c10` acceptance is unreachable for the matrix it was
  written to catch. It cannot misfire (the bit-identical-to-`c0` guard rejects the per-object
  `LocalToWorld`/`LocalToView` that really do live at vertex `c10`), so it stays as a guarded
  fallback, with its comment corrected. No behaviour change; `[compile-verified 2026-09-02]`.
- **What is genuinely still open is the pixel side.** 310 pixel shaders read the view-projection
  (at ps `c3` / ps `c10`) and the proxy does not hook `SetPixelShaderConstantF`, so whatever they
  project — screen-space effects, reflections, decals; *which* is not known from the table — will
  use the un-offset matrix in a stereo build while geometry is per-eye correct. Whether that is
  visible is a live question; the fix, if needed, is the same hook with the same guard on the pixel
  stage. `[hypothesis]` until seen.
- **The stage now has to travel with the register** in every table and log line of this project.
  A rule that says "`c3` x4 that equals `c0`" is one character from a rule that would, on a build
  that *did* carry the NVIDIA branch, treat a stereo parameter as a view-projection.

## 3. Built here, deployed here `[compile-verified 2026-09-02]`

The home PC had **no proxy at all** in `Binaries\Win32` — the 2026-09-01 deployment was on the dev
PC. Rebuilt from `staging/enslaved-vr/proxy-d3d9/` with llvm-mingw (`build.ps1`, i686): PE32 i386,
70,144 bytes, **9 undecorated exports** including `Direct3DCreate9` and `Direct3DCreate9Ex`. Copied
`d3d9.dll` + `d3d9_proxy.ini` next to `Enslaved.exe` (which imports `d3d9.dll` by name). Nothing was
overwritten, so there is nothing to back up; **deleting those two files restores stock.** Stereo is
`Enabled=0` by default, so the first launch is a pure regression check.

## 4. Next launch on this machine, in order

1. Launch normally, play a few seconds, quit. `Binaries\Win32\d3d9_proxy_log.txt` must exist and show
   `CreateDevice` + frame summaries. **No log = the proxy did not load; the rest is moot.**
2. Set `[stereo] Enabled=1`, `Mode=0`. **The whole image should rock side to side**, scaling with
   `Separation`. Rock = we own the camera at `c0`. Nothing = raise `Separation` 10×; tearing = lower it.
3. Watch the log for `rejected N as not-a-viewproj` climbing steadily — that would mean the `c0`
   derivation is wrong, not a knob.
4. While it rocks, look at water, reflections and decals: anything that stays put while the world
   rocks is §2's pixel-side view-projection showing itself, and says whether the pixel hook is needed.

## What is NOT established

- Anything about the running game — proxy load, rock, pixel-side visibility.
- Which effects the 310 pixel shaders belong to (CTAB gives registers, not shader names).

🤖 Static only. Evidence: `dev-archive/recon/2026-09-02-ctab-stage-and-nvstereo-check/`.
