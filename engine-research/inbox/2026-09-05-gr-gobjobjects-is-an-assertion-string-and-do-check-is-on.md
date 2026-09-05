Supersedes: `enslaved-vr/external-research/topics/2026-09-04-the-debug-menu-ships-in-the-pc-build-and-a-dll-patch-opens-it.md`, the claim that the UE3 SDK generators "ship patterns and document the offsets route"

# `GObjObjects` is an assertion string, `DO_CHECK` is on — and the generators ship no patterns

**Filed by `/gr`, 2026-09-05 (estate sweep). For the modding lane.** No launch; public source only.
Full write-up:
`external-research/topics/2026-09-05-the-generators-ship-no-patterns-but-gobjobjects-is-an-assertion-string.md`.

## 1. ❌ Half of the `[PD]` row's method is not available

The row's deliverable is *"the two addresses + the `ProcessEvent` slot, cross-checked two ways
(string xref and the SDK-generator signature)"*. **There is no SDK-generator signature to check
against.** `ItsBranK/UE3SDKGenerator`'s `Engine/Template/Configuration.cpp` ships
`GObjectsPattern`, `GObjectsMask`, `GNamesPattern`, `GNamesMask`, `ProcessEventPattern` and
`ProcessEventMask` all set to the literal string `"null"`, with the offsets `NULL` and
`ProcessEventIndex` `-1` `[verified-live 2026-09-05, n=1 API read]`. It ships a `FindPattern`
scanner and a slot to put *your* pattern in; the pattern is per-game and is the thing you have to
find. My 2026-09-04 wording — "both generators ship patterns" — was wrong, and this file is the
correction.

Substitute cross-checks, since the row rightly wants two: **(a)** two *different* assertion sites
naming the array should xref to code touching the **same** address — free, once you have the first;
**(b)** shape-validate it — `GObjObjects` is a `TArray<UObject*>`, so 32-bit UE3 gives
`{ void* Data; INT ArrayNum; INT ArrayMax; }` and a live read should show a heap pointer with
`0 < ArrayNum <= ArrayMax` and element 0 dereferencing to an object whose vtable is in-module (the
planned "log the object count and the `PlayerController` name" already does this).

## 2. ⭐ Why `GObjObjects` ×7 is in the binary — and why that is good news

`GObjObjects` is **never a string literal in UE3 source.** Every occurrence across the public mirror
is ordinary code, and the `debugf` messages beside it say "NULL object", "Invalid object index %i",
"Empty slot" — none name the array.

It gets there through the assertion macro (`Development/Src/Core/Inc/UnFile.h`)
`[reported 2026-09-05, from source]`:

```
#define check(expr)  { if(!(expr)) appFailAssert( #expr, __FILE__, __LINE__ ); … }
```

`#expr` stringifies the asserted expression. Sites naming the array in the published source:
`check( GObjObjects.Num() == 0 )` and `check(GObjObjects(InIndex)==NULL)` in `UnObj.cpp`,
`check( GObjObjects.IsValidIndex( CurObjectIndex ) )` in `UnObjGC.cpp`. Ninja Theory's 2010 branch
will differ in detail, and inlining duplicates sites, so **seven copies is consistent with a handful
of distinct assertions**.

**Three things follow, all of which make your row cheaper:**

1. **The xref lands exactly where you want it.** `appFailAssert` is called from *inside* the function
   containing the assertion, and that function tests `GObjObjects` in the immediately preceding
   instructions — so the global appears there as a **direct memory operand**. That is the address,
   not merely a hint towards it. `[inferred-static 2026-09-05]`
2. **`__FILE__` is a free confirmation beside every hit.** The same call passes the source path, so
   the string pool near a `GObjObjects…` literal should hold something like
   `…\Development\Src\Core\Src\UnObj.cpp`. That distinguishes a real hit from a coincidence **and**
   tells you which assertion you are standing in — plus the studio's source layout, reusable for
   every later hunt in this binary.
3. **`DO_CHECK` was left ON in a retail build.** Seven copies prove it. That generalises well beyond
   this symbol: *every* `check()` in the engine and the game contributes a stringified expression
   naming the variables it guards, each an xref to the code that touches them. `GNames`,
   `ProcessEvent`'s neighbourhood, and the `AllowCheats` / `CheatManager` gate route (A) wants to
   defeat are all plausible beneficiaries. **Before hand-building a byte signature for anything in
   `Enslaved.exe`, grep the strings for the symbol name first.**

## Suggested dossier change

Where §10 (or wherever route (B) is recorded) describes the SDK-generator recipe, note that the
generators supply the harness and not the patterns, and record the assertion-string mechanism as the
primary locator with the `__FILE__` neighbour as its confirmation. Add a general line that this build
ships with `DO_CHECK` enabled, so assertion strings are a navigational resource for the whole binary
— that is worth more than the `GObjObjects` hunt on its own.

The engine-agnostic form of point 3 has been filed to `flat-to-vr-cross-engine-research/inbox/` for
`/sr`; it is not duplicated in my own topics.

Credit: **ItsBranK** (UE3SDKGenerator, MIT — read online, nothing copied) and **CodeRedModding**
(public UE3 source mirror; the engine source is Epic Games').
