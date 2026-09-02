# 2026-09-02 — first live runs of the d3d9 proxy (dev PC, flat, stereo OFF)

Both runs: Steam launch, `[stereo] Enabled=0`, load a level, play briefly, quit.

## Run 1 (log overwritten by run 2 — facts transcribed from it)
- Proxy loaded, `CreateDevice` hooked, device vtable patched (Present/Reset/SetVSConstF). `[verified-live 2026-09-02, n=1]`
- Device: 1920x1080, `windowed=0`. 7,560 Presents logged.
- **One `[reset]` at ~frame 240, and the VS-constant histogram was EMPTY on every sampled frame after it** (only frame 240 showed `c0 x128 : 1`, `c128 x128 : 1`). Present kept logging, so the vtable was not restored — but SetVSConstF stopped being observed. `[verified-live 2026-09-02, n=1]`

## Run 2 (`run2-fullscreen-1920x1080-no-reset.log`)
- Same launch; **zero `[reset]`** this time, and **2,357 histogram rows**.
- Representative frame: `c0 x4 :28`, `c4 x1 :26`, `c5 x1 :26`, `c6 x4 :116`, `c10 x4 :18`, `c14 x3`, `c231 x4 :62`.
- **`c0` is uploaded as a 4-vec4 matrix ~28x/frame with `c4`/`c5` beside it** — exactly where the 34,046-table CTAB reflection put `ViewProjectionMatrix` / `CameraPosition` / `PreViewTranslation`. `[verified-live 2026-09-02, n=1]`

## Open
- Why run 1 reset and run 2 did not is unknown; the histogram going silent after a Reset is `[hypothesis]` pending a run that resets again. Forced-windowed (next build) may make resets rare, which would hide rather than answer it.
- The proxy's `<== SHARED matrix (view-projection candidate)` tag on `c10`/`c231` is stale: reflection says `c231` = `LocalToWorld` and the `c10` VP entries are pixel-stage.
