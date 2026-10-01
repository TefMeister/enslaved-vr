# 2026-10-01 (`/lm`, dev PC, driven by Claude): the live player controller is found

*Three launches, menus replayed by Menu-o-matiC, game closed through its own menus each time.*

## What the probe was for

The camera lives on the player's controller. The probe (read-only, never calls into the engine) has to find the
real controller object among ~125,000 objects, by its CLASS rather than its name.

## What happened `[verified-live 2026-10-01]`

1. **Run 1 (frame 300):** `UObject::Class` calibrated at **+0x30**. Eleven PlayerController classes listed, one
   per playable character (Monkey, Pigsy, Trip, Berserker, CDog, Rhino, Scout) plus three engine ones. But the
   "live" controllers it reported were all `Default__...`: the templates every class has. It stopped there.
2. **Fix:** templates (`Default__` prefix) are now counted, not reported, and the probe keeps trying. Self-test
   gained check 12 (a template alone must not end the probe); all checks pass. Built `d3d9.dll` `8c536ea63963`
   (old `36519dfa4b59` archived in `staging/enslaved-vr/proxy-d3d9/archive/`).
3. **Run 2 (frame 300):** one real instance, `MKPlayerController_Monkey`. Frame 300 is still the menus, though.
4. **Run 3 (`FirstFrame=4500`, in gameplay as Monkey, picture saved):** exactly one instance,
   `MKPlayerController_Monkey`, index 130,695.

So the route to the camera is open: controller → its camera → the view. The reader is working out the field offsets
for that next step from the game's files.

## Also done

- **Music off**: Esc → Options → Audio Options → Music Volume, Left tapped (holding does not repeat) until the bar
  is empty. No save prompt. Persisting across a relaunch is not yet checked.
- Probe set back to `Probe=0`; `FirstFrame=4500` kept as the new default.

Evidence: `dev-archive/recon/2026-10-01-lm-live-controller/`.
