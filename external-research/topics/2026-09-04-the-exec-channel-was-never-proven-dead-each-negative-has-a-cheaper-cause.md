# The exec channel was never proven dead — each of the three negatives has a cheaper cause, and one of them could not have produced a positive

**Date:** 2026-09-04 · **Status:** 🆕 new · **Answers:** ENGINE-DOSSIER.md §7's *"this build kept
its input/action bindings and STRIPPED ITS EXEC DISPATCH"* and the board's two `[PD]` rows that
rest on it (*"locate the engine's exec entry point by pattern"*)

## What the dossier concluded, and what it rests on

§7, 2026-09-03b, `[verified-live 2026-09-03, n=3 commands]`: F9=`shot` wrote no file, F6=`FOV 120`
changed no framing, F5=`ToggleDebugCamera` did nothing; therefore *"exec dispatch is stripped"*,
and by extension (03c) *"the debug camera is unreachable by ANY input route"*. The two in-process
`[PD]` rows then set out to find "the engine's exec entry point" in a 34 MB executable.

Reading the shipped config and the public UE3 source against each test, **none of the three
negatives requires a stripped dispatcher**, and the one the notes call *"the cheapest and most
decisive single test"* was placed where it could never fire. This does not prove the channel is
alive — it moves the claim from `[verified-live]` to `[hypothesis]`, and it names a one-launch
re-test that actually can settle it.

## 1. F9 = `shot` lives in the debug camera's own input class, which only exists inside the debug camera

In the live `MonkeyInput.ini` (the `Documents\My Games\…` copy this machine plays from), the
`Bindings=(Name="F9",Command="shot")` line sits at line 143 — **inside the
`[NTGameFramework.NTCam_DebugInput]` section that starts at line 114 and ends at 169**, next to
`Alt+C`→`ToggleDebugCamera` and the WASD fly keys. `[inferred-static 2026-09-04, read from the
shipped config]` `NTCam_DebugInput` is the input object the *debug camera controller* uses; in
normal play the live input object is the game's own class (the ini has an `[NTGameFramework.NTInput]`
section, and the game-folder copy also an `[MonkeyGame.MKInput]` one), which never reads that
section. So **F9 was not bound in normal gameplay at all.** The notes' premise — *"F9 does not
depend on our edit, so the test could have produced a positive"* — is inverted: it is the one test
that could not. The same applies to the UDK's own comment that `Alt+C` toggles the camera *off* from
inside it.

## 2. F5 = `ToggleDebugCamera` needs a CheatManager object, which a shipped game normally never creates

From the public UE3 source (read online, nothing taken):

- `ToggleDebugCamera` is `exec function ToggleDebugCamera(optional bool bDrawDebugText)` on
  **`GameFramework.GameCheatManager`**, not on the player controller
  (`GameCheatManager.uc:37`). `[inferred-static]`
- A CheatManager exists only if `PlayerController.AddCheats()` constructed one, and `AddCheats`
  does so only when `WorldInfo.Game.AllowCheats(self)` returns true (or it is called with
  `bForce`). Stock `GameInfo.AllowCheats` returns `NetMode == NM_Standalone`, but it is a plain
  script function any licensee overrides — and the `EnableCheats` exec that forces it is wrapped in
  `` `if(`notdefined(FINAL_RELEASE)) `` (`PlayerController.uc:1289–1305`). `[inferred-static]`
- The engine's exec dispatch for a bound command walks, in order: `PlayerInput` →
  `PlayerController` → `Pawn` → `InvManager` → `Weapon` → `HUD` → `GameInfo` → **`CheatManager`
  last, and only if non-null** (`UnPlayer.cpp:2923–2954`). A command that no object in that chain
  owns simply returns false — **silently, with the dispatcher fully alive**.

So F5 doing nothing is what a shipped UE3 game looks like when `AllowCheats` is false: the command
is dispatched, finds no owner, and drops. The thumbstick chord (03c) ends in the same place — its
`CheckDebugCamChord`/`DoDebugCamChord` are the developers' own execs whose job is to reach
`ToggleDebugCamera`, and they fail for the same missing object. dron_3's PS3 patch (see the
companion topic) is a single instruction that makes one function return zero — the shape of a
defeated "cheats allowed" gate, not of a rebuilt dispatcher.

## 3. F6 = `FOV 120` reaches a setter the game's own camera may overwrite every frame

`PlayerController.FOV(float F)` is an ordinary, unguarded exec (`PlayerController.uc:2472`) that
calls `PlayerCamera.SetFOV(F)`. Ninja Theory ships its own camera system (`MonkeyChaseCamera.ini`,
with per-mode distances and FOVs), and a camera that writes its FOV each tick from its own data
leaves nothing for a one-shot `SetFOV` to show — the exec runs, the frame does not change.
`[hypothesis]` — but the community's own FOV recipe for this game is *this very binding*,
`Bindings=(Name="F1",Command="FOV 0")` under `[MonkeyGame.MKInput]` (dossier §10a; WSGF and Steam
threads), reported to work. Either that report is wrong, or F6's silence is about *where* the
binding sat or *what value* it sent, not about dispatch.

## 4. And the section question

The 2026-09-03 test bindings were added to `[Engine.PlayerInput]`. That is the base class's section;
the community recipe uses `[MonkeyGame.MKInput]`, a section that exists in the game-folder
`MonkeyGame\Config\MonkeyInput.ini` (line 389) but **not in the Documents copy the game loads**.
Whether `[Engine.PlayerInput]` additions are inherited by the live `NTInput`/`MKInput` object, or
whether that class's own section replaces the `Bindings` array, is a UE3 config-inheritance detail
this lane could not pin from documentation (the UDN pages are gone). It does not need pinning: the
re-test below puts the same line in both sections.

## The re-test that can actually settle it — one launch, `[FLAT]`

Bind, in **both** `[Engine.PlayerInput]` and a new `[MonkeyGame.MKInput]` section of the Documents
copy, a command that (a) lives on the player controller itself, (b) is not FINAL_RELEASE-guarded,
(c) needs no CheatManager, and (d) has an effect nothing else can mask:

- **`Pause`** — `exec function Pause()` → `ServerPause()` → `SetPause` (`PlayerController.uc:4080`);
  the world freezes. Unmistakable, harmless, reversible with a second press.
- As a second witness, the community's `FOV 0` line exactly as published, to check §10a's report.

Outcomes: the game pauses → the exec channel is alive and §7 is `[disproved]`; both `[PD]` rows
change from "find the exec dispatcher" to "get a CheatManager constructed" (companion topic).
Nothing pauses, in either section → the stripped-dispatch reading gains its first *valid*
negative, and the in-process route stands. Either way the six-key budget is not exceeded: this is
one key, chosen for the property the earlier three lacked.

## Sources

- The live `MonkeyInput.ini` on the home PC (`Documents\My Games\UnrealEngine3\MonkeyGame\Config\`)
  and the game-folder copy — read only, section layout and line numbers as cited.
- [CodeRedModding/UnrealEngine3 — public UE3 source mirror](https://github.com/CodeRedModding/UnrealEngine3):
  `Development/Src/GameFramework/Classes/GameCheatManager.uc`,
  `Development/Src/Engine/Classes/PlayerController.uc`, `…/GameInfo.uc`,
  `Development/Src/Engine/Src/UnPlayer.cpp`, `…/UnIn.cpp` (`UInput::ExecInputCommands`). Read
  online; nothing copied.
- [UDK DebugCameraController.uc (snorrewb/IMT3601 mirror)](https://github.com/snorrewb/IMT3601/blob/master/UDK/Development/Src/GameFramework/Classes/DebugCameraController.uc)
  — the header comment on Alt+C / both-analog activation.
- [WSGF — Enslaved 2013 manual PLP instructions (imusrt, 2015)](https://www.wsgf.org/blog/imusrt/2015/04/18/enslaved-odyssey-west-2013-manual-plp-instructions)
  and the [Steam "Changing FOV value?" thread](https://steamcommunity.com/app/245280/discussions/0/487877107141205916/)
  — the `[MonkeyGame.MKInput]` FOV-binding recipe.
- Our own `modding-notes/2026-09-03*.md` and ENGINE-DOSSIER.md §7 — the claims re-examined.
