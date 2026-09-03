# 2026-09-03c (`/lm`, dev PC, live, fully autonomous) — the debug camera is unreachable by ANY input route, and the wet-floor stereo test comes back clean

Second autonomous session of the day. User launched to the title screen, said "all yours", left.
Claude drove title screen → main menu → gameplay → chapter select → a new chapter, and every
measurement. ViGEmBus had been installed and proven between the two sessions.

---

## 1. ❌ The debug-camera controller chord does NOT work — and this time the control passed

The last untried route to the shipped `[NTGameFramework.NTCam_DebugInput]` free camera. Its
normal-play entry point is a controller chord (`CheckDebugCamChord` on RightThumbstick,
`DoDebugCamChord` on LeftThumbstick in `[Engine.PlayerInput]`), which no key can send — so a virtual
pad was the only way to try it.

**Sent LS+RS held together for 1.2 s via a ViGEmBus virtual X360 pad. No debug camera:** `W`
afterwards still walked the character with the chase-cam behind him `[verified-live 2026-09-03]`.

> ### ✅ The control that makes this a real negative
> A negative is only evidence if the test could have produced a positive, so the obvious failure —
> *the game never saw the pad at all* — was ruled out directly. With the same pad object:
> **left stick full forward for 2.5 s moved Monkey (frame delta 48.9), and right stick right for
> 2.0 s swung the camera onto entirely different scenery (delta 62.5)**, against an idle baseline
> of about 2. Confirmed visually, not just by the numbers.
> **The game reads the virtual pad. The chord genuinely does nothing.**

### ⇒ The conclusion this completes

**The debug camera is unreachable in this build by any input route — pad or key.** That is not three
unrelated failures but one cause: `ToggleDebugCamera` is an **exec** command, exec dispatch is
stripped from this shipping build (2026-09-03b), and the chord's job is ultimately to *call* it. The
input side works perfectly; there is nothing left at the other end to receive it.

**So the only remaining route to a free camera is in-process** — either locating the engine's exec
entry point from our own `d3d9` proxy and calling it directly, or overriding the view-projection at
`c0`, which the proxy already does for stereo. Both are `[PD]`, no game needed.

## 2. ⭐ New capability: the virtual pad DRIVES this game

Worth stating separately from the chord result, because it is a positive finding that outlives it:
**ViGEmBus + a virtual X360 pad is a working third input route for Enslaved**
`[verified-live 2026-09-03]` — movement on the left stick, camera on the right, hot-plugged into a
running game with no restart. For any game that ignores synthetic keyboard, or gates something
behind a controller, this is now a proven tool
(`flat-to-vr-RE-toolkit/tools/virtual-pad.py`).

## 3. Chapter select works, and it costs something

`[verified-live 2026-09-03]` The route is longer than the profile assumed:

**main menu → CHAPTER SELECT → pick chapter → `DIFFICULTY SELECT` (NORMAL default) → a warning →
load.** Five chapters were unlocked. Chapter 2 "The Old City" loaded in roughly 60-90 s including a
long opening cutscene.

> ### ⚠️ "This will reset your last checkpoint."
> Chapter select is **not** free. It resets the CONTINUE pointer, so the player's position inside
> their current chapter is lost. Chapter *unlocks* survive, so it is recoverable by selecting the
> old chapter again, but it should not be used casually on someone's live save. The user had
> explicitly suggested trying different saves, which is why it was taken here.

## 4. ✅ The wet-floor / caustics stereo test comes back CLEAN

Chapter 2 opens on a **wet tiled floor with rippling caustics** — exactly the screen-space-looking
effect that the 310 un-offset **pixel** shaders (§4/§9) would break, and the closest thing yet to the
board's long-standing "get close to water / a wet floor / a decal" item.

Method: tile the frame on an 80 px grid, phase-correlate each tile between opposite eyes, and look
for **outliers from the per-row median** — a screen-space effect that ignores the eye offset would
sit near zero while its neighbours move.

| row | median dx | outliers |
|---|---|---|
| y 80–240 | +11 | none |
| y 240–320 | +11 | 1 |
| y 320–480 | +17 | 2 |
| y 480–560 | +18 | 1 |
| y 560–640 | +22 | 2 |

The depth gradient is there again (+11 → +22 with proximity). **The large outliers (+26…+29) are
Monkey himself** — he is the closest object to the camera, so a bigger shift is correct.

> ### ⚠️ One tile read +0, and it was a FALSE ALARM — worth recording because it nearly wasn't
> A single tile at y560–640, x280 measured **dx = +0** while its whole row moved +22. That is
> precisely the predicted signature of an un-offset screen-space effect, and it sat right on the
> caustics.
>
> Re-measured across the **four** best eye-pairs instead of one, the same tile reads
> **+24, −22, +18, −18**, tracking its neighbour (**+22, −18, +16, −16**) within ~2 px with the
> signs flipping together. The `+0` was a single low-confidence correlation failure.
>
> **The lesson: one eye-pair is not a measurement.** A phase-correlation peak on a low-contrast or
> fast-changing tile can land anywhere, and it lands on a value that looks exactly like the bug you
> are hunting. Repeat across pairs and require the sign to flip before believing it.

**So no un-offset region was found**, including on the wet floor. `[measured 2026-09-03, n=4 eye-pairs]`

## 5. What is NOT established

- **This is not proof the 310 pixel shaders are harmless.** It is one wet floor in one chapter.
  Reflective water surfaces seen at a glancing angle, and decals, remain untested — and correlation
  confidences here were lowish (0.06–0.30), which is why the four-pair agreement carries the claim
  rather than any single number.
- **Nothing about VR or comfort.** All flat-screen measurement.
- **The in-process exec route remains an idea** — no entry point has been located.
- Whether `CHAPTER SELECT` preserves collectables/upgrades was not checked; only that chapter
  unlocks survive and the checkpoint resets.
