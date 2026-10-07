# 2026-10-07 evening (dev PC, `/pd`, no launch): head yaw and pitch from OpenXR, built and installed off

**The game was not launched, and nothing here has been run inside it.**

## In plain words

The view-turning hook proven live today now has a second source: where a headset (or the OpenXR
simulator on the dev PC) says the head is pointing. Turning the head turns the view; tilting it
tilts the view up and down. No picture goes to the headset yet; that waits for the DirectX 10
output work. It is installed and switched off.

## What was built (`staging/enslaved-vr/proxy-d3d9/`)

- `headxr.inc.h`: a headset thread cut down from Hard Reset's `hxr.c`, which ran in the OpenXR
  simulator on 2026-10-07. Own D3D11 device (OpenXR needs one to open a session), empty headset frames
  (no layers), the head located (VIEW in LOCAL) each frame and published as two ints. Started from the
  first `Present`, never from `DllMain`. Every OpenXR and D3D11 function is loaded at run time, so the
  DLL imports nothing new.
- `headxr_math.inc.h`: quaternion to UE3 yaw (+ = right) and pitch (+ = up), and the pitch sum clamped
  at +/-89 degrees. `headxr_test.cpp` checks the shipped header against head turns built independently
  from axis-angle: **14 of 14 pass** `[verified-numerically 2026-10-07, n=14]`.
- `headyaw.inc.h`: with `[headxr] Enabled=1` the hook adds the head's yaw (relative to "straight ahead",
  taken from the first pose and re-taken on numpad 5) to the numpad offset, and writes pitch at
  `Camera+0x370` (`CameraCache.POV.Rotation.Pitch`, the slot the 2026-10-01 logger read live).
  The hook stays integer-only. A `[headxr]` log line shows stage, poses, head yaw/pitch and game pitch
  before and after ours, so a run proves its own effect.
- `headyaw_restore.inc.h`: puts pitch back too, by the same rule as yaw (only if the cache still holds
  exactly what we wrote).
- Build: `-Wall -Wextra` 0 warnings; the UObject self-test still passes; imports unchanged
  (kernel32, user32, CRT) `[compile-verified 2026-10-07]`.

## Installed on the dev PC

`d3d9.dll` `df9b39504a5b` (112,640 B), `openxr_loader.dll` `fb1e06de9653` (the same 32-bit loader Hard
Reset uses), `d3d9_proxy.ini` `b66cee2d4629` with a new `[headxr]` section, `Enabled=0`,
`RuntimeJson=` the simulator's 32-bit json. Previous files kept as `*.bak-2026-10-07c`.

## Not established

- Nothing ran. Whether the simulator's session starts beside this game, and whether its window steals
  focus from the game during automation, are unknown.
- Pitch on top of the game's own pitch: the game may clamp or fight it later in the tick. The hook
  writes after the camera loop, which worked for yaw, so the same is expected `[hypothesis]`.
- Roll is ignored.

## The one-launch test (FLAT, simulator, no headset)

Set `[headxr] Enabled=1` (with `[headyaw] Enabled=1`, `Restore=1`, `[uobject] Probe=1`), reach gameplay,
stand still. Turn the simulator's head (its MCP `set_head_pose`): yaw 30 right, then pitch 20 up.

| Log / screen | Meaning |
| --- | --- |
| `[headxr] session running`, poses rising, view turns 30 right and tilts 20 up | it works; next is the picture |
| `OFF: no 32-bit ... runtime` / `xrCreateSession failed` | runtime side, not the hook: check the json path and that the simulator is 32-bit |
| poses rise but `head yaw` stays 0 while the simulator turns | the simulator pose is not reaching LOCAL/VIEW the way assumed |
| yaw turns the wrong way | flip the sign in `HeadXrAngles` (the test fixes the convention; the runtime may not) |
| pitch logged as written but the view does not tilt | something after the hook re-decides pitch |
