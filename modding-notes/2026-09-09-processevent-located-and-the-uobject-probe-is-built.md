# 2026-09-09 — `ProcessEvent` is located, the published prologue signature does not fit this build, and the UObject probe is written

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** Both remaining `[PD]` rows on this project are closed.

Evidence: `dev-archive/recon/2026-09-09-processevent-located/`.
Tool: `dev-archive/tools/find_processevent.py`.
Code: `staging/enslaved-vr/proxy-d3d9/` (`dllmain.cpp`, `selftest.md`,
`build-selftest.ps1`).

---

## 1. ⭐ `UObject::ProcessEvent = 0x00580990` `[inferred-static 2026-09-09]`

Bounds `0x00580990..0x00580EFB` (1387 bytes), returns `ret 0Ch`.

Four signals converge, and none of them is "it has the right name":

1. **It is in `UnCorSc.cpp`** — UE3 Core's script VM, where `ProcessEvent`
   lives. The build ships `DO_CHECK` on, so the `check()` macro left the
   stringified expression, `__FILE__` and `__LINE__` at every assertion. This is
   the same route that located `GObjObjects` on 2026-09-07.
2. **It asserts `!HasAnyFlags(RF_Unreachable)` at `UnCorSc.cpp:6470`** —
   `ProcessEvent`'s own entry check that `this` is still a live object. The
   pushed line number decodes as `0x1946` = 6470, which is what confirms the
   argument decode is right rather than coincidental.
3. **It is the only VIRTUAL function among that file's assertion-bearing
   functions.** `ProcessEvent` is a `UObject` virtual, so its address appears
   once in every subclass's vtable: **1835 slots in `.rdata`**. The other six
   `UnCorSc.cpp` functions carrying assertions appear in **0** slots each. That
   single discriminator separates it cleanly — there is no second candidate.
4. **`ret 0Ch`** — thiscall plus three stack arguments, exactly
   `ProcessEvent(UFunction* Function, void* Parms, void* UnusedResult)`.

⚠️ **NOT confirmed, and confirmation is runtime-only.** The static case is
strong but it cannot exclude that this is a different `UObject` virtual defined
in the same file. The live check is one line: detour it and see whether the
first argument resolves through `GNames` to a script function name.

### ⚠️ The vtable INDEX is not delivered, deliberately

An earlier pass in this session read the index as 64 (which would have sat
neatly between the two published values, APB 60 and Rocket League 67). **That
reading was wrong and is withdrawn.** It came from treating runs of code
pointers in `.rdata` as vtables, and adjacent vtables in this binary abut with no
separator, so runs merge and every index derived that way is an artefact.

A cross-check from the call side killed it: a virtual call to index 64 would be
`call [reg+0x100]`, and a scan for it found none. That scan was itself
unreliable (a byte scan matches `FF` inside other instructions), so **the index
is simply unresolved** — not 64, not 26, unknown.

This costs nothing: `/gr` already established that the index is not stable across
UE3 games and that `unrealsdk` skips it entirely in favour of a detour on the
function's own address. The address is the deliverable.

---

## 2. ⚠️ The published `ProcessEvent` prologue signature DOES NOT FIT this build

`external-research/topics/2026-09-07b-...` reports `unrealsdk`'s prologue shape
`[reported]`:

```
push ebp / mov ebp,esp / push -1 / push <scopetable> / push <handler>
/ mov eax,fs:[0] / push eax / sub esp,0x50 / xor eax,ebp
/ lea eax,[ebp-0x0C] / mov fs:[0],eax          (CallFunction: sub esp,0xA4)
```

What `ProcessEvent` actually looks like here `[measured 2026-09-09]`:

```
55 8b ec 6a ff 68 d0 ca 91 01 64 a1 00 00 00 00 50 83 ec 54 ...
push ebp / mov ebp,esp / push -1 / push 0x191cad0 / mov eax,fs:[0]
/ push eax / sub esp,0x54 / mov eax,[0x234ba00] / xor eax,ebp
/ mov [ebp-0x10],eax
```

Two constants in the reported signature are wrong for this build:

| reported | actual here | why |
| --- | --- | --- |
| **two** `push imm32` | **one** | this build uses the older `_except_handler3` frame, where the handler comes from the scope table rather than a second push |
| `sub esp,0x50` | `sub esp,0x54` | just a different local-frame size |

**A scanner built from those literal bytes finds exactly ONE function in 23 MB of
code, and it is not `ProcessEvent`** `[verified-numerically 2026-09-09]` —
reproduce with `find_processevent.py --prologue`.

**The invariant survives; the byte pattern does not.** "An SEH + /GS frame" is
still the right shape to look for. This is worth recording precisely because the
row was written as *"scan the prologue"* and that, taken literally, would have
returned nothing and looked like the function was absent. A verdict file has gone
to `external-research/inbox/` so `/gr` can re-tag the claim.

---

## 3. The UObject probe: built, self-tested, deployed, never run

`staging/enslaved-vr/proxy-d3d9/dllmain.cpp` gains a `[uobject]` section and a
read-only probe. It closes the second `[PD]` row.

**It is read-only by construction**: it never calls `ProcessEvent`, never writes
engine memory, and every read is guarded by `VirtualQuery` first, so a wrong
address logs a rejection instead of crashing.

### ⭐ ASLR is OFF, so the static addresses ARE the runtime addresses

`Enslaved.exe` has `DYNAMIC_BASE` clear and an image base of `0x00400000`
`[measured 2026-09-09]`. No scanning or rebasing is needed at runtime. The probe
still checks `GetModuleHandle(NULL)` and reads nothing if the base differs, and
compares the ten bytes at `0x00580990` against the file so a mismatched build is
caught before any address is believed.

### What it does

1. shape-validates `GObjObjects` — `0 < Num <= Max < 8000000`, `Data` readable;
2. requires element 0 to dereference to an object whose **vtable is inside
   `Enslaved.exe`** — both criteria the row asked for by name;
3. counts live objects / NULL holes / junk across the first 4000 entries;
4. validates `GNames` by reading entry 0 and requiring `"None"`, which tests the
   `FNameEntry` name offset `+0x10` at the same time;
5. **calibrates `UObject::Name` rather than assuming it**, then dumps a sample
   of object names and reports the live `PlayerController`.

### ⚠️ The self-test caught a real bug before the game ever saw it

`build-selftest.ps1` compiles **`dllmain.cpp` itself** with `-DUOBJECT_SELFTEST`
against a synthetic UObject world, so the code under test is the code that ships
— the Far Cry 2 lesson, where verifying a transcription passed and only
compiling the real source proved anything. The name field is planted at `+0x2C`,
an offset the probe is never told.

The first run **failed checks 6 and 7**: calibration picked `+0x04` instead.
**FName index 0 is the legal name `"None"`, so any all-zero field resolves for
100% of objects** and the first zero-filled offset wins. This would have happened
in the real game too, and the probe would have reported a confidently wrong
`Name` offset and then found no `PlayerController`.

Fixed by scoring only **non-zero** indices and requiring **≥4 distinct names**,
plus logging every close runner-up rather than silently picking one — any small
integer is a valid FName index, so a counter field can still score well, and that
is a judgement for whoever reads the log. **8/8 checks now pass**
`[verified-numerically 2026-09-09, n=8 checks]`.

### Deployed

`Binaries\Win32\d3d9.dll` is now the new build (86,528 B, md5 `a9d6a63c…`) and has
been re-stamped with `deployed.sh record`. The previous DLL and ini are backed up
beside it as `*.bak-2026-09-09`.

⚠️ **Wording correction, applying to the 2026-09-08 note as well as this one:**
`d3d9.dll` is **gitignored in `staging`** (`proxy-d3d9/.gitignore` line 3), so
there is no "committed staging copy" to be byte-identical to. What is committed is
the **source**; the DLL is reproducible from it with `build.ps1`. The deployed
file matches the one built in the staging working tree this session, and that is
all a hash comparison against staging can ever mean here.

⚠️ **The installed `d3d9_proxy.ini` was NOT overwritten** — it had been tuned by
the live session (`Enabled=1`, `Mode=1`, `Separation=6.5`) and differs from the
staging template, which still carries the safe `Enabled=0` defaults. Only the new
`[uobject]` section was appended. **Anyone deploying here must append to the
installed ini, never copy the staging one over it**, or the stereo silently
switches off.

---

## What the next live run should do

**One change: set `Probe=1` under `[uobject]` in
`Binaries\Win32\d3d9_proxy.ini`, then play into a level.** Search the log for
`[uobject]`.

| log line | meaning |
| --- | --- |
| `PLAYERCONTROLLER [...] MonkeyPlayerController_0` (or similar) | ⭐ the whole chain works. `GObjObjects`, `GNames`, the name offset and route (B) are all real, and the in-process route is open. |
| `shape OK ... live objects` but no name offset | `GObjObjects` is real, `GNames` or `+0x10` is not. Object access works; names need re-deriving. |
| `shape REJECTED` | `0x0242B984` is not `GObjObjects`. Route (B) needs re-deriving from scratch — the strongest runner-up is recorded in the 2026-09-08 note. |
| `ProcessEvent prologue ... DOES NOT MATCH` | the installed exe is not the build analysed. Stop; every address is suspect. |
| nothing at all | the probe never ran — check `Probe=1` really is in the *installed* ini. |

It costs one ini edit and one ordinary play session, and it can be combined with
any other flat run — it does not disturb the stereo.
