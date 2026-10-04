# BL1GOTYVR turns the view just before drawing, and puts the game's camera back afterwards

**Found 2026-10-04 (`/gr`, estate sweep).** Source: Mastersellz's BL1GOTYVR, `docs/HOOK_RESEARCH.md`, read through
the GitHub API. Borderlands 1 GOTY Enhanced is Unreal Engine 3, like Enslaved. Nothing here was run, and no code was
copied.

## What it is

Borderlands 1's VR mod applies the headset pose to the game's own view cache, the same idea as our `[headyaw]`
test, but with a restore step around it `[reported 2026-10-04]`:

1. It hooks the live `GameViewportClient`'s `Draw` (found at runtime; slot 2 of a secondary vtable at object
   `+0x60`), which runs once per game frame.
2. Before calling the original `Draw`, it **saves** the player controller's `CalcViewLocation`,
   `CalcViewRotation` and `CachedFOVAngle`, then writes the OpenXR head pose and the eye offset into them.
3. It calls the original `Draw` **exactly once**. Calling it twice in one frame corrupts the UE3 heap
   (`0xC0000374`) in that build.
4. It **restores** the saved values after `Draw`.

In Borderlands 1 Enhanced the standard `PlayerController::PlayerCamera` is null during gameplay, so the view lives
on the controller itself. In Enslaved it does not: `PlayerCamera` is live and its `CameraCache.POV` is what drawing
copies out (dossier §9e, §9h).

## Why it matters for Enslaved

Our 2026-10-04 `[headyaw]` hook writes the yaw into `CameraCache.POV` right after the camera loop and **never puts
it back**. Between that write and the next tick's camera update, anything in the game that reads the cache (aiming,
movement direction, AI checking what the player looks at) sees the turned view, and if the camera update starts from
last tick's cache, the offset feeds back and the view spins. The test's outcome table already names both symptoms.
BL1GOTYVR's restore step avoids both by keeping the change inside the drawing window `[hypothesis]` for Enslaved,
since the two games keep their view in different places.

## Next step

If the one-launch `[headyaw]` test shows the walking direction turning, or the yaw spinning: add a matching
**restore** after drawing (the equivalent point in Enslaved is after the frame's draw, before the next world tick),
rather than moving the write. If it shows neither, keep the current shape and note that the cache is fully
rebuilt each tick.

## Credits

Mastersellz (BL1GOTYVR).
