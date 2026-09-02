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

## Runs 3-4 — forced windowed (proxy `[window]`)
- This build has NO windowed mode: `Windowed` occurs 0 times in the exe in any encoding (controls: `ResX`/`ResY` utf16=7, `FullScreen` 91/9, `Exec` 3348), the menu offers only gamma + resolution, and the game rewrites `MonkeyEngine.ini` on exit while ignoring `[SystemSettings] Fullscreen=False` and `ResX/ResY` (asked 1920x1080 with ResX=1280 in the file). `[verified-live 2026-09-02, n=2]`
- Run 3: forcing `Windowed=TRUE` + shrinking the backbuffer to 1280x720 gave a correct captioned window showing only the TOP-LEFT quarter — UE3 sizes render targets from its own resolution. Run 4: backbuffer left at 1920x1080, only the window client shrunk → fits, D3D stretches on Present. Window restyle never fought back (`present#1/60/300: already ok`). `[verified-live 2026-09-02, n=1 each]`

## Run 5 — first stereo run (`run5-stereo-on-wrong-row-black-flicker.log`)
- Hook applied: `offset ~4100 uploads / 120 frames`, `rejected 840` steady. Picture: black with flickering fragments from the main menu on. `[verified-live 2026-09-02, n=1]`
- **Cause, from the same log:** the `c231` LocalToWorld dump has its translation in the **4th register** (`[-444.18, -550.06, -11229.03, 1.0]`, first three registers a 75x rotation-scale). So registers are COLUMNS (D3D9 HLSL default `column_major` with `mul(M,v)`) and the 2026-09-01 "registers are rows, translation at floats 3/7/11" reading is **[disproved 2026-09-02]**. The offset was being added into the perspective (w) row. Fix: direction = floats 0/4/8, update floats 12..15 (staging `986210a`). Identical under the rows + `mul(v,M)` reading, so it is right under either consistent layout.

## Run 6 — stereo with the corrected layout, `Separation=6.0` (log overwritten by run 7 — transcribed)
- **Works.** User: "looks like AER, very quick left-right teleport, not a big gap between images, the game runs". `[verified-live 2026-09-02, n=1]`
- `offset 2,280–2,731 / 120 frames`; `rejected` scene-dependent 680–4,259 (was a steady 840 before the re-index — those are `c0` uploads whose row 0 is zero, i.e. not VPs, `[inferred-static]`).
- Watched `c0` was the UI ortho: `[0.0010 0 0 0] [0 -0.0019 0 0] [0 0 1 0] [-1.0005 1.0009 -1 1]` — translation in the 4th register, a third layout proof. It passes the sanity check → **the HUD hops too** (user confirmed).
- Far objects barely move, near ones do: depth-dependent parallax = a real world-space eye translation, not an image shift. `[verified-live, n=1]`
- The window's caption was gone by ~frame 3600 although checks 1/60/300 passed.

## Run 7 — `Separation=60.0` (`run7-stereo-sep60-two-monkeys.log`)
- Hop scales up: "I can basically see 2 monkeys with a little gap in between" — roughly one body-width at 60 units. With Monkey's torso ~50–60 cm that puts the world at **~1 unit ≈ 1 cm (UE3 convention)**, so a real IPD is `Separation ≈ 6.5`. `[inferred 2026-09-02, n=1, by eye]`
- Window re-check (now every 300 frames) caught the game restyling its own window to `WS_POPUP` (`0x94080000`, client 1286x749) at **present#1800 and #6600** and restored it both times. `[verified-live 2026-09-02, n=2]` So the game reapplies its fullscreen window style periodically (level/checkpoint loads, most likely) — the periodic re-check is required, not a nicety.
- 6,600 frames, 0 resets.
