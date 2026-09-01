# 2026-09-01 (b) — Stereo built at `c0`; and the build recipe could not produce a loadable proxy

**Date:** 2026-09-01, dev machine, `/pd` pass. **The game was never launched.** Built, deployed,
**never run.** Stereo defaults to **OFF**, so with the shipped config the rendering behaviour is
unchanged.

---

## 1. Stereo is implemented, on evidence rather than convention

The morning's note established that `c0`–`c3` is a shared, engine-reserved `ViewProjectionMatrix`.
This wires the per-eye offset onto it.

**Both the register and the matrix layout come from the game's own shipped sources**, which is what
makes this cheap and safe to write without a launch:

* `Common.usf` reserves `VSR_ViewProjMatrix = c0`, `VSR_ViewOrigin = c4`,
  `VSR_PreViewTranslation = c5`, noting they must match `EVertexShaderRegister` in `RHI.h`.
* On PC (the `#else` branch of the `PS3` guard) `Common.usf` defines
  **`MulMatrix(Mtx, Vect) = mul(Mtx, Vect)`** — column vectors — and `BasePassVertexShader.usf` /
  `DepthOnlyVertexShader.usf` both do `MulMatrix(ViewProjectionMatrix, WorldPosition)`.

So the 16 uploaded floats are the matrix's **rows**, and the translation is **column 3**. Moving the
eye by `t` in world space is therefore

```
M' = M * T(t)      ->      m[r*4+3] += m[r*4+0]*tx + m[r*4+1]*ty + m[r*4+2]*tz
```

with `t = -(eye · sep/2) · normalize(row0.xyz)` — row 0's xyz being the world direction that maps to
view +X. **No P/V split needed**, the same shape already working in Far Cry 2.

### Refinement to yesterday's `PreViewTranslation` warning

I wrote that an eye offset "must be consistent with `c5`". **That was overstated.** UE3
pre-translates the world so the camera sits near the origin, but a relative eye offset is a
*translation*, and translations commute — the same `t` is correct in translated world space.
`c5` matters when reasoning about **absolute** positions (comparing `c4` against the matrix, say),
not for applying an offset. The trap is real; it just is not in this code path.

### Controls — `[stereo]` in `d3d9_proxy.ini`

| Key | Meaning |
|---|---|
| `Enabled` | `0` (default) / `1` |
| `Mode` | `0` = wiggle (alternate eyes per frame), `1` = left, `2` = right |
| `Separation` | world units, default `6.0` — **a guess** |

**`Separation` is not measured.** Enslaved's world-unit scale is recorded nowhere in this project.
UE3 conventionally runs ~1 unit per centimetre, which would put a real IPD near 6.5, hence the
default — but if the wiggle is invisible, raise it tenfold; if the world tears apart, lower it.

### The diagnostic that says the premise is wrong, not the setting

The periodic summary logs `rejected N as not-a-viewproj`. A **steady** non-zero count means `c0` is
carrying something other than a view-projection in this build, and §1's whole premise needs
revisiting — it is not a tuning problem. Uploads at `c0` that fail a finiteness/direction sanity
check are passed through untouched rather than corrupted.

## 2. ⚠️ The committed build recipe could not produce a loadable proxy

Found while trying to compile. **Both defects are pre-existing** — `build.ps1` is untouched since
the subtree import.

1. **`build.ps1` did not parse at all.** `-Wl,--kill-at` is a PowerShell parse error unless quoted
   (`Missing argument in parameter list`), and `-municode:$false` passed a literal `False` to the
   compiler. Fixed by quoting the linker flag and dropping the meaningless one.
2. **Once it ran, it produced a DLL with no export directory whatsoever.** The source contains **no
   `__declspec(dllexport)`**, and the script **never passed `d3d9.def`** — which sits right beside it
   listing exactly the nine exports needed. A d3d9 proxy that exports nothing cannot be loaded by the
   game at all.

**Careful about what this does and does not mean.** The DLL deployed on 2026-08-21 *does* have its 9
exports, so the working artifact is real and predates the script's current state — the proxy was
never broken, the **recipe** was. Anyone rebuilding from the repo would have produced a silent dud
and had to rediscover why.

Verified after fixing: **9 undecorated exports**, `Direct3DCreate9` and `Direct3DCreate9Ex` among
them.

Also corrected: the file header claimed *"This is instrumentation only. It changes no rendering
behaviour."* That is no longer true when `[stereo] Enabled=1`, and the header now says so. A stale
doctrine comment is how a fail-safe reputation gets quietly lost.

## 3. Status and next

`[compile-verified 2026-09-01]` for the build and the export table.
`[inferred-static 2026-09-01]` for the register and layout — from the shipped `.usf` sources.
`[untested]` for everything about the running game.

Deployed to `Binaries\Win32\` with the previous `d3d9.dll` and `d3d9_proxy.ini` backed up beside
them, dated.

### Next launch, in order — no rebuild needed

1. Play a few seconds with the shipped config (stereo **off**) and confirm the log still looks
   normal. This is the regression check.
2. Set `[stereo] Enabled=1`, `Mode=0`. **The whole image should rock side to side**, and the amount
   should scale with `Separation`. If it does, we own the camera and stereo is a solved problem here.
3. If the rock is invisible, raise `Separation` 10×; if geometry tears, lower it.
4. Check the log for `rejected N as not-a-viewproj` — a steady count means §1 is wrong.

Still open and unaffected: whether the Tilde console works now the game is windowed, and whether
cutscenes use a separate camera path.

🤖 Built and deployed only. The game was not launched, and the only game-folder files touched are the
mod's own DLL and INI, both backed up first.
