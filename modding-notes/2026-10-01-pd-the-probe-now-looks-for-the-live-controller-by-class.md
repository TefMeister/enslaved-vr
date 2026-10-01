# 2026-10-01 (`/pd`, dev PC): the UObject probe now looks for the live PlayerController by its class

**The game was not launched, and nothing here has been run inside it.**

On 2026-09-29 the probe confirmed GObjObjects, GNames and ProcessEvent live, but its PlayerController search matched
**names**, and every object named `*PlayerController*` it reached was the class or one of its functions, not the live
controller. Route (B) (calling the engine through the controller) needs the instance.

## What changed (staging `enslaved-vr/proxy-d3d9/`)

- **Split first, as the code-shape rule asks:** `dllmain.cpp` was 1,432 lines. The probe (367 lines) and its
  self-test (156) moved, unchanged, into `uobject_probe.inc.h` and `uobject_selftest.inc.h`, included at the same
  places. Proof: the preprocessed source is identical apart from two blank lines (32,851 non-blank lines, equal) for
  both the normal and the self-test build; backup tag `pre-split-2026-10-01-enslaved-probe`. (Two builds of the
  same source give different hashes with this compiler, so the preprocessed text is the honest comparison.)
- **Step 7, `FindLiveController`:** calibrate `UObject::Class` from the one object that is its own class (`"Class"`),
  searching Name+4 to Name+0x14; collect the classes named `*PlayerController*` (their class is `Class`); then report
  every object whose class is one of them as `LIVE PLAYERCONTROLLER`.
- **Self-test:** the synthetic world now carries class pointers (Class at Name+8, a PC class, one instance). 11 checks
  pass, including the regression this fixes: with the instance's class pointer moved, a name match alone is NOT
  reported as the live controller `[verified-numerically 2026-10-01, n=11 checks]`.
- Installed on the dev PC (`d3d9.dll` `36519dfa4b59`; previous build kept as `.bak-2026-10-01-before-live-controller-probe`),
  probe still off (`[uobject] Probe=0`).

## The one test

In gameplay (not a menu), with `[uobject] Probe=1`: the log should show `UObject::Class is at +0x30` (if Name is
+0x28, as measured live) and a `LIVE PLAYERCONTROLLER ... (class ...)` line. ⚠️ This is a D3D9-mode run; the
estate's VR output is now planned through D3D10 (Tefa, 2026-09-29), but these engine globals do not depend on the
graphics mode.
