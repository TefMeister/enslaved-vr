# 2026-09-09 — the pause blocker was an invented ini section, and the reset re-arm works

**Dev PC, `/lm enslaved-vr`, three flat launches, autonomous throughout.** Both of the
project's top two `[FLAT]` rows are answered, and the answers point in opposite directions:
the blocker was **ours** (a config edit), and the build it cast doubt on is **fine**.

Evidence: `dev-archive/recon/2026-09-09-pause-blocker-and-reset-rearm/` — three proxy logs
and 24 screenshots.

---

## 1. ⛔️→✅ The pause menu opens. The 2026-09-07 blocker was the ini we wrote.

**Escape opened the pause menu on the first press, in run 1, with nothing changed from
how the machine was left on 2026-09-07 except the ini** (which that session had already
reverted). Then it was reproduced and un-reproduced deliberately:

| run | `MonkeyInput.ini` | Escape in gameplay | F4 → `DoPause` | `W` |
| --- | --- | --- | --- | --- |
| 1 | reverted state (the 2026-09-03 exec-test block only) | **pauses**, twice | not bound | walks |
| 2 | the 2026-09-07 test ini, byte-identical | **nothing**, ×2 (90 ms and 300 ms holds) | nothing | walks |
| 3 | run 2's ini **minus `[MonkeyGame.MKInput]`** | **pauses**, first press | nothing | walks |

`[verified-live 2026-09-09, n=1 A/B pair]` — one change between run 2 and run 3, one
outcome flip.

**So the cause is the invented section, not the added bindings.** `[MonkeyGame.MKInput]`
does not exist in this build; the 2026-09-07 session created it to test a community report.
Creating it silently disables Escape and the F-keys while leaving character movement
working — which is precisely the signature that session recorded and could not explain.

- **This EXONERATES the 2026-09-04 self-healing proxy** (`d3d9.dll`, 78,336 B), which was
  the loudest suspect because it had never been run. It was installed and running in all
  three launches today, including the two where Escape worked `[verified-live 2026-09-09, n=3 launches]`.
- **The concurrent-`/lm` focus-contention hypothesis is not needed to explain 2026-09-07.**
  It is not disproved as a general hazard — it remains real and remains in `CONVENTIONS.md`
  — but it is no longer the explanation of record for this failure. `[hypothesis]`
- **The route `gameplay → main_menu` is re-established** and was walked twice today, plus
  `main_menu → process_exit` twice. The profile's `disputed` marking is lifted.

### The operational rule this earns

**Never create a config SECTION this build does not ship.** Adding `Bindings=` lines inside
a section that already exists is harmless (run 3 carried two of them and behaved normally).
Inventing a section name is not: UE3 accepts the file, the game starts, nothing errors, and
input silently degrades. The failure looks like the game ignoring the keyboard.

### Free negative, worth keeping

With `Bindings=(Name="F4",Command="DoPause")` and `Bindings=(Name="F2",Command="Pause")`
live in `[Engine.PlayerInput]` in run 3, **neither fired** while Escape worked in the same
session `[verified-live 2026-09-09, n=1]`. Bindings we add to that section are inert in this
build — consistent with 2026-09-07's finding that the section is gamepad-only. **The exec
question still has no valid control**: an alias that never fires cannot distinguish
"exec dispatch is stripped" from "this file's bindings are not read for the keyboard".

---

## 2. ⭐⭐ A device Reset reverts slot 94, the proxy re-patches it the same frame, and the
stereo keeps working

The reset row's reading table is answered, and its success branch is the one that happened.

**Two Resets, both from stepping the resolution in DISPLAY OPTIONS (1280x720 → 1280x768 →
back). Both identical** `[verified-live 2026-09-09, n=2 resets]`:

```
[reset] returned hr=0x00000000 at frame 24436; slot94=NOT ours slot17=ours slot16=ours (before any re-arm)
[rearm] reset-return: slot 94 (SetVertexShaderConstantF) had REVERTED to the runtime's original
        71757420 at frame 24436 (0 frames after the last Reset, 0 state blocks recorded so far)
        -> re-patched (total re-arms 1)
```

and afterwards, every summary to the end of the run:

```
[stereo] on=1 mode=0 sep=6.500 | offset 2760, ortho-skipped 240 (UI/HUD), … | re-arms 1, state blocks 0, slot94=ours
```

- **`slot94=NOT ours` while 16 and 17 stayed ours** — the Reset rewrites exactly one slot,
  the state-**setting** method, which is the shape the 2026-09-04 research predicted.
- **`state blocks 0`, across the entire session** — no `BeginStateBlock`/`EndStateBlock` pair
  was ever recorded, before or after either Reset. **The recorded-state-block explanation is
  therefore NOT what happens here**; the revert is at `Reset` itself, `0 frames after` it
  returned. The 2026-09-04 `[hypothesis]` is not supported for this game
  `[verified-live 2026-09-09, n=2 resets]`. (It stays a valid general mechanism — it is simply
  not this game's.)
- **`offset` non-zero for the rest of the run ⇒ the stereo SURVIVES a reset now.** The
  2026-09-03d "a Reset disarms the stereo for the life of the process" is fixed, by the
  2026-09-04 build, on its first live run.

### ⚠️ And one claim that did NOT reproduce: a checkpoint restart caused no Reset at all

Run 1 did a full `RESTART FROM LAST CHECKPOINT` — menu, confirmation, reload into a cutscene
— and the log records **zero `[reset]` lines** across it, with `offset` healthy either side
`[verified-live 2026-09-09, n=1]`. That contradicts 2026-09-03d, which listed an ordinary
checkpoint restart as one of its two resets.

The two runs differ in machine and in display path: 09-03d was the **home PC** (3440x1440
desktop, and that session also proved the game ignores its stored resolution and asks for the
desktop size). Today's dev PC runs the proxy's forced 1280x720 window over a 1920x1080
backbuffer. **The honest statement is now: a resolution change resets the device on both
machines; a checkpoint restart resets it on the home PC and did not here.** Which of machine,
resolution or window mode decides it is not established.

---

## 3. Automation scorecard (the five capabilities)

| # | capability | today |
| --- | --- | --- |
| 1 | self-launch | ✅ three launches, no user involvement `[verified-live 2026-09-09, n=3]` |
| 2 | menu → gameplay | ✅ three times, title → CONTINUE JOURNEY → gameplay |
| 3 | console / exec commands | ❌ still nothing. No console, and ini bindings are inert (§1) |
| 4 | character + camera | ✅ movement (`W`); camera not exercised today |
| 5 | self-close | ✅ two graceful quits through the game's own QUIT; one `WM_CLOSE` in run 2, where the pause menu was deliberately broken |

Four of five. Capability 3 is the only gap, and it is a game limitation rather than a
harness one.

---

## 4. Housekeeping

- `MonkeyInput.ini` restored to its known-good state and hash-checked against
  `MonkeyInput.ini.bak-2026-09-07-pre-pausetest` (`82d136c0…`). Two new labelled copies kept
  beside it: `…claude-known-good-2026-09-09` and `…claude-playerinput-only-2026-09-09` (run 3's).
- In-game resolution left where it started, 1280x720.
- Deployed files unchanged and re-checked `OK` after the session.
- The game was closed. Nothing is left running.
