Supersedes: `enslaved-vr/external-research/topics/2026-09-04-the-debug-menu-ships-in-the-pc-build-and-a-dll-patch-opens-it.md`, the claim that the SDK generators "ship patterns and document the offsets route"

# The generators ship no patterns — but `GObjObjects` is an **assertion string**, and that is better

**Status:** 🆕 new · **Priority:** high — it corrects one half of the `[PD]` row's stated method and
substantially strengthens the other half, which is the one that will actually be used.

## The row this is about

> **`[PD]` THE IN-PROCESS ROUTE, ROUTE (B): pattern-find `GObjects`/`GNames`/`ProcessEvent` in
> `Enslaved.exe` statically.** […] Deliverable: the two addresses + the `ProcessEvent` slot,
> **cross-checked two ways (string xref and the SDK-generator signature)**.

Two routes are named. One of them does not exist off the shelf; the other is stronger than the row
knows.

## ❌ Correction: neither generator ships a pattern for `GObjects` or `GNames`

The 2026-09-04 topic says of ItsBranK's UE3SDKGenerator and CodeRed Generator that *"both generators
below ship patterns and document the offsets route"*. Read directly
`[verified-live 2026-09-05, n=1 API read]`, `UE3SDKGenerator`'s
`Engine/Template/Configuration.cpp` ships **placeholders, not patterns** — `GObjectsPattern`,
`GObjectsMask`, `GNamesPattern`, `GNamesMask`, `ProcessEventPattern` and `ProcessEventMask` are all
literally `"null"`, with `GObjectsOffset`/`GNamesOffset` `NULL` and `ProcessEventIndex` `-1`.

What the generator ships is the **harness**: a `FindPattern(HMODULE, pattern, mask)` scanner, a
config slot to put your pattern in, and a `UsingOffsets` switch to use hardcoded addresses instead.
`dllmain.cpp` calls `Utils::FindPattern` with whatever the config holds. The `GObjectsString`
alongside each pattern is not a second locator — it is the printable form written into the generated
SDK header.

So the pattern is **per-game and must be found first**. The generator is what you use *after* you
have the addresses, not a way to get them. The row's "cross-check two ways" therefore has one
off-the-shelf way, not two — and the remaining cross-check has to be built (see the last section).

MIT-licensed, read online, nothing copied. Credit: **ItsBranK**.

## ⭐ The better half: why `GObjObjects` is in the binary at all

The board records, `[measured 2026-09-04]`, that `Enslaved.exe` contains **`GObjObjects` ×7 as
ASCII**. That is a striking fact once you check the source, because **`GObjObjects` is never a string
literal in UE3.** Read across the public UE3 mirror, every occurrence is ordinary code — a
declaration (`TArray<UObject*> UObject::GObjObjects;`), indexing, `.Num()` calls. The nearby
`debugf` messages say *"NULL object"*, *"Invalid object index %i"*, *"Empty slot"* — none of them
name the array.

**It gets there through the assertion macro.** From `Development/Src/Core/Inc/UnFile.h`
`[reported 2026-09-05, from source]`:

- `#define check(expr) { if(!(expr)) appFailAssert( #expr, __FILE__, __LINE__ ); … }`
- `verify(expr)` is the same shape; `checkMsg`, `checkFunc`, `checkf` likewise stringify `#expr`.

`#expr` is the preprocessor stringification operator, so **the text of the asserted expression
becomes a string literal in the binary** — and only when `DO_CHECK` is on. Assertions naming the
array in the published source:

| site | expression, as it would appear as a string |
| --- | --- |
| `UnObj.cpp` | `GObjObjects.Num() == 0` |
| `UnObj.cpp` | `GObjObjects(InIndex)==NULL` |
| `UnObjGC.cpp` | `GObjObjects.IsValidIndex( CurObjectIndex )` |

Ninja Theory's 2010 branch will differ in detail, and inlined templates can duplicate a site, so
seven copies is entirely consistent with a handful of distinct assertions.

### Three consequences, all of which make the `[PD]` row cheaper

**(1) The xref lands exactly where you want it.** `appFailAssert(#expr, __FILE__, __LINE__)` is
called from **inside the function containing the assertion**, and that function tests `GObjObjects`
in the immediately preceding instructions. So an xref from the string to its use site puts you in a
basic block that accesses the global **directly, as a memory operand** — which is the address the row
is looking for. This is not "a string that happens to mention it"; it is a labelled pointer to the
access itself. `[inferred-static 2026-09-05]`

**(2) There is a free confirmation signal beside every hit: `__FILE__`.** The same call passes the
source path, so the string pool near a `GObjObjects…` literal should contain something like
`…\Development\Src\Core\Src\UnObj.cpp` or `…\UnObjGC.cpp`. Finding that pair **identifies which
assertion you are standing in**, and distinguishes a real hit from a coincidence at no cost. It also
tells you the studio's source layout, which is reusable for every later hunt in this binary.

**(3) `DO_CHECK` was left on in a retail build — treat that as a general resource.** Seven copies
prove Enslaved shipped with assertions compiled in. That is not just true of `GObjObjects`: **every**
`check()` in the engine and the game contributes a stringified expression naming the variables it
guards, each one an xref to the code that touches them. `GNames`, `ProcessEvent`'s neighbourhood, and
the `AllowCheats`/`CheatManager` gate that route (A) wants to defeat are all plausible beneficiaries.
Before hand-building a byte signature for anything in this binary, **grep the strings for the symbol
name first** — this build answers that question more often than a stripped retail build has any right
to.

## What to do about the missing second cross-check

The row wants two independent confirmations. With the generator's signature unavailable, the honest
substitutes, in order of cost:

1. **Two different assertion sites** naming `GObjObjects` should xref to code touching the **same**
   address. Two sites agreeing is a genuine independent check, and it costs nothing beyond the first.
2. **Shape-validate the address**: `GObjObjects` is a `TArray<UObject*>` — in 32-bit UE3 that is
   `{ void* Data; INT ArrayNum; INT ArrayMax; }`, so a live read should show a plausible heap
   pointer with `0 < ArrayNum <= ArrayMax`, and element 0 dereferencing to an object whose vtable
   sits in the module. The 2026-09-04 plan's "log the object count and the `PlayerController` name"
   already does this once running.
3. **`GNames` by the same trick** — it is `TArrayNoInit<FNameEntry*>` and appears in its own
   assertions; finding both globals by the same mechanism and having them land in the expected
   relative region of `.data` is a third weak-but-free agreement.

## Concrete next steps

1. Search `Enslaved.exe`'s strings for `GObjObjects`, and **for each hit look for a neighbouring
   `.cpp` path string**. Record which assertion each corresponds to.
2. Xref each hit; the calling function's direct memory operand on the tested array is the `GObjects`
   address. Require **two sites to agree** before recording it.
3. Repeat for `GNames`. Then `ProcessEvent` — the row already notes the string is present.
4. Only then reach for the generator, which is the consumer of these addresses, not their source.

## Sources

- https://github.com/ItsBranK/UE3SDKGenerator — **MIT**, `Engine/Template/Configuration.cpp` and
  `dllmain.cpp`, read via the GitHub API 2026-09-05. Nothing copied. Credit: **ItsBranK**.
- https://github.com/CodeRedModding/UnrealEngine3 — public UE3 source mirror:
  `Development/Src/Core/Inc/UnFile.h` (the `check`/`verify` macros),
  `Development/Src/Core/Inc/UnObjBas.h`, `Development/Src/Core/Src/UnObj.cpp`,
  `Development/Src/Core/Src/UnObjGC.cpp`. Credit: **CodeRedModding** for the mirror; the engine
  source is Epic Games'.
- This project's own
  `topics/2026-09-04-the-debug-menu-ships-in-the-pc-build-and-a-dll-patch-opens-it.md`, whose
  "ship patterns" wording this corrects, and the board's `[PD]` route-(B) row.
