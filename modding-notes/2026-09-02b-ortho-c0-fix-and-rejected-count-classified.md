# 2026-09-02 (`/pd`, home PC, NO LAUNCH) — HUD-hop fix built + deployed, `rejected` count explains itself, ctab tool's stage-blindness fixed

Picked up the two `[PD]` items the dev-PC live session left on the board after proving the stereo
wiggle (runs 6–7, `status/enslaved-vr.md`). **The game was not launched, and nothing here has been
run in-game.**

## 1. Orthographic (UI/HUD) `c0` uploads are now skipped by the stereo offset

Run 6's watched `c0` was the UI ortho projection: row 0 `[0.0010 0 0 0]`, row 1 `[0 -0.0019 0 0]`,
row 2 `[0 0 1 0]`, 4th register (translation) `[-1.0005 1.0009 -1 1]`. `float[11]=0`, `float[15]=1`
exactly — the ortho shape the board named. It passes `LooksLikeViewProj` (row 0 is non-zero, just
tiny) and was getting the same per-eye offset as the world VP, which is why the HUD hopped (user
confirmed live, run 6).

Added `IsOrthographic(m)` (`fabsf(m[11]) < 1e-6f && fabsf(m[15]-1.0f) < 1e-4f`) and skip the offset
for any `c0` upload it flags — falls through and forwards `pData` unmodified instead of the shifted
scratch copy. `[compile-verified 2026-09-02]`, **not yet run**: the fix cannot be confirmed live
until the next stereo launch shows the HUD holding still while the world still rocks.

## 2. The `rejected` counter is now three counters, and the mystery is gone

The board flagged that `rejected` went from a steady 840/120 frames (run 5, wrong layout) to a
scene-dependent 680–4,259 (run 6, fixed layout) and asked for it to be classified. Reading the
actual dispatch logic (`dllmain.cpp`), the single `g_stereoRejected` counter was conflating two
unrelated things:

- **`c0` uploads whose row 0 is zero** — global-shader-params draws that happen to share register
  `c0` with the real view-projection. Expected, scene-dependent, not a fault.
- **`c3`/`c10` uploads that didn't bit-match this frame's `c0` value** — ordinary per-object
  `LocalToView`/`LocalToWorld` matrices. The comment in the code already said these are expected
  (`c10` carries per-object matrices in vertex shaders); they were just never counted separately
  from real rejections.

Split into `g_stereoRejC0Zero`, `g_stereoRejC0Other` (should stay 0 — the one number that would mean
"the premise is wrong"), and `g_stereoRejAlias`. The summary log line now prints all three plus
`ortho-skipped`, so the next run's log makes the scene-dependent swing self-explanatory instead of
needing this write-up to interpret it.

`[compile-verified 2026-09-02]` (`d3d9.dll`, 73,728 bytes, `list-exports.ps1` confirms all 9 exports
intact — same class of check that caught the September 1 broken build recipe). **Deployed** to this
machine's `Binaries\Win32\` with the prior files backed up as `*.bak-2026-09-02`; `Enabled=0` in the
deployed ini, matching staging's default, so nothing changes on a stock launch.

## 3. Toolkit fix: `d3d9-ctab.py` was stage-blind in exactly the way that caused the c3/c10 mis-staging

The board's other `[PD]` item. Read the tool (`flat-to-vr-RE-toolkit/tools/d3d9-ctab.py`) rather than
guessing where the gap was: `find`/`list` mode's `print_table` already prints the shader stage once,
in the table header — but `summary` mode's "most common constants" breakdown keys its per-register
tally by `(regidx, regcount)` only, **dropping the stage the header carries everywhere else**. That
is exactly how `ViewProjectionMatrix` at `vs c0` and `ps c3`/`ps c10` got read as three registers for
one shared matrix instead of one vertex register plus two unrelated pixel ones.

Fixed both:
- `find`/`list`: added a stage column to every constant **row**, not just the table header, so a row
  copied or grepped out of context still carries its stage.
- `summary`: the per-constant register tally is now keyed `(stage, regidx, regcount)`.

**Verified numerically**, not just compiled — re-ran the fixed tool against the same
`RefShaderCache-PC-D3D-SM3.upk` used for the original (now-corrected) dossier claim:

```
ViewProjectionMatrix   in 3635   vs_3_0 c0 x4 (3325), ps_3_0 c3 x4 (288)
```

Reproduces the already-verified 3325/288/22 split exactly (the third spot, `ps c10 x4 (22)`, is
outside `most_common(2)`'s cap of 2 — unrelated to this fix, matches the original tool's behaviour).
`[verified-numerically 2026-09-02]`

## Inbox drained (2 files, `engine-research/inbox/`)

Both from `/gr`, 2026-09-02, folded into `ENGINE-DOSSIER.md` §9 and new §10a:
- **A public 3D-Vision fix for this exact binary exists** (superseding the 2026-08-24 "no entry
  exists" claim) — motion blur must be off before judging stereo (it reprojects using the
  pixel-stage VP, which this proxy doesn't touch), independently corroborates the 310-shader/HUD
  finding, and separation ≈6.0–6.5 is corroborated from UE3's own unit-scale convention, not just our
  by-eye fit.
- **The D3D10 path sidesteps the `D3DPOOL_MANAGED` trap** entirely (ordinary DXGI shared textures, no
  Ex upgrade needed) at the cost of an undesigned constant-buffer injection point. Named as a second
  route in §9, decided after the `D3DPOOL_MANAGED` instrumented launch either way.

## What is NOT established

- The HUD fix is compile-verified only. It could not be run — no headset/monitor session this pass.
  The specific diagnostic that would show it's wrong rather than just untested: HUD elements still
  visibly hop on the next stereo launch despite `ortho-skipped` incrementing in the log (would mean
  another matrix shape carries HUD projections, or the epsilon on `IsOrthographic` is too tight/loose
  for some other UI draw).
- The `rejected` split is a classification of already-observed, already-benign traffic, not new
  behaviour — it changes what the log says, not what the proxy does to any upload.
- `d3d9-ctab.py`'s fix was checked against Enslaved's own shader cache only; not re-run against any
  other project's cache in this pass.
