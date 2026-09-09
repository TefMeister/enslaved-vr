Supersedes: topics/2026-09-07b-public-ue3-locators-find-gnames-by-code-pattern-and-one-fork-ships-working-signatures.md §5 (the `ProcessEvent` prologue BYTE PATTERN only)

# Verdict from the modding lane: the `unrealsdk` prologue signature does not fit this build

**Author:** `/pd`, dev PC, 2026-09-09. The game was not launched.
**Status of the lead: PARTLY CONFIRMED — the strategy worked, the literal bytes did not.**

## What the topic reported

§5 of the 2026-09-07b topic reports `[reported]` that `unrealsdk` skips the vtable
index and scans `ProcessEvent`'s own prologue, giving the shape as:

```
push ebp / mov ebp,esp / push -1 / push <scopetable> / push <handler>
/ mov eax,fs:[0] / push eax / sub esp,0x50 / xor eax,ebp
/ lea eax,[ebp-0x0C] / mov fs:[0],eax      (CallFunction: same, sub esp,0xA4)
```

## What we found when we tried it `[verified-numerically 2026-09-09]`

**`UObject::ProcessEvent` in `Enslaved.exe` is at `0x00580990`**, and its prologue is:

```
55 8b ec 6a ff 68 d0 ca 91 01 64 a1 00 00 00 00 50 83 ec 54
push ebp / mov ebp,esp / push -1 / push 0x191cad0 / mov eax,fs:[0]
/ push eax / sub esp,0x54 / mov eax,[0x234ba00] / xor eax,ebp / mov [ebp-0x10],eax
```

Two constants in the published signature are wrong for this build:

| reported | actual here | why |
| --- | --- | --- |
| **two** `push imm32` | **one** | this build uses the older `_except_handler3` frame — the handler comes from the scope table, not from a second push |
| `sub esp,0x50` | `sub esp,0x54` | just a different local-frame size |

**A scanner built from the reported bytes matches exactly ONE function in 23 MB of
code, and it is not `ProcessEvent`.** Reproduce:

```
python dev-archive/tools/find_processevent.py --prologue
```

## What this does and does not withdraw

- ✅ **KEEP as reported and correct:** the vtable index is not stable and should be
  skipped; a detour on the function's own address is the right route. That framing
  is what made this tractable, and we followed it.
- ⚠️ **NARROW:** the prologue *invariant* ("an SEH + /GS frame") transfers. The
  prologue *byte pattern* does not — it encodes one compiler's SEH scheme and one
  function's frame size, both of which vary per build.
- ❌ **Do not present those bytes as a signature to try first.** Taken literally
  they return nothing, which reads as "the function is absent" rather than "the
  signature is for a different compiler".

## What worked instead, for the index

The §9c assertion-string route (`DO_CHECK` is on in this retail build) located it
in one pass: the only VIRTUAL function among `UnCorSc.cpp`'s assertion-bearing
functions, 1835 `.rdata` vtable slots against 0 for every other, asserting
`!HasAnyFlags(RF_Unreachable)` at `UnCorSc.cpp:6470`, returning `ret 0Ch`.

**Suggested addition for the topic, if `/gr` agrees:** for UE3 titles that shipped
with `DO_CHECK` on, the assertion-string route beats prologue scanning outright —
it is compiler-independent, it names the source file, and it self-validates via
the `__LINE__` immediate.

## One correction to our own side, recorded here for completeness

We briefly derived a `ProcessEvent` vtable index of **64** — which would have sat
neatly between the two published values (APB 60, Rocket League 67) and looked like
corroboration. **It is withdrawn** `[disproved 2026-09-09]`: it came from treating
runs of code pointers in `.rdata` as vtables, and adjacent vtables in this binary
abut with no separator, so runs merge and the derived index is an artefact. **No
index should be quoted for this game.** Flagging it because a plausible number
between two published ones is exactly the kind of thing that gets cited later.
