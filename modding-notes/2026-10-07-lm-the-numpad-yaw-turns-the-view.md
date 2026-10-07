# 2026-10-07 (dev PC, `/lm`, one launch, driven by Claude): the numpad yaw turns the view

*One launch. Menus replayed by Menu-o-matiC; game closed through its own menus. Recorded with OBS
(game window only): `headyaw-test_2026-10-07_17-57-33.mp4`.*

## In plain words

The 2026-10-04 test worked on its first run. Pressing numpad 6 turned the picture 15 degrees each
time, it stayed put, and numpad 5 put it back exactly. The game's own camera did not fight it or
spin. That means we have a working place to turn the view every frame, which is what a headset needs.

## What was run

`[uobject] Probe=1`, `[headyaw] Enabled=1` (ini backed up as `d3d9_proxy.ini.bak-2026-10-07`).
Still camera in the Chapter checkpoint garden, Monkey standing still.

## What it showed `[verified-live 2026-10-07, n=1 launch]`

| Step | Log | Screen |
| --- | --- | --- |
| start | `installed at 0x008BEFE8 -> trampoline`; probe: `LIVE PLAYERCONTROLLER MKPlayerController_Monkey` at frame ~4500 | normal view |
| numpad 6 | offset 15, game yaw 6.5 -> ours 21.5, diff 15 | view turned right |
| numpad 6 ×2 more | offset 45, game yaw 6.5 -> ours 51.5, diff 45, steady for 200+ frames | turned further, held |
| numpad 5 | offset 0, 6.5 -> 6.5 | identical to the start frame |

That is the first row of the 2026-10-04 outcome table: **the lever works.** The "spins" row did not
happen: the game's yaw never moved while Monkey stood still.

## Extra check, not settled

With +45° held, Claude walked Monkey forward 1.2 s and back. The game's own camera swung
(6.5 -> 25.5 -> 101.5 -> 68.7 -> 39.0°) and our diff stayed exactly 45 on every line, so the offset
sits on top of a moving camera without piling up `[verified-live 2026-10-07, n=1]`. But because the
game turns its camera as Monkey walks, the screenshots cannot say whether walking followed the drawn
view or the game's view. **Not established.** An enemy began firing at Monkey during it; the check
was stopped there.

## Small faults seen

- `gameplay_to_main_menu` reported "lost" at the exit-warning checkpoint, yet the game reached the
  main menu and `main_menu_to_closed` then quit it cleanly. Probably the combat (moving picture
  behind the warning). Worth a retry before changing the route.
- `sed -i` on the ini turned its line endings from CRLF to LF (3713 -> 3703 bytes). The game read it
  fine.

## Next

Feed a head pose instead of the numpad (the OpenXR simulator on the dev PC can give one), and
pitch as well as yaw. Before that, the walking question can be settled with the reader's static
answer or a still test with a wall straight ahead.
