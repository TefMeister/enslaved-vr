# 2026-10-07 later (dev PC, `/lm`, one launch, driven by Claude): the restore build runs cleanly

*One launch. Menus replayed by Menu-o-matiC; closed through the game's menus. Recorded:
`headyaw-restore_2026-10-07_18-40-04.mp4`.*

## In plain words

The reader found that walking reads the turned view, so a head turn would steer Monkey. Its fix
hands the game its own direction back after each frame is drawn. That fix is now installed and on.
The view still turns, the fix runs every frame without a miss, and the walking looks like it follows
the game's direction, not ours. The walking part is one messy try (turrets were firing), so it is
likely, not proven.

## Installed

`d3d9.dll` `0b00186109c5` (104,448 B; the reader's draft, rebuilt here to the identical hash),
ini adds `[headyaw] Restore=1`. Previous files kept as `*.bak-2026-10-07` / `*.bak-2026-10-07b`.

## What it showed

- Both hooks installed: `restore installed at 0x008BDE30 (UWorld::Tick entry)` `[verified-live 2026-10-07, n=1]`.
- With +45° held: `restored` rose with `wrote` one for one (540 written, 540 restored), `skipped 0`.
  The view still turned 45° (diff 45 on every line) `[verified-live 2026-10-07, n=1]`.
- **Control walk** (no offset, W 2 s): the game's own yaw swung 6.5 → 66.5 → 83.3 as Monkey walked.
  So the big swing seen in the first run happens without us; it is the chase camera, not feedback.
- **Offset walk** (+45°, restore on, W 2 s): game yaw stayed 83.3 → 82.7 → 84.1 while walking forward.
  On screen the scene slid sideways as Monkey moved, which fits walking along the game's direction
  rather than straight into the turned view `[hypothesis, n=1]`. Turret fire and the chase camera make
  it a weak test.

## Small faults

- `gameplay_to_main_menu` lost again at the exit warning: Monkey had died and respawned, so the
  background behind the warning differed from the recorded checkpoint. Enter pressed by hand, then the
  quit route worked. The warning checkpoint's region includes too much background; worth re-marking
  on just the OK/BACK buttons.

## Next

Feed a pose source (OpenXR simulator) into yaw and pitch, with restore on. A cleaner walking check
(quiet spot, facing a wall) when convenient.
