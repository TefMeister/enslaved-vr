# 2026-09-03b (`/lm`, dev PC, live, fully autonomous) — the exec channel is dead; the stereo is geometrically correct

The user launched the game at the title screen, said "all yours", and left. **Everything below was
driven by Claude**: title screen → main menu → gameplay, all navigation, all measurement. This is
the first session run under the new definition of automation (`PREFERENCES.md`), and the first use
of the per-game profile at `ai-game-control-profiles/profiles/enslaved.json`.

---

## 1. ❌ The key-binding exec channel is DEAD too. Automation capability 2 is blocked.

Yesterday's staged test, run three ways. `[verified-live 2026-09-03, n=3 commands]`

| test | expectation if the channel were live | result |
|---|---|---|
| **F9 = `shot`** — a **developer** binding shipped in `MonkeyInput.ini`, not one we added | a screenshot file appears | **no file written** anywhere under the game tree or `Documents\My Games` |
| **F6 = `FOV 120`** | obvious, large framing change | **none** — framing pixel-for-pixel comparable, tree/crane at identical distances |
| **F5 = `ToggleDebugCamera`** | camera detaches; `W` then flies the camera | **none** — `W` still walked the character with the chase-cam behind him |

**The test could have produced a positive**, which is what makes this evidence rather than an
absence: the `CLAUDE-EXEC-TEST` block was verified still present in the live
`Documents\…\MonkeyGame\Config\MonkeyInput.ini` after the launch (mtime unchanged from when it was
written, so the engine did not rewrite it), and **F9 is a binding the developers shipped** — that
one is independent of our edit entirely.

### What this means, and it is a coherent picture rather than three separate failures

**This build kept its input/action bindings and stripped its exec-command dispatch.**

- Action and axis bindings work fine — movement, menus, ESC, ENTER, arrows all drive the game.
- Console-style *exec* commands (`FOV`, `shot`, `ToggleDebugCamera`) dispatch nowhere.

That is exactly what a shipping UE3 build looks like when the console/cheat-manager path is
compiled out: the bindings survive in config because config is just text, but nothing is left to
execute the command strings. It also **retires yesterday's optimism about the shipped
`[NTGameFramework.NTCam_DebugInput]` debug-camera map** — the map is real, and unreachable by this
route.

> **The general lesson, stated plainly because it cost two sessions:** a binding surviving in a
> shipped config file is not evidence the feature behind it is live. Enslaved ships console
> bindings with no console, and a full debug-camera map with no reachable debug camera. **Config is
> a lead; running it is the evidence.**

### What is still open for capability 2 — and one route is better than anything tried so far

- **⭐ In-process exec, from our own proxy.** We already own `d3d9.dll` and run inside the process
  every frame. Locating the engine's exec entry point by pattern and calling it directly bypasses
  input, bindings and the console entirely. **This is the strongest remaining route** and it is
  `[PD]` work — static analysis of a 34 MB binary, no game required.
- **A virtual gamepad.** The debug camera's normal-play entry point is a controller thumbstick
  chord (`CheckDebugCamChord` / `DoDebugCamChord`), which a real or emulated pad could send. The
  estate already has a `[USER]` item for installing **ViGEmBus** (recorded under `doom-2016-vr`),
  which is exactly the tool for this. Worth noting the two projects now share that dependency.
- Not worth retrying: more keys. Six have been tried across two sessions.

## 2. ⭐ The stereo is geometrically correct — measured, in two scenes

The proxy was running `Enabled=1 Mode=0 (wiggle) Separation=6.5`. In wiggle mode consecutive frames
are opposite eyes, so two frames captured close together differ by the full eye offset. **Phase
correlation per screen region** turns "does it look right" into a number.

**Why phase correlation and not a frame difference:** an eye offset is a *coherent global
translation* of a region; animated grass is not. A mean difference cannot separate them — that is
precisely the statistic that scored a working keypress as "no effect" earlier today.

### Scene 2 (close rocks, near-field geometry) — the clean one

`[measured 2026-09-03, n=18 tiles per row band]` Horizontal shift by screen row, which for ground
geometry is a proxy for depth (lower on screen = nearer the camera):

| screen row | dx (px) | |
|---|---|---|
| y 110–174 | **−1.4** ± 2.1 | skyline / far |
| y 174–238 | −1.5 ± 2.1 | |
| y 238–302 | −1.9 ± 2.5 | |
| y 302–366 | −4.9 ± 4.8 | mid |
| y 366–430 | −9.7 ± 3.0 | |
| y 430–494 | −12.4 ± 2.2 | |
| y 494–558 | **−13.6** ± 1.3 | nearest |
| y 558–622 | −12.0 ± 5.4 | |

**That is a textbook parallax curve**: near-zero at infinity, rising smoothly and monotonically to
~13 px at the closest geometry. Parallax scaling inversely with distance is the thing correct
stereo does and an incorrect offset does not. Scene 1 agreed on the same ordering
(far +2, mid +5, near ground +10), and the **sign flipped** between eye pairs as wiggle demands.

### ✅ The HUD does NOT hop — the 2026-09-02 ortho fix is confirmed live

`[verified-live 2026-09-03, n=2 scenes]` In scene 2 **both** HUD probe boxes measured **dx = 0**:
the bottom-left ability radial and the top-left health/shield bars.

⚠️ **Scene 1 nearly produced a false alarm here, and the reason is worth keeping.** The top-left
bars box read ±4–6 px there, which looks like a hopping HUD. Cropping and magnifying both eye
frames showed the truth: **the bars held position while the foliage behind them moved.** That box is
~70 % world seen through a translucent overlay, so the correlation locked onto the background. In
scene 2 the same box sits against a static dark trunk and reads exactly 0.
**A HUD probe region must be checked for what is behind it before its number is believed.**

### No shadow swim detected in these scenes

The highest-prior open risk was the 310 un-offset **pixel** shaders (§4/§9) — if shadows reproject
using the un-offset view-projection they would sit still while the ground moves. Tiles in the ground
band were split by brightness (dark = shadow, bright = lit) and correlated separately:
**shadow tiles measured −9 to −13 px, tracking the same depth gradient as everything else**, not
sitting near zero `[measured 2026-09-03]`.

### ✅ UPGRADED, same session: the matched-depth test WAS obtained, and shadows pass it exactly

Navigating on to a third area produced the frame the earlier test lacked: Monkey's own cast shadow
hard against the camera, with lit grass beside it **on the same screen rows** (therefore the same
depth), plus a second shadow/lit pair further back.

`[measured 2026-09-03, n=2 depth bands x 3 eye-pairs]`

| region | dx per eye-pair (px) |
|---|---|
| CLOSE cast shadow (own) | −14, −13, **+13** |
| LIT grass, SAME rows | −14, −14, **+14** |
| mid shadow band | −8, −8, **+8** |
| mid LIT grass, SAME rows | −8, −8, **+8** |
| bright reflective surface (further) | −5, −5, **+5** |

**Shadow and lit ground at the same depth move identically — within 1 px at the near band and
exactly at the mid band, with the sign flipping together.** Shadows are offset correctly; they do
not swim. That closes the board's highest-prior watch item, which existed because a public 3D Vision
fix for this exact game had to correct shadows.

⚠️ **What this still does NOT prove.** Three scenes, all daylight exteriors. It also says nothing about **screen-space** effects —
reflections, water surfaces, decals — which are the likelier home of the pixel-stage problem. The
board's "get close to water / a wet floor / a decal" item is **not** answered by this.

## 3. Automation scorecard after this session

| capability | state |
|---|---|
| 1. Start menu → live gameplay | ✅ **done** — title screen → main menu → gameplay, unaided, this session |
| 2. Console / exec commands | ❌ **blocked** — console stripped, exec dispatch stripped. Best remaining route is in-process from our proxy `[PD]` |
| 3. Move character + camera | ✅ **character yes**; camera is chase-cam only. A *free* camera still wants either the proxy `c0` override or the pad chord |
| 4. Close the game itself | ✅ **done** (2026-09-03a, graceful menu quit) |

## 4. What is NOT established

- **Nothing about how any of this looks or feels in a headset.** All of the above is flat-screen
  measurement. The stereo being *geometrically* correct says nothing about comfort, and the
  `Separation=6.5` value is still confirmed only by fitting, not by wearing it.
- **Close-range water / wet floor / decal behaviour** — the specific board item — remains untested.
  Navigation reached a rocky area with water at the frame edge but never got hard up against it.
- **Whether the game read our edited ini** is inferred, not proven; the mtime was unchanged and the
  block was present. The F9 result does not depend on this, since that binding shipped with the game.
- **The in-process exec route is an idea, not a finding.** No entry point has been located.
- Tile-based depth inference assumes lower-on-screen means nearer, which holds for ground planes and
  not for arbitrary geometry.
