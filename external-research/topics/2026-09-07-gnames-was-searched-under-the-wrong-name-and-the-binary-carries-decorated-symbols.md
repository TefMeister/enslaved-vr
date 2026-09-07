# `GNames` was searched under a name UE3 may not use — and this binary carries **decorated symbols**, which is a locator the scan has never tried

**Status:** 🆕 new · **Priority:** medium — **downgraded from high the same day.** This proposes two
in-house routes, both one command with the tool that already exists. Its companion topic
[*Public UE3 locators find `GNames` by code pattern*](2026-09-07b-public-ue3-locators-find-gnames-by-code-pattern-and-one-fork-ships-working-signatures.md)
found what the public toolchain actually does, and **those routes have six games behind them while
these have none.** Try them first; keep these as the cheap fallback.

> ⚠️ **Two things below need correcting in light of that topic — read this before acting.**
>
> 1. **"No `GNames` string" is the normal case, not an anomaly.** *No public UE3 tool searches for a
>    `GNames` symbol or string at all* — all six shipped locators are **code patterns** (an absolute
>    load followed by a scale-4 indexed read). So the negative that prompted this topic did not need
>    explaining; the wrong-token hypothesis below may still be true, but it is no longer needed to
>    explain anything.
> 2. **The decorated-symbol route has no public corroboration.** No public UE3 locator uses decorated
>    symbols. That does not make it wrong — this binary is unusually generous with debug residue
>    (`DO_CHECK` on, `__FILE__` intact, a decorated symbol present), which is precisely why tools
>    written for normal binaries would not rely on it — but it is **ours alone and unvalidated**, and
>    should be ranked below the byte-pattern and adjacency routes.
>
> ⭐ The companion topic's **adjacency probe** is the cheapest thing on either list: in two published
> UE3 games `GNames` sits **below** `GObjects` by 0x30 and 0x48, and we have `GObjObjects` to the byte.

## The row this is aimed at

The board, 2026-09-07:

> "`[PD]` **route (B), the remaining half: locate `GNames` and the `ProcessEvent` vtable slot.**
> `GObjObjects` is DONE. ⚠️ **`GNames` has no string in the binary in either encoding**
> `[measured 2026-09-07]`, so the assertion route does not reach it — it needs a different locator.
> Scan BOTH encodings."

And this lane owns the falsified prediction behind it: my 2026-09-05 topic said *"`GNames` by the
same trick — it is `TArrayNoInit<FNameEntry*>` and appears in its own assertions."* The measurement
says otherwise, and that half is now **`[disproved 2026-09-07]`**. The `GObjObjects` half worked and
closed most of the row.

## ⚠️ 1. The likely reason the scan found nothing: `GNames` may not be the symbol's name

The scan table records the token searched for as **`GNames`** — 0 ASCII, 0 UTF-16.

**`GNames` is the SDK-generator community's conventional name for the global, not necessarily UE3's
own identifier for it.** In UE3 the name table is commonly a **static member of `FName`** rather than
a free global — in which case the identifier appearing in an assertion string or a decorated symbol
is **`Names`**, qualified by its class, and the token `GNames` would never appear anywhere in the
binary no matter how much debug information survived.

If that is right, then *"the assertion route does not reach `GNames`"* is a conclusion drawn from
searching for the wrong string, and the assertion route may work perfectly. `[hypothesis 2026-09-07]`
— stated as a hypothesis because I have not confirmed UE3's exact identifier for this generation.

**The check is one command**, because `find_uobject_globals.py` already takes the symbols to scan for
on its command line (`usage: find_uobject_globals.py <path to exe> [symbol ...]`) — no code change:

```
python find_uobject_globals.py Enslaved.exe Names FName FNameEntry NameEntry appGetGName
```

A hit on `Names` with a neighbouring `.cpp` path is the same signature that worked for
`GObjObjects`; the tool's `__FILE__`-neighbour confirmation applies unchanged.

## ⭐⭐ 2. The stronger route, and it needs no guess about the name at all

This one is derived entirely from our own §9c, and it is the better idea because **it does not depend
on knowing what the symbol is called.**

§9c records, almost in passing:

> "The **7th occurrence is a decorated MSVC symbol** at `0x021C09BC`
> (`?GObjObjects@UObject@@0V?$TArray@PAVUObject@@VFDefaultAllocator@@@@A`), **not yet chased**."

That single line is worth more than it was given credit for. **This binary retains decorated MSVC
symbol names for private static members** — and decoration is *structural*, so it can be searched by
shape:

| fragment | what it matches |
| --- | --- |
| `@@0V?$TArray@` | every **private static** `TArray` **member of a class** |
| `@@3V?$TArray@` | every **namespace-scope global** `TArray` — see the access-code note below |
| `?$TArrayNoInit@` | every `TArrayNoInit` — a candidate type for the name table |
| `FNameEntry` | the element type of the name table, wherever it is mentioned |
| `@FName@@` | every member of class `FName` |

Decoding the recorded symbol confirms the shape: `?GObjObjects@UObject@@` is `UObject::GObjObjects`,
the `0` marks a **private static member**, and `V?$TArray@PAVUObject@@VFDefaultAllocator@@@@` is
`TArray<UObject*, FDefaultAllocator>`; the trailing `A` is normal (non-const, non-volatile) storage.

⚠️ **The access code matters, and searching only `0` would miss the case this is aimed at.** In MSVC
decoration the character after the qualified name encodes storage: **`0`/`1`/`2`** are private /
protected / public **static class members**, while **`3`** is a **namespace-scope variable**. So:

- if the name table is `FName::Names` (a class static) the symbol carries `0`, `1` or `2`;
- if it is a genuine free global — the `GNames` the SDK-generator community assumes — it carries
  **`3`**, and a scan for `@@0V?$TArray@` alone would **not** find it.

**Search all four codes.** The safest single fragment is the type itself — `?$TArray@` or
`?$TArrayNoInit@` — with the access code read off each hit afterwards rather than assumed. That also
sidesteps the question this whole topic is about, which is that we do not know which shape the global
takes.

**So a scan for `@@0V?$TArray@` enumerates every private static `TArray` in the executable — a small,
bounded set that the name table is almost certainly a member of, whatever it is called.** You would
then read the decoded type of each hit and pick the one whose element type is a name entry. That
turns "find a global whose name we are guessing at" into "read a short list and recognise one".

**None of these tokens has ever been scanned for.** A grep of the dossier and the tool for
`FNameEntry`, `TArrayNoInit`, `mangled` and `decorated` returns **only** the two existing mentions of
the word "decorated"/"undecorated" `[verified-numerically 2026-09-07]` — and that grep was capable of
positives, since it found those two. The scan table covers `GObjObjects`, `GObjAvailable`,
`ProcessEvent`, `CheatManager`, `ConsoleCommand`, `GNames`, `AddCheats`, `ToggleDebugCamera` and
`AllowCheats`, and nothing structural.

## 3. The same route is the cheapest lead on `ProcessEvent`'s vtable slot

The row's other half is the `ProcessEvent` vtable index. The scan already shows **`ProcessEvent`: 1
ASCII, 2 UTF-16** — and the one ASCII hit is unexplained. Given §9c's finding, a decorated symbol is a
strong candidate for what that ASCII occurrence is.

A decorated symbol for a virtual member function encodes its **class and full signature**, so if
`?ProcessEvent@UObject@@` is present it gives an exact address for the function, from which the
vtable index is a matter of finding that address inside `UObject`'s vtable — rather than a byte
signature that has to be built by hand. **Worth chasing before building any pattern**, which is
§9c's own consequence 3: *"before hand-building a byte signature for anything in this binary, grep
the strings for the symbol name first."*

## Why this was not obvious, and what it costs to be wrong

The 2026-09-07 execution did exactly what the 2026-09-05 topic asked and got a clean negative. The
negative is real *for the token it tested*. What makes it worth revisiting is that **a null result on
one identifier is not a null result on the object** — and this binary has already proved unusually
generous with debug residue (`DO_CHECK` left on, `__FILE__` paths intact, decorated symbols present),
so "there is nothing to find" is a weaker prior here than it would be in a stripped build.

If both routes above come back empty too, that is a **much stronger** negative than the current one,
and it would justify moving to the runtime route: with `GObjObjects` already known, take object 0,
read its `FName` index, and locate the table by finding the pointer array whose element at that index
resolves to the expected string. That is a live read rather than a static scan, so it belongs behind
the pause-menu blocker — which is why it is named here but not recommended first.

## The concrete next steps

Both are static, need no launch, and use the tool that already exists:

1. `python find_uobject_globals.py Enslaved.exe Names FName FNameEntry NameEntry appGetGName`
   — tests the wrong-token hypothesis directly.
2. `python find_uobject_globals.py Enslaved.exe "?$TArray@" "?$TArrayNoInit@" "FNameEntry" "@FName@@"`
   — enumerates the `TArray`s structurally, independent of naming. **Search the bare type fragment
   rather than `@@0V?$TArray@`**, and read the access code off each hit: `0`/`1`/`2` are static class
   members, **`3` is a namespace-scope global**, and the free-global case is exactly the one a `0`-only
   scan would miss. ⚠️ These are substrings of decorated symbols rather than identifiers, so check the
   tool treats its argument as a literal substring and not as a whole-token match.
3. Chase the single ASCII `ProcessEvent` occurrence and see whether it is a decorated symbol.

## Sources

Entirely our own record; no public source was needed for this and none is claimed.

- `enslaved-vr/engine-research/ENGINE-DOSSIER.md` §9c — the assertion method, the located addresses,
  the encoding table, and the **decorated MSVC symbol at `0x021C09BC`, recorded as "not yet chased"**.
- `enslaved-vr/dev-archive/tools/find_uobject_globals.py` — its usage line is what makes both
  proposals one-command jobs.
- `claude-memory/status/enslaved-vr.md`, OPEN block 2026-09-07 — the row this answers.
- `enslaved-vr/external-research/topics/2026-09-05-…-gobjobjects-is-an-assertion-string.md` — this
  lane's own prior topic, whose step 3 is now `[disproved]`.
