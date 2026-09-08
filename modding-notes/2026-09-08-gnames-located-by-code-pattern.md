# `GNames` is located: `0x0242B954`, by code pattern, four ways

`/pd`, dev PC, 2026-09-08. **The game was not launched. Nothing here has been run.**

Tool: `dev-archive/tools/find_gnames.py` (new, read-only). Evidence:
`dev-archive/recon/2026-09-08-gnames-located/find_gnames-output.txt`.

## The result

> **`&GNames = 0x0242B954`** `[inferred-static 2026-09-08]`
> so `GNames.Data = 0x0242B954`, `.ArrayNum = 0x0242B958`, `.ArrayMax = 0x0242B95C`

Four independent signals agree, and none of them is "it has the right name":

**1. The published UT3 signature matches exactly, from four call sites.**
`8B 0D ?? ?? ?? ?? 83 3C 81 00 74` — `mov ecx,[imm32]` / `cmp dword ptr [ecx+eax*4],0` / `jz`, the
engine asking *"is name slot `Index` empty?"*. It is the **identical** pattern used for UT3, APB:
Reloaded, Tribes: Ascend and Hawken in `polivilas/UnrealEngineSDKGenerator` `[reported 2026-09-07]`.
It hits at `0x00594368`, `0x006777FE`, `0x00677A24`, `0x00679D0E` — and **all four resolve to the
same address**.

**2. The adjacency prediction lands on the nose.** `/gr` gave two published UE3 pairs where `GNames`
sits **below** `GObjects` by under `0x50`: Borderlands 1 by `0x30`, Rocket League by `0x48`. Ours is
`0x0242B984 − 0x0242B954` = **exactly `0x30`**, the Borderlands figure.

**3. It is in `.data`, which is the only writable section**, as a mutable global must be.

**4. The usage gradient matches a `TArray` — and this one was not predicted, it fell out.** Counting
absolute-load sites for the three consecutive words:

| address | field | load sites |
| --- | --- | --- |
| `0x0242B954` | `Data` | **26** |
| `0x0242B958` | `ArrayNum` | **12** |
| `0x0242B95C` | `ArrayMax` | **1** |

Exactly the descending frequency a `{Data, ArrayNum, ArrayMax}` triple produces: the buffer is read
constantly, the count often, the capacity almost never. A coincidental address would have no reason
to show that shape.

## Why searching for the name could never have worked

The 2026-09-07 scan found **no `GNames` string in either encoding**, and that was recorded as a wall.
It is not an anomaly — **no public UE3 locator searches for a `GNames` string or symbol**; all six
working ones, across six games and two independent codebases, scan for the code shape above
`[reported 2026-09-07]`. `GNames` is the SDK-generator community's name for the global, not
necessarily the engine's.

So the blocker was a method problem, not a missing thing. The `/gr` drop that said so is what turned
this from "needs a different locator" into a fifteen-minute scan.

## ⚠️ What this does NOT establish

**It is not confirmed, and the confirmation is runtime-only.** The validator is: treat the candidate
as `TArray<FNameEntry*>`, read `Data[0]`, follow it, read its characters at `+0x10`, and **require
`"None"`**. `FNameEntry` objects are **heap-allocated at startup** from the compiled-in
`REGISTER_NAME` table, so `None` and `ByteProperty` are **not in `Enslaved.exe` on disk** — no static
check can close this.

Four agreeing signals make it a strong candidate. They do not make it verified, and the tag says so.

## Also folded from the inbox

- **`ProcessEvent`'s vtable index is not stable** — APB 60, Rocket League 67 — so it must be found
  per game and no public table exists. `unrealsdk` avoids the index entirely by scanning
  `ProcessEvent`'s **prologue** and detouring it. That is now the recommended route for the other
  half of the row. `[reported 2026-09-07]`
- **A §9c claim of ours was too broad.** We recorded that the UE3 SDK generators *"ship a
  `FindPattern` harness with every pattern set to the literal string `null`"*. True of
  `UE3SDKGenerator` and `CodeRed`; **false of the family** — `polivilas/UnrealEngineSDKGenerator`
  ships real filled-in signatures for six games, and it is the one that just worked. Narrowed in the
  dossier.
- **⚠️ Helix Mod's 3D Vision fix for Enslaved is itself a `d3d9.dll` wrapper** in `Binaries\Win32\`
  `[reported 2026-09-07]`. Two consequences, and neither was written down: it is independent evidence
  that `d3d9` proxying is the right seam on this game, **and it occupies the exact slot our proxy
  uses**, so the two cannot both be installed. Worth knowing before anyone tries them together to
  compare.

## The one live check

Read `0x0242B954` as a `TArray<FNameEntry*>`: require `0 < ArrayNum <= ArrayMax` with `ArrayNum` in
the tens of thousands, then follow `Data[0]` and read `+0x10`.

| what you see | what it means |
| --- | --- |
| the string **`None`** | **`GNames` is confirmed** and route (B) has both globals |
| a plausible array but a different first name | still very likely `GNames`; the early-name order differs between engine generations, so check `Data[1..8]` for identifiers ending in `Property` |
| garbage or `ArrayNum == 0` | wrong candidate — the ranked shortlist in the tool's output is the next thing to try, and `0x0242B950` (34 sites) is the strongest runner-up |

The proxy stub that does this is already the next `[PD]` row on the board, and it now has a second
address to validate in the same pass.
