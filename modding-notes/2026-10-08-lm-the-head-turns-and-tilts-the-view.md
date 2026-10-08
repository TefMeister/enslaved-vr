# 2026-10-08 (dev PC, `/lm`, one launch, driven by Claude): the head turns and tilts the view

*One launch. Menus replayed by Menu-o-matiC both ways; closed through the game's menus. Recorded:
`headxr-sim-test_2026-10-08_11-33-46.mp4`. Evidence: `dev-archive/recon/2026-10-08-headxr-simulator/`.*

## In plain words

The OpenXR simulator now steers the game camera. Turning the simulated head turns the view; tilting
it tilts the view up or down; putting it back puts the view back. No picture goes to a headset yet.

## What it showed

Installed build unchanged from 2026-10-07 (`d3d9.dll` `df9b39504a5b`, `openxr_loader.dll`
`fb1e06de9653`); only `[headxr] Enabled=1` in the ini (backup `d3d9_proxy.ini.bak-2026-10-08`).

- The headset thread started beside the game, the session reached running, and poses and headset
  frames climbed together for the whole run, no failures `[verified-live 2026-10-08, n=1]`.
- Simulator `yaw_deg=+30` logged as head yaw **-30** and the view turned **left** (a0 -> a1). The
  simulator follows the OpenXR rule (+yaw = left); our maths converts it correctly. `yaw_deg=-30`
  turned it right (a4). Game yaw 6.5 -> 36.5 / -23.5, diff exactly 30 `[verified-live 2026-10-08, n=2 turns]`.
- Pitch +20: view tilted up (a2); pitch -15: tilted down (a4) `[verified-live 2026-10-08, n=2]`.
- The game's own chase-camera pitch is **-9.3** here, and ours **adds** to it (-9.3 + 20 = 10.7;
  -9.3 - 15 = -24.3), held steady across 14 status lines, no pile-up `[verified-live 2026-10-08, n=1]`.
- Head back to 0: game yaw and view back to the game's own `[verified-live 2026-10-08, n=1]`.
  Restore ran every written frame (`restored` = `wrote`, `skipped 0`).

## Small things

- The log prints "game pitch 0.0 -> after ours 0.0" while head pitch is 0: the read is skipped then
  (`pOff != 0 &&` in `headyaw.inc.h`), so that 0.0 is a placeholder, not a reading (reader, static).
  Log-only fix for later: always read pitch, keep the write gated.
- Writing the ini with `sed` turned its line endings to LF; the game read it fine.
- `gameplay_to_main_menu` passed the exit warning by itself this time (it failed on 2026-10-07).

## Not established

- Walking with a head turn held (restore on) is still the weaker 2026-10-07 try.
- Roll is ignored. Nothing reaches a real headset; the picture waits for the DirectX 10 work.
