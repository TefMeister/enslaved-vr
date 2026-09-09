# 2026-09-09 — the pause blocker is an ini hazard, and the self-healing proxy survives a Reset

Dev PC (`DESKTOP-V8GTSIR`), `/lm enslaved-vr`, three flat launches, fully autonomous
after the first launch. Deployed proxy unchanged throughout: `d3d9.dll` 78,336 B
(the 2026-09-04 self-healing build), `d3d9_proxy.ini` 2,165 B, both `OK` against
`deployed.sh` before and after.

## What is in here

| file | run | what it holds |
| --- | --- | --- |
| `run1-log.txt` | 1 | stock-state ini. Checkpoint restart (no Reset), then TWO resolution-change Resets with the re-arm firing. 11,215 lines. |
| `run2-log.txt` | 2 | the 2026-09-07 test ini restored verbatim. Escape dead. |
| `run3-log.txt` | 3 | same ini MINUS the invented `[MonkeyGame.MKInput]` section. Escape alive. |
| `02-…` → `19-…` | 1 | title → menu → gameplay → pause → checkpoint restart → options → two Resets → main menu |
| `22-…` → `26-…` | 2 | gameplay, Escape ×2 (nothing), F4 (nothing), W (character walks) |
| `27-…` → `31-…` | 3 | gameplay, Escape (pause menu opens), F4 (nothing), F2 (nothing) |

Screenshots are BitBlt captures of the client area, JPEG q72. Stereo ran in wiggle
`Mode=0` all session, so consecutive frames are different eyes — see the dossier's
image-comparison warning before scoring anything by pixel difference.

## The two results, in one line each

1. **The pause blocker was the ini, and specifically the section that does not exist
   in this build.** Run 2 reproduced 2026-09-07 exactly (Escape and F-keys inert,
   `W` walks). Run 3 changed one thing — deleted `[MonkeyGame.MKInput]` — and Escape
   opened the pause menu on the first press. `[verified-live 2026-09-09, n=1 A/B pair]`
2. **A device Reset reverts slot 94 and the self-healing build re-patches it in the
   same frame, and the stereo keeps working.** Two Resets, identical readings, and
   `state blocks 0` in both — so the revert happens at `Reset`, not via a recorded
   state block. `[verified-live 2026-09-09, n=2 resets]`
