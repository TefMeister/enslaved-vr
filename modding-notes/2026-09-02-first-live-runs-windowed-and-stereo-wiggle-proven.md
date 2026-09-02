# 2026-09-02 — first live runs: forced windowed, and the stereo wiggle is PROVEN

Six launches on the dev PC, flat screen, Steam launch each time. Evidence logs in
`dev-archive/recon/2026-09-02-first-live-runs/`. Proxy source in `staging/enslaved-vr/proxy-d3d9/`
(`8bd8209` window, `46b65bc` window-only, `986210a` layout fix).

## Headline
**The per-eye offset on `c0` works.** With `[stereo] Enabled=1 Mode=0 Separation=6.0` the game
runs and the picture alternates left/right every frame — the user's words: "it looks like AER,
very quick left-right teleport, not a big gap between images, the game runs though".
`[verified-live 2026-09-02, n=1]` We own the camera in Enslaved with no engine cooperation.

## What each run taught
1. **Run 1 (stock, fullscreen):** proxy loads and hooks; one `[reset]` at ~frame 240 after which
   the VS-constant histogram was empty for 7,300 frames. `[verified-live, n=1]` — cause unknown,
   `[hypothesis]` that a Reset stops SetVSConstF being observed. Run 2 had no reset and full data.
2. **Run 2:** `c0 x4 :28/frame`, `c4 x1`, `c5 x1`, `c6 x4 :116`, `c231 x4 :62` — the CTAB
   reflection's register map, live. `[verified-live, n=1]`
3. **Runs 3–4 (windowed):** this build has NO windowed mode — `Windowed` occurs 0× in the exe in
   any encoding (positive controls: `ResX`/`ResY` 7, `FullScreen` 91/9, `Exec` 3348), the menu
   has only gamma + resolution, and it rewrites `MonkeyEngine.ini` on exit while ignoring
   `[SystemSettings] Fullscreen=False` and `ResX/ResY`. So the proxy forces `Windowed=TRUE` in
   `CreateDevice`/`Reset` and restyles the window. Shrinking the BACKBUFFER clips (UE3 sizes
   render targets from its own resolution); shrinking only the WINDOW works, D3D stretches on
   Present. The game never fights the restyle (`present#1/60/300: already ok`).
   `[verified-live, n=2]`
4. **Run 5 (stereo, wrong layout):** black + flicker. The `c231` LocalToWorld dump in the same
   log had its translation in the **4th register** (`[-444, -550, -11229, 1]`), so registers are
   COLUMNS (D3D9 HLSL default `column_major` with `mul(M,v)`) — the 2026-09-01 "registers are
   rows, translation at floats 3/7/11" reading is **[disproved 2026-09-02]**; it was adding the
   eye shift into the perspective row.
5. **Run 6 (stereo, fixed):** direction = floats 0/4/8, update into floats 12..15. Works. The
   captured `c0` in this run was the UI ortho (`2/1920`, `-2/1080`, translation `(-1,1,-1)` in the
   4th register) — the layout proof a third time.

## Open, in gate order
- `[PD]` Ortho `c0` uploads (`float[11]==0 && float[15]==1`) pass the sanity check and get offset
  → the HUD probably wobbles. Skip them. Also classify the `rejected` count, which went from a
  steady 840/120 frames to a scene-dependent 680–4,259 after the re-index: those are `c0` uploads
  whose row 0 is zero — global-shader params sharing `c0`, not VPs `[inferred-static]`.
- `[FLAT]` `Separation` scale: 6.0 reads as a small hop. Raise 10× and check it scales linearly.
- `[FLAT]` Reflections/decals/water staying still while the world rocks = the 310 pixel-stage
  shaders. The user can answer this on any stereo run.
- `[FLAT]` `D3DPOOL_MANAGED` instrumentation, separate launch (unchanged).
- Run 1's post-Reset silence is unexplained; forced windowed makes resets rare, which hides
  rather than answers it.
