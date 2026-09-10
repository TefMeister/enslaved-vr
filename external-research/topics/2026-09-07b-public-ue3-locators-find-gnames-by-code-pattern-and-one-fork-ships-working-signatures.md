# Every public UE3 locator finds `GNames` by **code pattern**, not by name — and a generator fork we never found ships working signatures for six games

**Status:** 🆕 new · **Priority:** ⭐ high — it supplies a concrete byte signature to try, a
published adjacency figure that makes a minutes-long probe worth doing first, **corrects this lane's
own 2026-09-05 conclusion** about the generators, and flags a collision risk against our own proxy.

## Why this was looked up

The `[PD]` row's remaining half: *"`GNames` has no string in the binary in either encoding, so the
assertion route does not reach it — it needs a different locator."* My companion topic today
([wrong name / decorated symbols](2026-09-07-gnames-was-searched-under-the-wrong-name-and-the-binary-carries-decorated-symbols.md))
proposed two in-house routes. This one asked the public record what people **actually do**.

## ⭐ 1. The answer: nobody looks for a symbol at all

**No public UE3 tool searches for a `GNames` string or symbol.** Every working locator found — six
games across two independent codebases — scans for a **code pattern**: an instruction that loads the
array's `Data` pointer from an absolute address, immediately followed by an indexed read with
**scale 4**. `[reported 2026-09-07]`

That reframes our own negative helpfully: *"`GNames` has no string in the binary"* is not a surprising
result to be explained. **It is the normal case, and the public toolchain never depended on one.**

### ⭐⭐ The convergent stock-UE3 signature — try this first of the byte routes

`polivilas/UnrealEngineSDKGenerator` ships a per-game `NamesStore.cpp` for four UE3 titles, and
**all four use the identical pattern** `[reported, n=4 titles in one codebase]`:

```
pattern  8B 0D ?? ?? ?? ?? 83 3C 81 00 74      mask  xx????xxxxx
```

which is `mov ecx,[imm32]` / `cmp dword ptr [ecx+eax*4],0` / `jz`, and **the DWORD at match+2 is
`&GNames`** — the address of the `TArray<FNameEntry*>` itself, whose first field is `Data`.
(APB: Reloaded drops the trailing `74`.)

The four are **Unreal Tournament 3, All Points Bulletin: Reloaded, Tribes: Ascend and Hawken**.
**UT3 is close to stock UE3**, which makes this the single most likely signature to transfer to
Enslaved. Semantically it is the engine asking *"is slot `Index` in the name table empty?"* — the
null-slot check in `FName`'s lookup path — which is why it survives across licensee builds: it is a
property of the algorithm, not of the game.

**The generalisable invariant, if the exact bytes miss** `[inferred-static]`: scan for
`A1 imm32` / `8B 0D imm32` / `8B 15 imm32` / `8B 05 imm32` / `8B 1D imm32` where `imm32` lands in a
**writable** section, and the next instruction is an indexed read with **scale 4**. That yields a
handful of candidates — which is what §3's validator is for.

Independent corroboration from a different codebase: `bl-sdk/unrealsdk` (apple1417) ships
structurally identical but textually different patterns for Borderlands 1 (`A1 {????????} 8B 0C ??…`,
a *read* site) and Borderlands 2 (`A3 {????????} 8B 45 ?? 89 03`, `mov [GNames],eax` — a **write**
site inside the array-growth code). Same idiom, different games, arrived at separately.

## ⭐ 2. `GNames` sits just BELOW `GObjObjects` — and we already have `GObjObjects` to the byte

Two independent published UE3 address pairs `[reported, n=2]`:

| game | `GNames` | `GObjects` | Δ |
| --- | --- | --- | --- |
| Borderlands 1 | `0x01FB4DA8` | `0x01FB4DD8` | **0x30** |
| Rocket League | `0x0246D6F0` | `0x0246D738` | **0x48** |

**In both, `GNames` is at the LOWER address, under 0x50 away.** Both are `Core` globals, so the
linker groups them. n=2 is not proof, but our `GObjObjects.Data = 0x0242B984` makes the probe cost
minutes: look at roughly `0x0242B780`–`0x0242BB80`, **biased below**, for a 12-byte `TArray`-shaped
triple `{ptr, count, max}` where `ptr` is a plausible heap pointer and `0 < count <= max` with
`count` in the tens of thousands.

⚠️ Note `GObjAvailable` already sits **12 bytes above** `GObjObjects`, so the neighbourhood is
confirmed to be the Core-globals cluster. That is a point in favour.

## ⚠️ 3. The validator — and the correction it forces to my other topic today

The universal acceptance test, used by every tool that auto-finds a name pool `[reported]`: treat the
candidate as `TArray<FNameEntry*>`, read `Data[0]`, read the characters, and **require `"None"`**;
then require `Data[1..8]` to be ASCII identifiers, most ending in `Property`.

**`FNameEntry` layout, 32-bit UE3** `[reported, n=2 explicit models + consistent with 2 more]`:

| offset | field |
| --- | --- |
| `0x00` | `Flags` — 8 bytes (UE3's `EObjectFlags` is 64-bit) |
| `0x08` | `Index` — `uint32`; **bit 0 is `NAME_WIDE_MASK`**, the real index is `Index >> 1` |
| `0x0C` | `HashNext` — `FNameEntry*` |
| `0x10` | `union { char Ansi[]; wchar_t Wide[]; }` |

All four 32-bit UE3 games land the character array at **`+0x10`**. So the name data is **per-entry
ANSI *or* UNICODE, selected by bit 0 of `Index`** — not fixed-encoding — and the early engine names
are ANSI. Do **not** hard-code the full early-name list: the order after index 0 differs between
engine generations (`StrProperty` vs `StringProperty`, `DelegateProperty` inserted). Checking entry 0
is `None` and the next few end in `Property` is sufficient and version-proof.

### ✏️ The correction

**My companion topic's contents-based reasoning only works against a LIVE process.** UE3's
`FNameEntry` objects are **heap-allocated during startup** from the compiled-in `REGISTER_NAME`
table, so `None`, `ByteProperty` and the rest are **not in `Enslaved.exe` on disk**
`[reported 2026-09-07]`. That is fine for our DLL-proxy plan, but it means the validator is a
**runtime** step, not an offline scan — and any static route (mine or the byte signature) still has
to be *confirmed* at runtime by it.

## ❌ 4. This corrects our own 2026-09-05 conclusion

That topic recorded, and the dossier §9c repeats, that the UE3 SDK generators *"ship a `FindPattern`
harness with every pattern set to the literal string `null`"*. **That is true of `UE3SDKGenerator`
and `CodeRed` — and false of the wider family.**

**`polivilas/UnrealEngineSDKGenerator` (the KN4CK3R lineage, ~376★) ships real, working byte
signatures already filled in** for six games — the four UE3 titles above plus Borderlands 2 and
Rocket League — in per-game `NamesStore.cpp` / `ObjectsStore.cpp`. It is not one of the two repos this
lane checked, and **nothing in our record mentions it, KN4CK3R, `NamesStore`, `unrealsdk`, apple1417,
Tribes or Hawken** `[verified-numerically 2026-09-07 — the same grep returns 3 hits for
`UE3SDKGenerator`, so it was capable of positives]`.

So the honest form of the 2026-09-05 claim is: *the two generators we looked at expect hand-supplied
addresses; a third, better-populated fork exists and ships patterns.* Suggested tag on the original:
`[disproved 2026-09-07]` as a general statement about "the generators".

**Free cross-check on work already done:** UT3's `GObjects` pattern is
`A1 ???? 8B ?? ?? 8B ?? ?? 25 00 02 00 00` and BL2's is `8B 0D {????????} 8B 04 ?? 8B 40 ?? 25 00020000`
— **both AND an object-flag field with `0x200`**. Looking for that idiom near our confirmed
`GObjObjects` xref is independent corroboration of an address we already trust.

## 5. `ProcessEvent`: the index is NOT stable, and the better route skips it

**Two published UE3 indices disagree: All Points Bulletin = 60, Rocket League = 67**
`[reported]`. So the vtable index must be found per game, and no public index table or generic
signature exists — every generator leaves `ProcessEventIndex`/`Pattern`/`Mask` null.

⭐ **`unrealsdk` avoids the index entirely**: it scans for `ProcessEvent`'s **own prologue** and
installs a **detour**, so it never needs a vtable slot. The prologue shape is `push ebp` /
`mov ebp,esp` / `push -1` / stack setup / `sub esp,0x50` / `xor eax,ebp` (stack cookie) /
`lea eax,[ebp-0x0C]` / `mov fs:[0],eax` (SEH frame). It scans the same way for `CallFunction`
(same shape, `sub esp,0xA4`). `[reported]` — **⚠️ the STRATEGY holds, the BYTES do not. See "What the modding lane found" at the end of this section `[disproved 2026-09-09]` for this build.**

Two UE3-specific extras worth having:

- **The `check()` trick should work here too** — `UObject::ProcessEvent` and `CallFunction` are dense
  with assertions, and this build demonstrably retains them. Hunt assertion strings mentioning
  `Function`, `ParmsSize`, `Parms`, `Stack` or recursion limits and take the xref. **⭐ CONFIRMED — this is what actually worked, in ONE pass** `[verified-numerically 2026-09-09]`; see below.
- ⭐ **`GNatives`** — UE3's script VM dispatches bytecode through a global array of ~256 native
  function pointers (with `GCasts` alongside). **A contiguous 0x100-entry block of in-module code
  pointers in `.data` is one of the most recognisable structures in the whole binary**, and landing on
  it puts you inside the VM cluster where `ProcessInternal` / `CallFunction` / `ProcessEvent` are
  neighbours. `[reported]` that they exist and are bytecode-indexed; `[hypothesis]` that scanning for
  the table is a practical locator.

### ⛔ What the modding lane found when it tried the published bytes (added by `/gr` 2026-09-10)

`/pd` (dev PC, 2026-09-09, no launch) implemented the signature above and measured it against
`Enslaved.exe`. **`UObject::ProcessEvent` is at `0x00580990`**, and its real prologue is:

```
55 8b ec 6a ff 68 d0 ca 91 01 64 a1 00 00 00 00 50 83 ec 54
push ebp / mov ebp,esp / push -1 / push 0x191cad0 / mov eax,fs:[0]
/ push eax / sub esp,0x54 / mov eax,[0x234ba00] / xor eax,ebp / mov [ebp-0x10],eax
```

Two constants in the published signature are wrong for this build `[verified-numerically 2026-09-09]`:

| reported above | actual here | why |
| --- | --- | --- |
| **two** `push imm32` | **one** | this build uses the older `_except_handler3` frame — the handler comes from the scope table, not a second push |
| `sub esp,0x50` | `sub esp,0x54` | a different local-frame size |

**A scanner built from the reported bytes matches exactly ONE function in 23 MB of code, and it is
not `ProcessEvent`.** Reproduce: `python dev-archive/tools/find_processevent.py --prologue`.

**What this withdraws, and what it does not:**

- ✅ **KEEP:** the vtable index is not stable and should be skipped; a detour on the function's own
  address is the right route. That framing is what made this tractable and it was followed.
- ⚠️ **NARROW:** the prologue *invariant* ("an SEH + /GS frame") transfers. The prologue *byte
  pattern* does not — it encodes one compiler's SEH scheme and one function's frame size, both of
  which vary per build.
- ❌ **Do not present those bytes as a signature to try first.** Taken literally they return nothing,
  which reads as *"the function is absent"* rather than *"the signature is for a different compiler"*
  — a false negative that is expensive precisely because it looks like a finding.

### ⭐⭐ What worked instead, and it generalises to any UE3 title that shipped with `DO_CHECK` on

The §9c assertion-string route located `ProcessEvent` **in one pass**: the only VIRTUAL function
among `UnCorSc.cpp`'s assertion-bearing functions — 1835 `.rdata` vtable slots against **0** for
every other candidate — asserting `!HasAnyFlags(RF_Unreachable)` at `UnCorSc.cpp:6470`, returning
`ret 0Ch` `[verified-numerically 2026-09-09]`.

**Adopted as this topic's recommendation, as the modding lane suggested:** for UE3 titles that
shipped with `DO_CHECK` enabled, **the assertion-string route beats prologue scanning outright** —
it is compiler-independent, it names the source file, and it self-validates through the `__LINE__`
immediate. Prologue scanning is the fallback for builds with assertions compiled out.

### ⛔ And a number NOT to quote: there is no `ProcessEvent` vtable index for this game

The modding lane briefly derived an index of **64**, which would have sat neatly between the two
published values (APB 60, Rocket League 67) and read as corroboration. **It is withdrawn**
`[disproved 2026-09-09]`: it came from treating runs of code pointers in `.rdata` as vtables, and
adjacent vtables in this binary abut with no separator, so runs merge and the derived index is an
artefact. Recorded here because a plausible number sitting between two published ones is exactly
the kind of thing that gets cited later.

## ⚠️ 6. A collision risk against our own proxy, previously unrecorded

**Helix Mod's 3D Vision fix for this exact game is a `d3d9.dll` wrapper** dropped into
`Binaries\Win32\` alongside `dx9settings.ini` and a `shaderoverride\` folder `[reported 2026-09-07]`.

Two consequences, and this lane has recorded neither — the 2026-09-02b topic names the Helix fix four
times but never says what form it takes `[verified-numerically 2026-09-07]`:

1. **Positive:** `d3d9.dll` proxying is a *proven, shipped* injection vector on this exact
   executable — independent evidence that our own approach is sound on this binary.
2. ⚠️ **Negative:** it occupies **the same slot as our proxy**. A user with that fix installed cannot
   run both, and if anyone ever tests on a machine that has it, the symptom would be ours silently not
   loading. Worth one line in the dossier and in any future install instructions.

## 7. Enslaved specifically: nothing published, and that negative looks real

No SDK dump, no published `GNames`/`GObjects` offsets, no script hook, no injection-based mod
`[reported 2026-09-07]` — searches across GitHub, the usual RE forums and mod sites surfaced only
pointer-scan cheat tables (health, tech orbs, noclip — no UObject awareness), commercial trainers, and
ini/texture mods. Ninja Theory's *DmC: Devil May Cry* (also UE3, also `NT*` packages) is the best
analogue and has no published SDK either.

⭐ **But the engine version is one command away.** Enslaved is **absent** from `EliotVU/Unreal-Library`'s
`GameBuild` enum, which lists ~25 UE3 titles with their package/licensee versions (APB 547/028,
Batman AA 576/021, Borderlands 584/057, Bulletstorm 742/029, Dishonored 801/030, Rocket League
867/009, XCOM 845/059 …) `[reported; the fetch enumerated those two dozen correctly, so it was capable
of a positive, though it reported a partial read]`. **`UPKUtils` / `Unreal-Library` will read
`PackageVersion`/`LicenseeVersion` straight out of an `NTEngine.u` header** — which then tells us
which of the six games above is our nearest neighbour, and therefore which signature to try first.

## The concrete next steps, in cost order

1. **The adjacency probe (minutes, runtime).** Dump `[GObjObjects − 0x200, GObjObjects + 0x200]`,
   biased **below**, and look for the `{ptr, count, max}` triple. Validate with §3.
2. **Write the §3 validator first**, whichever locator runs into it — it is decisive and cheap, and it
   turns every other step from a guess into a search. ⚠️ Runtime only.
3. **The UT3-family signature** `8B 0D ?? ?? ?? ?? 83 3C 81 00`, DWORD at +2. Widen to the invariant
   if the exact bytes miss.
4. **Read the licensee version out of `NTEngine.u`** with UPKUtils — cheap, and it picks the sibling.
5. **`ProcessEvent` by prologue signature + detour**, not by vtable index.

## Honest limits

- Every address and signature above is **from other games**. Nothing here has been run against
  `Enslaved.exe`.
- The adjacency figure is **n=2**.
- ⚠️ **My companion topic's decorated-symbol proposal has no public corroboration** — no public UE3
  locator uses decorated symbols. That does not make it wrong (this binary is unusually generous with
  debug residue, which is exactly why public tools targeting normal binaries would not rely on it),
  but it is **ours alone and unvalidated**, and the byte-pattern and adjacency routes above are the
  ones with six games behind them. Rank accordingly.

## Sources and credit

Read online only; nothing cloned, downloaded or copied.

- **KN4CK3R** (original) and **polivilas** (fork) — `UnrealEngineSDKGenerator`, the four UE3
  `NamesStore.cpp`/`ObjectsStore.cpp` signatures. <https://github.com/polivilas/UnrealEngineSDKGenerator>
- **apple1417** — `bl-sdk/unrealsdk` (the Borderlands UE3 `globals.cpp` and `hooks.cpp` signatures,
  and the prologue-detour approach). <https://github.com/bl-sdk/unrealsdk>
- **TheFeckless** — the original UE3 SDK Generator, ancestor of the family, and the CE Lua dumper port.
- **ItsBranK** — `UE3SDKGenerator`. **CodeRedModding** — `CodeRed-Generator`. **matix2** —
  `RLSDK-Generator` (the Rocket League offsets and `ProcessEventIndex = 67`).
- **EliotVU** — `Unreal-Library` (the UE3 package/licensee version table); **wghost** — `UPKUtils`.
- **Helix Mod** — the Enslaved 3D Vision fix, the `d3d9.dll` wrapper precedent on this exact game.
- **Do0ks** (`GSpots`), **McDaived** (`UE-Dumper`), **kovidomi**/**CorrM** (Unreal Finder Tool),
  **patrickBakin** — all checked and **UE4/UE5 only**; credited for having been ruled out.
- **Shh0ya**, the **Unreal Wiki / BeyondUnreal** contributors.

## What came back empty, and whether it is real

- **No `GNames` string in any UE3 binary, anywhere:** **real and expected** — no public tool looks for
  one.
- **No published UE3 `ProcessEvent` index or generic signature:** **real**, and actively disproved as
  a stable value by APB=60 vs Rocket League=67.
- **No UE3-capable *automatic* GNames finder:** **real** — GSpots, UE-Dumper, Unreal Finder Tool and
  UE4-Function-Address-Finder all state UE4/UE5 scope explicitly. There is no tool to point at this
  game.
- **No Enslaved SDK, offsets, script hook or injection mod:** **real**, across GitHub, the RE forums
  and the mod sites.
- ⚠️ **Several high-value pages returned HTTP 403 to automated fetch** (a cheat-engine forum's UE3
  dumper thread ×3, two RE-forum threads on manually finding `GObjects`/`GNames`, a mod site, a wiki,
  and one article). **These are fetch failures, not negatives** — the dumper thread and the two
  manual-locator threads are the highest-value unread items and would open fine in a browser.
