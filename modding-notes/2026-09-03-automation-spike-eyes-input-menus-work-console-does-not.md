# 2026-09-03 (`/lm`, dev PC, live) — automation spike: **eyes, input and menus all work; the console does not**

The user defined what "automation" must mean on every game project (see `claude-memory/PREFERENCES.md`
→ *What "automation" MEANS on a game project*): Claude navigating start menu → gameplay, issuing
console commands, moving character and camera to reverse-engineer the engine, and closing the game
itself when a swap or an exhausted lane needs it.

Rather than build a harness and discover it could not reach the menu, this session proved the
foundations first, with **no DLL rebuild**, against a live level the user had loaded. All of it is
external tooling driving the game window.

**Result: 3 of the 4 required capabilities are proven — eyes, input, menus (both directions) and
the self-quit. The 4th (console commands) is NOT reachable by keypress, but a promising alternative
was found and is staged for the next launch. See Part 2.**

---

## 1. ✅ Eyes — Claude can see the game

A window capture at the forced-windowed 1280×720 produces a clean, readable frame
`[verified-live 2026-09-03, n=many]`. Confirmed by actually reading the images, not by a
"has content" heuristic.

> ### ⚠️ `PrintWindow` serves a STALE frame when the game stops presenting — use `BitBlt`
> This is the single most important trap found today, because it fails in the worst possible
> direction. While the game renders, `PrintWindow(PW_RENDERFULLCONTENT)` returns correct live
> frames. When the game **stops** presenting — paused, in a menu, hitching — it keeps returning the
> last composed frame from the DWM cache, indefinitely and with no error.
>
> It was caught because six consecutive captures were byte-identical and the first delta of each run
> was *exactly* `6.91` — a repeating constant is a cache signature, not a scene. A `BitBlt` of the
> window rect from the screen DC showed the truth immediately: the pause menu was open.
>
> **So: the moment the picture matters — is the game paused, did the menu open, did the level
> load — `PrintWindow` is exactly the wrong tool.** `BitBlt` reads the real screen (and needs the
> window unoccluded). A proxy-side backbuffer readback would beat both and is the right long-term
> answer. `[verified-live 2026-09-03]`

## 2. ✅ Input — `SendInput` drives both camera and character

| route | result |
|---|---|
| `SendInput` **relative mouse** | ✅ camera turned through a large arc, entirely different scene |
| `SendInput` **keyboard scancode** (`W` = `0x11`) | ✅ character walked forward, visibly closer to scenery |
| `SendInput` keyboard **virtual-key** | untested properly — superseded, scancode is preferred anyway |
| `PostMessage WM_KEYDOWN` | ⚠️ **no evidence it works** — see the measurement warning below |

`[verified-live 2026-09-03, n=1 per route, confirmed visually]`

**Scancodes rather than virtual keys, deliberately.** Carried over from `doom-2016-vr`, where
`scan 0x29` opened the console with no virtual key in the path and routed around a keyboard-layout
trap for good. The same reasoning applies here and costs nothing.

> ### ⚠️ The first measurement method was WRONG, and nearly produced a false negative
> The first attempt scored each route by **mean luma difference** between a before and after frame,
> against a no-input control (per the standing "measure against a no-input control" rule). It
> reported **`SendInput scancode W` as "no effect"** — which is false; the key demonstrably walks
> the character.
>
> Why it failed: this scene has animated grass, water and an idle animation, so the no-input control
> itself ranged **3.38 → 23.27**, and a threshold of 2× the control peak (46.5) sat *above* the real
> signal (41.1). The control was right in principle; whole-frame mean luma was simply too blunt a
> statistic for a scene with that much ambient motion.
>
> **What worked instead: looking at the pictures.** A large, unmistakable action (a ~120-step mouse
> sweep, a 2.2 s key hold) and then reading the two frames. **When a cheap decisive observation
> exists, prefer it to a statistic that has to out-run scene noise.** If a numeric measure is wanted
> later, the right one is a global-shift estimate (phase correlation), not a mean difference —
> camera motion is a coherent global translation, grass sway is not.

## 3. ✅ Menu navigation — the pause menu is fully drivable

`ESC` opens **PAUSED** with `RESUME GAME` / `OPTIONS` / `RESTART FROM LAST CHECKPOINT` /
`EXIT TO MAIN MENU`, and the menu states its own controls on screen: **`ENTER` SELECT, `ESCAPE`
BACK**. Sending `ENTER` (scancode `0x1C`) selected the highlighted `RESUME GAME` and the game
resumed — frame deltas went from a flat `0.00` (paused, not presenting) to a steady `~21`
`[verified-live 2026-09-03, n=1]`.

That is the menu-navigation capability demonstrated end to end: pause, read the menu, choose an
item, return to gameplay. `EXIT TO MAIN MENU` is present, so start-menu → gameplay should be
reachable by the same means; not yet exercised.

**Found by accident, and worth saying plainly:** the pause menu opened because this session sent
`ESC` as "cleanup" after the console probes. Blind cleanup keystrokes are not neutral — in this
game `ESC` pauses. Automation should read the screen after any key it is not certain about, rather
than assuming a keypress did nothing.

## 4. ❌ Console — NOT reachable by keypress in this build

`[verified-live 2026-09-03, n=3 keys]` Tried, each with a fresh capture afterwards:

| key | scancode | result |
|---|---|---|
| Tilde (`ConsoleKey`) | `0x29` | nothing — scene unchanged |
| Tab (`TypeKey`) | `0x0F` | nothing — scene unchanged |
| F10 | `0x44` | nothing — scene unchanged |

**This confirms §7's long-standing suspicion** — *"Shipping build may have the console class
stripped despite the binding (common in UE3 releases)"* — and settles the item that said *"first
session in-game should just press Tilde"*. Pressed. Nothing.

⚠️ **This is `n=3` keys on one build, not proof the console is unreachable by any means.** What it
rules out is the cheap route.

**The named untested alternative, and it is promising:** dossier §10a records exec-via-key-binding
as reported working on this build — `Bindings=(Name="F1",Command="FOV 0")` under
`[MonkeyGame.MKInput]` in `MonkeyInput.ini`. That is a *different* mechanism from the console: not
a prompt to type into, but a bound key that executes a command string. If it works, a block of
pre-bound keys gives Claude an arbitrary command vocabulary without a console existing at all.
**It needs a relaunch to test** (input inis are read at load), which is why it is not answered here.

## 5. Incidental, but it matters: the ortho/HUD fix is firing live

First live evidence for the fix built on 2026-09-02 and deployed to this machine today:

```
[stereo] on=1 mode=0 sep=6.500 | offset 2640, ortho-skipped 1485 (UI/HUD),
         rejected: c0-zero-row0 0, c0-other 0 (should be 0), c3/c10-no-match 7491
```

`ortho-skipped` ≈ 12 per frame, so the `IsOrthographic` skip is genuinely catching UI uploads
rather than sitting dead. **`c0-other` is `0`** — the one counter whose non-zero value would mean
the whole c0-is-the-view-projection premise is wrong `[measured 2026-09-03]`.

⚠️ That the mechanism *fires* is not the same as the HUD *visually* holding still under stereo.
That remains unjudged.

## 6. What is NOT established

- **Whether `PostMessage` input works.** The mean-luma method that scored it was unsound, and it
  was never re-tested visually. Treat its "no effect" as unmeasured, not as a negative.
- ~~**Whether the game can be driven from the START menu**~~ — **answered in Part 2 below: yes,
  both directions, gameplay → main menu → gameplay.**
- **Whether the keybinding exec channel works** — needs a relaunch.
- **Whether the game pauses on focus loss.** Suspected from an early sample but never isolated,
  because the pause menu confounded it. The practical rule stands regardless: foreground the window
  before acting.
- **Nothing about VR, comfort, or how any of this looks.** No headset involved.
- **Everything in Part 2 §8 (the debug free camera) is read from CONFIG, not run** —
  `[inferred-static 2026-09-03]`. The console's bindings also survive in the ini and the console is
  dead, so shipped bindings are not evidence a feature is live.
- The scripts used here are **spike code** in the session scratchpad, not a harness. Their value is
  the four facts above, not the code.

---

# Part 2 (same session) — menus driven end to end, the game closed itself, and **the engine ships a debug free camera**

## 7. ✅ Full menu navigation, both directions, and a graceful self-quit

Driven entirely by Claude, verified by reading each screen `[verified-live 2026-09-03, n=1 run]`:

**gameplay → `ESC` → pause menu → ↓↓↓ → `EXIT TO MAIN MENU` → `ENTER` → confirm → main menu →
`CONTINUE JOURNEY` → `ENTER` → load → back in gameplay → `ESC` → … → main menu → ↓×6 → `QUIT` →
process exits in ~4 s.**

- **The pause menu**: `RESUME GAME` / `OPTIONS` / `RESTART FROM LAST CHECKPOINT` / `EXIT TO MAIN
  MENU`, and it prints its own controls: `ENTER` SELECT, `ESCAPE` BACK.
- **The main menu**: `CONTINUE JOURNEY` / `CHAPTER SELECT` / `NEW JOURNEY` / `EXTRAS` / `OPTIONS` /
  `CREDITS` / `QUIT`. **`CHAPTER SELECT` matters for RE** — arbitrary chapters on demand means
  varied scenes without hunting for them.
- **Closing is a graceful menu quit, not a force-kill** — which is the disposition the RE Village
  incident argued for.

> ### ⚠️ Arrow keys need `KEYEVENTF_EXTENDEDKEY`, or the menu ignores them
> Three `Down` presses as bare scancode `0x50` moved the selection **not at all** (delta `0.00`
> each). Arrows are *extended* keys: without the flag, scancode `0x50` is numpad-2, which this menu
> does not bind. With `KEYEVENTF_EXTENDEDKEY` the selection moved on the first try
> `[verified-live 2026-09-03]`. `S` and non-extended `0x50` both stayed dead, so this is the flag
> and not the key choice.
>
> This is the same family as DOOM's scancode/keyboard-layout trap: **the input reaches the OS
> either way, so nothing errors — it simply does nothing**, which reads exactly like "the menu
> ignores keyboard".

**Safety note worth keeping:** on the main menu, `NEW JOURNEY` sits two rows below `CONTINUE
JOURNEY`. A miscounted `Down` would overwrite the save. The sequence above therefore **navigates,
captures, verifies the highlight visually, and only then sends `ENTER`.** Blind key-count
navigation on a menu with a destructive item is not acceptable.

## 8. ⭐ THE BIG ONE: `[NTGameFramework.NTCam_DebugInput]` — the engine ships a debug free camera

Found in `MonkeyInput.ini` while preparing the exec-channel test. **This is shipped stock config,
not something we added:**

| binding | command | what it would give us |
|---|---|---|
| `Alt+C` | **`ToggleDebugCamera`** | a free camera, the engine's own |
| `W`/`S`/`A`/`D`, `Q`/`E` | `MoveForward`/`Backward`, `Strafe`, `MoveDown`/`Up` | fly it, including vertically |
| `MouseX`/`MouseY` | `Axis aMouseX`/`aMouseY` | look |
| `LeftShift` | `MoreSpeed` / `NormalSpeed` on release | speed control |
| `F` | **`FreezeRendering`** | freeze the render, fly out, inspect the frustum |
| `End` / `PageDown` | **`Pause` / `Step`** | frame stepping |
| `F9` | `shot` | screenshot |

**If `ToggleDebugCamera` is live in this shipping build, most of the "move the camera to
reverse-engineer the engine" requirement is already solved by the engine** — with speed control,
render-freeze and frame-stepping thrown in — rather than needing a camera override built on top of
the proxy's `c0` hook.

**The entry point in normal gameplay is a CONTROLLER CHORD, not a key.** `[Engine.PlayerInput]`
binds `XboxTypeS_RightThumbstick` → `CheckDebugCamChord | DoCloud` and `XboxTypeS_LeftThumbstick` →
`DoDebugCamChord | …`; line 151 carries a commented-out `ToggleDebugCamera` on the left thumbstick.
So the feature is wired for a pad, and the `Alt+C` binding lives *inside* the debug-camera input
class — i.e. it toggles back off once you are already in it.

**⚠️ All of this is `[inferred-static 2026-09-03]` — read from config, nothing run.** The shipping
build may well have the debug camera stripped even though its bindings survive in the ini; that is
exactly what happened to the console. **`F9="shot"` shipping in this same file is the encouraging
sign**, because it is an ordinary exec command bound to a key by the developers.

## 9. What is staged for the next launch

The game is closed, so `MonkeyInput.ini` can be edited without the engine rewriting it on exit.
Added to `[Engine.PlayerInput]` (live copy under `Documents\My Games\…`), inside a clearly marked
`CLAUDE-EXEC-TEST` block with a removal note; backup `MonkeyInput.ini.bak-2026-09-03-pre-exectest`:

| key | command | what its outcome means |
|---|---|---|
| **F5** | `ToggleDebugCamera` | ⭐ the whole question. A detached flyable camera = the RE camera is free |
| F6 / F7 | `FOV 120` / `FOV 70` | a visible FOV change proves **arbitrary** exec, not just a whitelisted one |
| F8 / F11 | `stat fps` / `stat unit` | an overlay appears = the `stat` family is live |
| F12 | `FreezeRendering` | freeze = the render-debug family is live |
| (F9) | `shot` — **already shipped** | a screenshot file appears = the channel works at all |

**F9 is the cheapest and most decisive single test**, because it is the developers' own binding: if
pressing F9 produces a screenshot file, the key-binding exec channel is live in this build and the
console's absence stops mattering.
