# 2026-10-04 (dev PC, `/pd`, no launch): the camera is decided in one loop, and the yaw test is built

**The game was not launched, attached to or touched.** Everything below is read from the exe and
the cooked script packages, plus a build that compiles and passes its self-test.

## In plain words

Every frame, the game first moves everything, then runs one short loop that asks each player's
camera to work out where it is looking. Only after that does it draw the picture, and drawing
just copies the answer out. So there is one clean moment, right after that loop, where we can
turn the view and the drawing will use our turn. A numpad test for exactly that is built and
installed, switched off.

## What was found

1. **The camera loop** `[inferred-static 2026-10-04]`: `0x008BEF70..0x008BEFE6`, inside the world
   tick. For each controller (`Controller::NextController` at +0x244), if it is a player controller
   with a `PlayerCamera` (+0x3D4), it calls `PlayerCamera->eventUpdateCamera(DeltaTime)` (DeltaTime
   divided by the world's time dilation when set). The `UpdateCamera` FName global is `0x0243AC10`,
   filled at start-up from the wide string at `0x01C040A0`. This matches stock UE3's
   "update cameras last, after all actors have ticked".
2. **Who writes `CameraCache.POV`** `[inferred-static 2026-10-04]`: no native code. `Camera.UpdateCamera`,
   `Camera.FillCameraCache` and `Camera.GetCameraViewPoint` are all **script** in this build (flags read
   from `Engine.u`; none has `FUNC_Native`). No camera subclass (`NTCam_*`, `MKCam_CameraController`)
   overrides `UpdateCamera`, `FillCameraCache` or `GetCameraViewPoint`; they override `UpdateViewTarget`.
   A byte scan of the three bodies (a heuristic, not a bytecode decode) finds `FillCameraCache`
   inside `UpdateCamera`, and `GetCameraViewPoint` (132 bytes) touching only `CameraCache.POV`
   Location and Rotation. So the cache is written inside step 1 and only read afterwards.
3. **The hook spot** `[inferred-static 2026-10-04]`: `0x008BEFE8`, `cmp dword ptr [0x023B88B8],0`
   (7 bytes `83 3D B8 88 3B 02 00`), the first instruction after the loop. It is a single instruction,
   the only jump into it targets its first byte (`je` at `0x008BEF6A`, the "no controllers" case),
   and the code after it holds no live SSE values.
4. **Side finding: ProcessEvent is vtable slot 64 (`+0x100`)** `[inferred-static 2026-10-04, n=845]`.
   845 of the 850 calls to `FindFunctionChecked` (`0x005B3850`) are followed within 40 bytes by a
   `+0x100` displacement, which is UE3's generated `eventXxx()` thunk shape
   (`ProcessEvent(FindFunctionChecked(NAME), &Parms, NULL)` through the vtable). The 2026-09-09
   "64" was withdrawn because the METHOD (merged `.rdata` runs) was unsound; this is a different
   route arriving at the same number. Still static; the vtable entry was not shown to equal
   `0x00580990` directly.

## Which step runs last

Per tick: actors tick, then **the camera loop decides the view (step K)**, then **our hook (step N,
right after K)**, then drawing reads the cache. N is after K and before the reader, so the hook
changes the view instead of annotating it. Writing it from `Present` would be too late: the next
tick's loop rewrites the cache before the next draw.

## What was built

`staging/enslaved-vr/proxy-d3d9/headyaw.inc.h`, wired into `dllmain.cpp` (4 lines), behind
`[headyaw] Enabled=0`:

- At load (before the game's first tick, so no thread can be inside the bytes) it checks the 7
  bytes are exactly the expected ones, refuses otherwise, and puts a jump to a small trampoline:
  save registers, flags and xmm0-7, call our function, restore, re-run the replaced `cmp`, jump back.
- Our function (game thread, integers only, its own `VirtualQuery` reads) finds the live controller
  (needs `[uobject] Probe=1`), checks its class is unchanged, reads `CameraCache.POV.Rotation.Yaw`
  (Camera+0x374), writes yaw + offset, and reads it back.
- `Present` handles numpad 6 / 4 (+/- `StepDeg`, default 15) and 5 (zero), only while the game has
  focus, and logs `[headyaw] ... game yaw X -> after ours Y (diff D) | why` every `Every` frames
  and on each key. **The log proves the effect by itself**: diff equal to the offset means the write
  landed; a stable "game yaw" while the offset is held means no feedback.

`[compile-verified 2026-10-04]`, 0 warnings with `-Wall -Wextra`, self-test 12/12 still passes, 9
exports. The trampoline's bytes were disassembled with capstone and read back as intended.

Installed on the dev PC: `d3d9.dll` `a81c37cf6aab` (102,400 B), `d3d9_proxy.ini` `c1570727ef01`
(the installed ini plus the new section, `Enabled=0`; nothing else changed). Previous files kept as
`*.bak-2026-10-04`.

## The one-launch test (FLAT, still camera)

Set `[uobject] Probe=1` and `[headyaw] Enabled=1`, reach gameplay, stand still, wait for the probe's
live-controller line, then press numpad 6 three times, then 5. Read the `[headyaw]` lines.

| What the log / screen shows | Meaning |
| --- | --- |
| `installed`, diff = offset, view turns 15° per press, holds still, 5 snaps back | the lever works; next is feeding it a head pose |
| `NOT installed` | the bytes differ: wrong exe build; nothing was changed |
| diff = offset but the view does NOT turn | something after the hook re-decides the view (a second update, or drawing reads elsewhere); look at the render path |
| "game yaw" drifts by the offset every tick (spins) | `UpdateCamera` starts from last tick's cache; subtract our offset back before the loop next tick |
| `hook ran 0` | the loop is not reached (paused, menus) or the jump is wrong |
| the player's walking direction turns too | movement reads the camera; fine for a test, matters for VR |
