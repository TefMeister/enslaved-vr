# 2026-09-03d — a device Reset disarms the stereo permanently, and glancing-angle water measures CLEAN

Home PC, `/lm`, fully autonomous after the user reached the title screen.
Third autonomous session on this game, and the first on the **home** machine.

---

## ⭐ 1. A D3D9 device **Reset** kills the stereo, and does not give it back

The board carried this as *"run 1's post-Reset histogram silence is unexplained;
forced windowed makes resets rare, which hides it rather than answers it — needs a
run that resets"*. It got two, and the answer is worse than a logging quirk.

**After a Reset the proxy records ZERO vertex-shader constant uploads, for the rest
of the process's life.** The per-frame histogram still prints its header and then
nothing under it, and the stereo summary drops to `offset 0, ortho-skipped 0`.

`[verified-live 2026-09-03, n=2 resets]`

| | reset 1 | reset 2 |
| --- | --- | --- |
| cause | resolution changed to 1280x720 in the options menu | **an ordinary in-game transition** (checkpoint restart), nothing we did |
| backbuffer at reset | 1280x720 | 3440x1440 |
| frames still dead after | ~28,000, through a load into gameplay | 22,500+ |

- **It is NOT an artefact of being in a menu.** The identical menu was uploading busily
  one log line earlier — 36 x `c0`, a full `c231` matrix — and went silent immediately
  after.
- **It is NOT a dead proxy.** `Present` keeps firing throughout (frame counter advanced
  142320 -> 142680 across 6 s, a clean 60 fps), the `Reset` hook logged the event, and
  the forced-window logic correctly re-applied afterwards. **Only the constants path
  dies.**
- **⭐ It is NOT instantaneous, which is the useful part.** Reset 2 shows one MORE healthy
  summary after the reset (`offset 2054`) and only then goes to `offset 0`. So the thing
  that kills it happens roughly 120–240 frames *after* the reset completes, not inside the
  `Reset` call. UE3 re-creating device objects post-reset is the obvious suspect and is
  checkable with no game running. **`[PD]`, and cheap.**
- **The control is clean:** same DLL, same machine, minutes apart — a fresh launch reads
  `offset 2690 / 3360 / 4000, ortho-skipped 120–1499`. Relaunching always restores it.

**Consequence for every future session: a reset disarms the mod silently.** Nothing on
screen says so. Check `offset` in the log before trusting any stereo observation.

## 2. The game ignores its own saved resolution at startup `[verified-live 2026-09-03, n=2 launches]`

`MonkeyEngine.ini` holds `ResX=1280 ResY=720`, and `CreateDevice` still asks for
**3440x1440** — the desktop size — on every launch. Only the *Reset* ever applied 720p.
The options menu also displayed `1920x1080` while the device was actually 3440x1440.

**So a matched-resolution capture and a working stereo are currently mutually exclusive**,
because the only way to get the backbuffer to match the window is the reset that kills the
stereo. Not a blocker for region tests: a uniform downscale shifts every tile equally, so
"this patch is not moving with its neighbours" survives it.

## ⭐ 3. Reflective water at a glancing angle measures CLEAN — the last stereo unknown is half closed

Chapter 4 "Wherefore Art Thou?", the flooded pool at the chapter start, seen at a shallow
glancing angle with a static camera. **20-frame burst, 16 opposite-eye pairs.**
`[measured 2026-09-03, n=16 eye-pairs, 1 scene]`

- **The water and the ridged concrete blocks standing in it show the LARGEST parallax in
  the frame** (bottom row `+18.3`, `+19.1`, `+7.0`, `+6.2`, `+6.2`, `+5.0` against a frame
  median of `+2.01`). They are the nearest geometry, and parallax scaling up with proximity
  is what correct stereo does. **There is no un-offset region on the water.**
- The rows above reproduce the depth gradient: far alley `+0.62`, mid `+1.0` to `+2.0`,
  near ground `+3.1` to `+5.0`.
- ⚠️ **Treat the magnitude, not the verdict, with caution.** Those blocks are a strongly
  repetitive ridged pattern, and phase correlation on a periodic texture can lock onto the
  wrong period. The robust claim is that the tiles are **not near zero**; `+18` itself is
  worth less than the sign and the ordering.

### ⚠️ The two "suspect" tiles were both HUD — the trap the notes warned about

The detector flagged exactly two tiles at `dx = -0.00` and `+0.00`. Zooming them settled it
in one look: **the bottom-left tile is dominated by the ability radial (`LEAP`/`EMP` dial),
and the bottom-right tile is the item counters.** Both are HUD, both are *supposed* to be
un-offset, and the log agrees — `ortho-skipped 1499 (UI/HUD)`.

So this is a **positive confirmation of the ortho/HUD fix**, not a defect. It also re-earns
the standing rule: *check what is behind a probe region before believing it*.

**Still open: DECALS.** Not tested — identifying a true projected decal by eye is the
problem, not the measurement.

## 4. The measurement was validated before it was trusted

`phase_shift` recovers 7/7 synthetic shifts (0, ±1, 3, 7, 5, 12, 13 px) exactly, and a
deliberately wrong expectation correctly fails. The analyser **refuses to report** on fewer
than 3 opposite-eye pairs, which it did when the stereo was dead: all 17 pairs came back
pixel-identical and it said so instead of inventing numbers.

**The internal control is what makes the rest credible:** same-eye pairs read `+0.000`,
`-0.000`, `+0.000` — exactly zero — while opposite-eye pairs read a consistent `±1.85`.

## 5. Automation on the home PC — 4/4, and the pad works here

- **A virtual XInput pad drives the camera on this machine too**
  `[verified-live 2026-09-03]` — `thumbLX=29490`, `buttons=0x1000`, reproducing the dev PC
  exactly; a hard right-stick pan moved the frame by 34.4 mean difference.
- **⚠️ The pad needs ~2 s after creation before the game acts on it.** At 1 s the scan
  returned a flat, meaningless score curve that read as "the camera will not turn". Not a
  dead route — an impatient one.
- **⚠️ ENSLAVED has no keyboard camera binding at all.** Mouse-look does nothing
  `[disproved 2026-09-03]`. `A`/`D` turn the *character* and the chase-cam trails, which is
  enough to spin on the spot and nothing more — it walked Monkey into foliage and then put
  the camera inside a bush.
- All four capabilities exercised here: menus -> gameplay, chapter select, character +
  camera, and **closing the game** (graceful, through its own QUIT).

Evidence: `dev-archive/recon/2026-09-03d-reset-kills-stereo/` (full proxy log of the run
that reset, plus the water and facade scenes).
