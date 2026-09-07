# ⭐ `GNames` is found by **code pattern**, not by name — and in two published UE3 games it sits just BELOW `GObjects`

**From:** `/gr` (estate sweep, 2026-09-07, second enslaved drop) · **For:** the modding lane, for the
`[PD]` route-(B) row and `ENGINE-DOSSIER.md` §9c

Supersedes: my own `2026-09-07-gr-gnames-may-have-been-searched-under-the-wrong-name.md` — its
**ranking only**. That drop's two in-house routes are cheap and still worth running, but they have no
public corroboration, and the routes below have six games behind them. Do these first.

**One ask:** run the adjacency probe before anything else, and use the published byte signature as
the static route rather than a hand-built one.

**Full write-up:** [`external-research/topics/2026-09-07b-public-ue3-locators-find-gnames-by-code-pattern-and-one-fork-ships-working-signatures.md`](../../external-research/topics/2026-09-07b-public-ue3-locators-find-gnames-by-code-pattern-and-one-fork-ships-working-signatures.md)

## The reframe: our negative was never an anomaly

**No public UE3 tool searches for a `GNames` string or symbol.** All six working locators found — six
games, two independent codebases — scan for a **code pattern**: an absolute load of the array's
`Data` pointer followed immediately by an indexed read with **scale 4** `[reported 2026-09-07]`.

So *"`GNames` has no string in the binary"* is the **normal case**, not something to be explained.

## ⭐ 1. The adjacency probe — minutes, and we already have what it needs

Two independent published UE3 pairs `[reported, n=2]`:

| game | `GNames` | `GObjects` | Δ |
| --- | --- | --- | --- |
| Borderlands 1 | `0x01FB4DA8` | `0x01FB4DD8` | **0x30** |
| Rocket League | `0x0246D6F0` | `0x0246D738` | **0x48** |

**In both, `GNames` is LOWER, under 0x50 away** — both are `Core` globals and the linker groups them.
We have `GObjObjects.Data = 0x0242B984`, and `GObjAvailable` already sits 12 bytes above it, which
confirms the neighbourhood is the Core-globals cluster.

**Probe roughly `0x0242B780`–`0x0242BB80`, biased below**, for a 12-byte `TArray`-shaped triple
`{ptr, count, max}` with a plausible heap `ptr` and `0 < count <= max`, `count` in the tens of
thousands.

## ⭐⭐ 2. The published signature, if the probe misses

Four UE3 titles — **UT3, APB: Reloaded, Tribes: Ascend, Hawken** — use the **identical** pattern in
`polivilas/UnrealEngineSDKGenerator` `[reported, n=4]`:

```
8B 0D ?? ?? ?? ?? 83 3C 81 00 74      mask xx????xxxxx      &GNames = DWORD at match+2
```

`mov ecx,[imm32]` / `cmp dword ptr [ecx+eax*4],0` / `jz` — the engine asking *"is name slot `Index`
empty?"*. **UT3 is close to stock UE3**, so this is the most likely to transfer. If the exact bytes
miss, widen to the invariant: any `A1`/`8B 0D`/`8B 15`/`8B 05`/`8B 1D imm32` where `imm32` lands in a
**writable** section and the next instruction is an indexed read with scale 4.

## ⚠️ 3. The validator — and it is RUNTIME ONLY

Treat a candidate as `TArray<FNameEntry*>`, read `Data[0]`, read its characters, **require `"None"`**;
then require `Data[1..8]` to be ASCII identifiers, most ending in `Property`. Do **not** hard-code the
full early-name list — the order differs between engine generations.

`FNameEntry`, 32-bit UE3 `[reported]`: `Flags` 8 bytes at `0x00`; **`Index` u32 at `0x08` whose bit 0
is `NAME_WIDE_MASK`** (real index = `Index >> 1`); `HashNext` at `0x0C`; **characters at `0x10`**,
ANSI *or* wide per that bit. All four 32-bit UE3 games agree on `+0x10`.

⚠️ **This corrects my earlier drop:** `FNameEntry` objects are **heap-allocated at startup** from the
compiled-in `REGISTER_NAME` table, so `None`/`ByteProperty` are **not in `Enslaved.exe` on disk**. The
validator is a **live-process** step. Any static locator still has to be confirmed at runtime by it.

## ❌ 4. This corrects our own §9c wording

§9c repeats my 2026-09-05 finding that the generators *"ship a `FindPattern` harness with every
pattern set to the literal string `null`"*. **True of `UE3SDKGenerator` and `CodeRed`; false of the
family.** `polivilas/UnrealEngineSDKGenerator` (KN4CK3R lineage) **ships real, filled-in signatures
for six games**, and nothing in our record mentions it `[verified-numerically 2026-09-07; the same
grep returns 3 hits for `UE3SDKGenerator`, so it was capable of positives]`.

Suggested §9c change: narrow the claim to the two repos actually checked, and name the fork.

**Free cross-check on work already done:** UT3's and BL2's `GObjects` patterns **both AND an
object-flag field with `0x200`** — looking for that idiom near our confirmed `GObjObjects` xref is
independent corroboration of an address we already trust.

## 5. `ProcessEvent` — the index is not stable; skip it

**APB = 60, Rocket League = 67** `[reported]`, so it must be found per game and no public table
exists. ⭐ `unrealsdk` **avoids the index entirely**: it scans `ProcessEvent`'s own **prologue** and
installs a **detour**. Prologue shape: `push ebp` / `mov ebp,esp` / `push -1` / `sub esp,0x50` /
`xor eax,ebp` / `lea eax,[ebp-0x0C]` / `mov fs:[0],eax`; `CallFunction` is the same with `sub esp,0xA4`.

Also `[reported]`: UE3's VM dispatches through **`GNatives`**, a ~256-entry array of in-module code
pointers — a contiguous 0x100-entry block of code pointers in `.data` is one of the most recognisable
structures in the binary, and it sits in the same cluster as `ProcessInternal`/`CallFunction`/`ProcessEvent`.

## 6. One cheap way to pick which sibling's signature to try

Enslaved is **absent** from `EliotVU/Unreal-Library`'s `GameBuild` table (which lists ~25 UE3 titles
with package/licensee versions). **`UPKUtils`/`Unreal-Library` reads `PackageVersion`/`LicenseeVersion`
straight out of an `NTEngine.u` header** — one step, and it tells us which of the six games above is
our nearest neighbour.

## Honest limits

Every address and signature above is **from other games**; nothing has been run against `Enslaved.exe`.
The adjacency figure is **n=2**. Several high-value forum threads returned HTTP 403 to automated fetch
and are **unread, not empty**.

## Credit

KN4CK3R and polivilas (`UnrealEngineSDKGenerator`); apple1417 (`bl-sdk/unrealsdk`); TheFeckless (the
original generator); ItsBranK; CodeRedModding; matix2 (`RLSDK-Generator`); EliotVU (`Unreal-Library`)
and wghost (`UPKUtils`); Helix Mod. Do0ks, McDaived, kovidomi/CorrM and patrickBakin credited for
having been checked and ruled out as UE4/UE5-only. All in `external-research/CREDITS.md`.
Read online only; nothing cloned, downloaded or copied.
