# The debug menu ships in the PC build, and dron_3 opened it with a `dinput8.dll` patch — the in-process route is a gate to defeat, not a dispatcher to find

**Date:** 2026-09-04 · **Status:** 🆕 new · **Answers:** the board's `[PD]` rows *"THE COMMAND
CHANNEL, NEXT BEST ROUTE: in-process exec from our own proxy"* and *"THE ONLY ROUTE LEFT TO A FREE
CAMERA IS IN-PROCESS"*

## The finding

**dron_3** — a debug-menu specialist with a long public record of re-enabling shipped debug UIs on
PS3 and PC — published, on **2020-11-02**, a working debug menu for the **PC** version of this
game: drop a `dinput8.dll` into `Binaries\Win32\`, then *"during the game press BACKSPACE + ESCAPE
on keyboard, BACK + START or SELECT + START on gamepad."* `[reported 2026-09-04]` The companion
PS3 post (2017-03-08, BLES00989 v1.01) enables *"Debug Menu (SELECT+START) and Debug Camera
(L3+R3)"* with a **single-instruction patch**, `0150BB34 38600000` — PowerPC `li r3,0`, i.e. one
function forced to return zero. `[reported]`

Three things follow, and they are the point:

1. **The debug systems are compiled into the shipped game**, PC included — menu, and on PS3 the
   L3+R3 debug camera we have been chasing. Nothing was "stripped" that a one-instruction patch
   could bring back; it was *gated*.
2. **The gate is a check, and the shape of the check is "return zero".** On PS3 that is enough for
   both the menu chord and the camera chord to start working — consistent with a single
   "debug/cheats allowed" predicate rather than with a removed dispatcher (see the companion topic:
   UE3's `AllowCheats` gate has exactly that shape).
3. **The PC route is in-process, from a proxy DLL** — the same seat our `d3d9.dll` already
   occupies. dron_3 chose `dinput8.dll` because it is the conventional loader host; the mechanism
   inside is what matters, and our proxy can carry the equivalent.

Nothing from dron_3's package was downloaded or examined (standing rule). What he demonstrates is
*that* the menu is reachable from inside the process; *how* is ours to work out, and the two
options below both stay `[PD]`.

## Option A — defeat the gate, as dron_3 did

Find the predicate that decides whether debug input is honoured and make it true. Candidates, from
the UE3 source structure and this game's config, in the order to try:

- **The cheats gate.** `GameInfo.AllowCheats(PlayerController)` (or Ninja Theory's override of it)
  decides whether `PlayerController.AddCheats()` constructs the `GameCheatManager` that owns
  `ToggleDebugCamera`. Patch it to return true, or call `AddCheats(bForce=true)` directly (Option
  B). With a CheatManager present, the stock chord, `Alt+C`, and a bound `ToggleDebugCamera` all
  have an owner again.
- **A debug-input gate specific to this game.** The `[Engine.PlayerInput]` chord bindings
  (`CheckDebugCamChord`/`DoDebugCamChord`) and the `[NTGameFramework.NTCam_DebugInput]` map show
  Ninja Theory routed the camera through their own input class. The PC menu's BACKSPACE+ESCAPE /
  BACK+START chord is the same family. The strings for those exec names are in the executable (the
  dossier records debug strings intact) and are the natural anchors for finding the function that
  checks whether they are allowed to act.

The pattern search is static, on the unpacked 32-bit image the dossier already describes.

## Option B — call the script functions directly, the SDK-generator way

Public tooling for 32-bit UE3 titles of this era has settled the recipe for calling UnrealScript
functions from inside the process without any console or binding:

- Locate **`GObjects`** and **`GNames`** by byte pattern (both generators below ship patterns and
  document the offsets route); walk `GObjects` to find the live `PlayerController` instance and the
  `UFunction` objects by name (`AddCheats`, `ToggleDebugCamera`, `FOV`, `Pause`).
- Invoke through **`UObject::ProcessEvent`** — a virtual on every `UObject`, by vtable index or
  pattern — with a parameter block laid out per the function's properties.

Prior art, all MIT-licensed, all read online and nothing copied: **ItsBranK's UE3SDKGenerator**
(*"offsets or patterns for GObjects and GNames"*, *"virtual voids for Process Event, or just use an
index number for UObject's VfTable"*, *"full support for both x32 bit and x64 bit games"*), the
**CodeRed Generator** (same lineage, modernised), and **TheFeckless's original UE3 SDK Generator**
they both descend from. `[reported]`

The sequence that yields the free camera with no gate patch at all: `ProcessEvent(PC, AddCheats,
{bForce=true})` — a plain script function, not FINAL_RELEASE-guarded — then
`ProcessEvent(PC.CheatManager, ToggleDebugCamera, {bDrawDebugText=false})`. It also restores the
whole command vocabulary the board wants ("exec from our own proxy"): `ProcessEvent(PC,
ConsoleCommand, {Command="…"})` is the engine's own entry point for a command string, and it is the
same `ULocalPlayer::Exec` chain the console would have used. `[inferred-static]` from the public
source; whether Ninja Theory kept `CheatClass` pointing at a real class is the one thing that
could make Option A necessary after all.

## Why this beats "locate the engine's exec entry point by pattern"

The exec entry point is not one function — it is a chain of eight `ScriptConsoleExec` calls across
different objects (`UnPlayer.cpp:2923–2954`), and calling into the middle of it by pattern buys
nothing that `ProcessEvent` on the right object does not buy more cheaply and more legibly. The
generators exist because the community reached the same conclusion a decade ago.

## Two smaller notes for the record

- **vorpX ships a geometry-3D profile for this game** (RJK_, 2019-05-12: *"Good S3D in all modes"*,
  *"Full VR with Headtracking"*, cinema modes recommended *"because mouse/camera issues"*, FOV via
  `FOVAngle` in `MonkeyEngine.ini`). `[reported]` Independent corroboration that the projection is
  interceptable per draw on this build, which the 2026-08-24 topic's "no public stereo work"
  reading did not have; it says nothing about *where* the matrix is, which our own `c0` result
  already settled.
- The 2026-08-24 topic's "no camera hack exists" is now `[disproved 2026-09-04]` for the debug menu
  and, on PS3, for the debug camera; the PC camera chord specifically remains untested by anyone
  public that this lane could find.

## Sources

- [dron_3 — "Enslaved: Odyssey to the West - PC - Debug Menu" (2020-11-02)](https://dron-3.blogspot.com/2020/11/enslaved-odyssey-to-west-pc-debug-menu.html)
  and the [video of the same title](https://www.youtube.com/watch?v=0Y-m8PBA7uc).
- [dron_3 — Enslaved PS3 debug menu and debug camera (2017-03-08)](https://dron-3.blogspot.com/2017/03/enslaved-odyssey-to-west.html).
- [ItsBranK/UE3SDKGenerator](https://github.com/ItsBranK/UE3SDKGenerator) ·
  [CodeRedModding/CodeRed-Generator](https://github.com/CodeRedModding/CodeRed-Generator/) —
  the GObjects/GNames/ProcessEvent recipe for UE3.
- [CodeRedModding/UnrealEngine3 (public UE3 source mirror)](https://github.com/CodeRedModding/UnrealEngine3)
  — `GameCheatManager.uc`, `PlayerController.uc` (`AddCheats`, `ConsoleCommand`), `UnPlayer.cpp`.
- [vorpX forum — Enslaved: Odyssey to the West profile (RJK_, 2019)](https://www.vorpx.com/forums/topic/enslaved-odyssey-to-the-west/).
