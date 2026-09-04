# 2026-09-04 (`/pd`, dev PC, static only) — the vtable patch now heals itself after a Reset, and "exec dispatch stripped" is downgraded to a hypothesis

**The game was not launched, and nothing here has been run.** One build, deployed on the dev PC;
three `/gr` inbox drops folded into the dossier; the board's three `[PD]` rows re-shaped.

---

## 1. Why a Reset disarmed the stereo — the leading explanation, and a build that survives it either way

**What was known** (2026-09-03d, home PC): after any `Reset`, `SetVertexShaderConstantF` stopped
being reached for the rest of the process, while `Present` and `Reset` kept firing
`[verified-live 2026-09-03, n=2 resets]`. The dossier's suspect was UE3 re-creating its device
objects onto a vtable the patch no longer covered.

**What `/gr` found** (drop `2026-09-04-gr-slot-94-dies-because-someone-records-a-state-block-after-reset.md`):
the suspect does not fit — D3D9 vtables are shared per runtime class, a second `CreateDevice`
would have been logged by our own hook, and slot 17 in the *same table* kept working. Two
independent public witnesses (DxWnd's author, 2014; a D3D8-era newsgroup answer) describe the
runtime **restoring its own method pointers into the vtable on `BeginStateBlock`/`EndStateBlock`**:
recording mode swaps the state-*setting* methods and puts the originals back afterwards. Slot 94
is a state-setting method; `Present` and `Reset` are not. That is exactly the observed pattern.
`[reported]` in general, **`[hypothesis]` for this game** until a log line says so. UE3's own D3D9
RHI records no state blocks (public source, one search), so the caller would be another resident —
Steam overlay, driver overlay, anything on D3DX sprites/fonts — re-initialising after the reset.

**One thing I checked in our own code and can confirm:** the "not instantaneous, ~120–240 frames
later" claim in §9a was never supported. The stereo summary prints every `FrameInterval` frames
with counters that are *reset at each summary*, so a summary printed after the reset still carries
the pre-reset frames of its window. One healthy post-reset summary is expected **even if the slot
died inside `Reset` itself**. `[inferred-static 2026-09-04, from dllmain.cpp lines 423–443]`
The figure is withdrawn from the dossier; the new build stamps the moment to the frame.

**The build** (`staging/enslaved-vr/proxy-d3d9/dllmain.cpp`, `[compile-verified 2026-09-04]`,
`-Wall -Wextra` clean, 78,336 B, all 9 exports verified with `list-exports.ps1`):

- **Self-heal, every `Present`.** Five pointer compares (slots 94, 16, 17, 60, 61) against our
  functions. A slot that has reverted to **the runtime's original pointer** — the state-block-restore
  signature, and the only case where re-patching is unambiguously right — is re-patched and logged
  as `[rearm] present: slot 94 ... had REVERTED to the runtime's original ... -> re-patched`. A slot
  holding a **foreign** pointer (neither ours nor the original) is logged once per distinct value
  with its owning module and **left alone**: it could be a later hook that chains to us, and
  overwriting it would cut that hook out. `[hooks] Rearm=0` in the ini turns healing off and keeps
  the observation, for a run that wants to watch the death rather than prevent it.
- **`BeginStateBlock`/`EndStateBlock` (slots 60/61, verified from the SDK header's vtable struct)
  are hooked** to log frame, frames-since-Reset, the calling module and offset, and whether slot 94
  was still ours before Begin and after End. Re-arm runs right after End; never during recording.
- **`[reset] returned ... slot94=ours|NOT ours`** is logged the instant the runtime's `Reset`
  returns, before any re-arm. That single line separates "died inside Reset" from "died later".
- **`[liveness] frame N had ZERO SetVSConstF calls (previous frame: M)`** stamps the first five
  non-zero→zero transitions, independent of the vtable check — so if the mechanism is something the
  vtable compare cannot see (the engine switching to a different device object, say), the frame
  is still known.
- The stereo summary line gains `re-arms N, state blocks N, slot94=ours|NOT OURS`.

**Deployed** on the dev PC to `Enslaved\Binaries\Win32\d3d9.dll`; the previous build (73,728 B,
2026-09-03) is kept as `d3d9.dll.bak-2026-09-04-pre-rearm`. The deployed `d3d9_proxy.ini` was
**not** touched — it carries the live session's `Enabled=1`; the new key defaults to healing on.
⚠️ **The home PC — where the 2026-09-03d resets were observed — still runs the old build** until
that machine pulls `staging` and rebuilds (`build.ps1`, llvm-mingw i686, as on 2026-09-02).

**Fail-safe review.** The only new write to game-owned memory is the same `PatchVTableEntry` the
proxy has always used, on the same slots, gated on an exact pointer compare. The hot path gains one
`InterlockedIncrement` per constant upload. Present gains five compares. `ModuleNameOf` is only
called on state-block events and on a first-seen foreign pointer. Nothing here can make a frame
fail that would have succeeded before.

**NOT established:** that state blocks are the rewriter in this process, that the log will show a
`[stateblock]` line at all, or that re-patching restores a *working* stereo (it restores the
*calls*; if the hook is reached the stereo maths is unchanged and already measured correct).

## 2. "Exec dispatch stripped" was a hypothesis wearing a `[verified-live]` tag

Drop `2026-09-04-gr-exec-dispatch-stripped-is-a-hypothesis-not-a-verified-negative.md` carries a
`Supersedes:` header for dossier §7's "COHERENT READING" and is folded in as a correction:

- **F9=`shot`** is bound only inside `[NTGameFramework.NTCam_DebugInput]` — the debug camera
  controller's own input class, which does not exist in normal play. I re-read the live ini on this
  machine: `[NTGameFramework.NTCam_DebugInput]` spans lines 129–183 and the F9 line is 158, inside
  it `[inferred-static 2026-09-04, n=1 file]`. So "F9 does not depend on our edit" was true and
  irrelevant: **that test could never have produced a positive.**
- **F5=`ToggleDebugCamera`** is a `GameCheatManager` exec; a CheatManager exists only if
  `PlayerController.AddCheats()` ran, gated on `GameInfo.AllowCheats()`. With dispatch fully alive,
  the bound-command chain returns false silently when no object owns the name. The pad chord ends
  at the same missing object.
- **F6=`FOV 120`** is a one-shot setter the game's own chase camera can overwrite each tick.

The census I ran on the shipped files adds one small fact and one non-fact:
`Enslaved.exe` contains `GObjObjects` (×7 ASCII), `ProcessEvent` and `CheatManager`/`ConsoleCommand`
(UTF-16) `[measured 2026-09-04]` — the anchors the in-process route needs are in the binary. It does
**not** contain `ToggleDebugCamera`, `AddCheats` or `AllowCheats` — **which is expected, not
evidence**: those are script-side names living in cooked packages whose name tables are compressed
(`Engine.u` shows `AddCheats` once in an uncompressed span; `GameFramework.u` shows nothing, and
nothing is what a compressed package shows). The "is `CheatClass` still a real class" unknown stays
open.

**The dossier now reads:** the exec channel is unreachable by the routes tried, none of which is yet
a valid negative. The one-key `[FLAT]` re-test from the drop is queued: bind `Pause` (an unguarded
`PlayerController` exec that needs no CheatManager and visibly freezes the world) in **both**
`[Engine.PlayerInput]` and `[MonkeyGame.MKInput]` of the Documents copy of `MonkeyInput.ini`, plus
the community `FOV` line verbatim. Pauses ⇒ dispatch is alive and both in-process rows become
"construct a CheatManager". Does not pause in either ⇒ the first valid negative.

## 3. The in-process route has a shape now, and a proof that the debug systems ship

Drop `2026-09-04-gr-dron3-opened-the-pc-debug-menu-with-a-dll-patch.md`: a `dinput8.dll` patch
opened this game's **PC debug menu** in 2020 (Backspace+Escape during play), and on PS3 a single
`li r3,0` enables both the debug menu and the debug camera — the shape of a defeated
"debug allowed" predicate. `[reported 2026-09-04]` The dossier's 2026-08-24 "no camera hack exists"
is `[disproved 2026-09-04]` for the menu. So the two in-process rows are not "find the exec
dispatcher by pattern" — the dispatcher is a chain of `ScriptConsoleExec` calls, not a function —
but either **(A) defeat the gate** (`AllowCheats` or Ninja Theory's override behind
`CheckDebugCamChord`/`DoDebugCamChord`), or **(B) call script functions directly through
`UObject::ProcessEvent`** after pattern-finding `GObjects`/`GNames` — the public, MIT-licensed UE3
SDK-generator recipe, which also restores the whole command vocabulary via
`ProcessEvent(PC, ConsoleCommand, "...")`. Route (B) is static work with the anchors above and is
now the single `[PD]` row on this project.

## 4. What the next launch answers

One ordinary launch on either PC with the new build, play to a checkpoint, **restart the checkpoint**
(the incidental reset of 2026-09-03d), play thirty more seconds, quit. Read `d3d9_proxy_log.txt`:

| Line | Meaning |
| --- | --- |
| `[reset] returned ... slot94=NOT ours` | the slot died **inside** Reset; the "later" story is wrong |
| `[reset] returned ... slot94=ours` then `[stateblock] End #n ... slot94 after End=NOT ours` | **the state-block hypothesis is confirmed**, and the `from <module>` field names the resident that records it |
| `[rearm] ... -> re-patched` followed by a summary with `offset` > 0 and `slot94=ours` | **the stereo survives a Reset** — the operational rule "read `offset` before trusting anything" can be relaxed to "check the summary says `slot94=ours`" |
| `[rearm] ... FOREIGN pointer ... (<module>)` | something other than the runtime took the slot and does not chain to us; the module name is the next question, and the proxy deliberately did not fight it |
| no `[stateblock]` lines, no `[rearm]` lines, but `[liveness]` shows uploads stopping | the vtable is intact and the calls still stop: the engine moved to another device object or another path — a different investigation, and the vtable theory is `[disproved]` |
