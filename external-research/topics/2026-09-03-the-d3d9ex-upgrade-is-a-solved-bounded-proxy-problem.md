# The D3D9Ex upgrade is a solved, bounded proxy problem — `D3DPOOL_MANAGED` is a sizing question, not a go/no-go

**Date:** 2026-09-03 · **Status:** 🆕 new · **Answers:** ENGINE-DOSSIER.md §9's *"unverified, and it
is the first thing to establish, because it is the difference between a one-line proxy change and a
resource-remapping project"*

## The open risk this addresses

§9 lays out the D3D9Ex upgrade cleanly: the proxy already owns `d3d9.dll` and already exports
`Direct3DCreate9Ex`, `IDirect3DDevice9Ex` derives from `IDirect3DDevice9`, so the proxy can create
the Ex object itself and hand the game the base interface. Then it names the trap that decides the
whole design:

> **`D3DPOOL_MANAGED` does not exist on a D3D9Ex device.** Any
> `CreateTexture`/`CreateVertexBuffer`/`CreateIndexBuffer` asking for it fails. So the upgrade above
> is only viable if UE3's D3D9 RHI never asks for MANAGED on this build — **unverified, and it is
> the first thing to establish**, because it is the difference between a one-line proxy change and a
> resource-remapping project. `[reported]`

The board carries the corresponding `[FLAT]` row: *"instrument one launch for `D3DPOOL_MANAGED` to
settle whether the D3D9Ex upgrade is a one-liner or a project."*

**The premise is right — but the dichotomy is false.** There is a third option, it is the one the
wrapper community converged on years ago, and it is neither a one-liner nor a project.

## First, the two primary facts, quoted

Microsoft's `D3DPOOL` reference, in its own differences box:

> Differences between Direct3D 9 and Direct3D 9Ex: **D3DPOOL_MANAGED is valid with
> IDirect3DDevice9; however, it is not valid with IDirect3DDevice9Ex.**

And "Lost Devices (Direct3D 9)":

> A Direct3D 9 device returns D3DERR_DEVICELOST. […] **A Direct3D 9Ex device never returns
> D3DERR_DEVICELOST**, but can return new status messages.

Put those two side by side and the removal stops looking arbitrary. The same `D3DPOOL` page says why
MANAGED exists at all:

> Applications should use D3DPOOL_MANAGED for most static resources because **this saves the
> application from having to deal with lost devices.** (Managed resources are restored by the
> runtime.)

**MANAGED is a device-loss recovery mechanism, and a 9Ex device has no device loss.** The pool was
not withdrawn to make life hard; it was withdrawn because on 9Ex it has nothing left to do. That
reframes the translation `MANAGED → DEFAULT` from a hack that might corrupt semantics into the
migration Microsoft's own design implies. `[reported 2026-09-03]`

## The one thing that genuinely does change — and the standard fix

Not all of MANAGED's behaviour is device-loss. From the same page:

> Textures placed in the D3DPOOL_DEFAULT pool **cannot be locked unless they are dynamic textures**
> or they are private, FOURCC, driver formats.

whereas managed resources *"can be locked. Only the system-memory copy is directly modified."* So a
naive `MANAGED → DEFAULT` rewrite keeps every allocation working and then fails the first time the
engine tries to `Lock()` a texture it has always been allowed to lock.

**That is exactly why the established rewrite is `MANAGED → DEFAULT + D3DUSAGE_DYNAMIC`, not
`MANAGED → DEFAULT`.** The `DYNAMIC` usage is what restores lockability, and the pool table on the
same page confirms the combination is legal (`D3DPOOL_DEFAULT` × `D3DUSAGE_DYNAMIC` = yes, while
`D3DPOOL_MANAGED` × `D3DUSAGE_DYNAMIC` is not — so there is no case where the rewrite collides with
a flag the game already set).

## The prior art: this is a named, shipped strategy with a known success rate

`elishacloud/dxwrapper` implements precisely the upgrade §9 describes — a hidden `D3d9to9Ex` option
that hands a legacy game an Ex device — and its maintainer states the pool handling directly: they
**override `D3DPOOL_MANAGED` to `D3DPOOL_DEFAULT` plus `D3DUSAGE_DYNAMIC`, following Special K's
strategy**, and report that this *"opened up a lot more games"*. Of eight games tested, **seven
worked**. `[reported 2026-09-03]`

That is the finding. The translation is not something this project has to design; it is a
half-dozen lines in the proxy's existing `CreateTexture` / `CreateVertexBuffer` /
`CreateIndexBuffer` wrappers, with two independent implementations already in public as evidence it
holds up across a real spread of titles.

## ⚠️ What the same source says breaks — take these as the real risk list

The maintainer is explicit that the conversion is *"a very basic conversion"* and names concrete
failure modes. These are worth carrying into §9 in place of the single MANAGED unknown, because they
are the things that actually decide whether this build cooperates:

- **Paletted textures are not supported on 9Ex.**
- **16-bit textures only work in system memory.**
- **D3DX functions remain problematic.** (Relevant here: Enslaved is UE3 with a 2010-era D3DX
  dependency chain.)
- **Some titles fail outright at device-creation time.**

`[reported 2026-09-03]` None of these is detectable from our current static evidence, and all four
are cheap to observe on the first Ex-upgrade launch.

## What this changes for the board

The `[FLAT]` row *"instrument one launch for `D3DPOOL_MANAGED` to settle whether the D3D9Ex upgrade
is a one-liner or a project"* should not be deleted, but its **purpose changes and its priority
drops**:

- It is **no longer a go/no-go gate.** Whatever the answer, the route is viable, because the
  translation is generic and does not depend on how much MANAGED traffic there is.
- What the instrumented count actually tells us is **how much Lock() traffic gets re-pointed**, i.e.
  the performance and risk *size*, not the feasibility. A count of zero would be pleasant; a large
  count is a reason to watch for the four failure modes above, not a reason to abandon the route.
- The measurement is still worth having, and it is still free if it rides along on a launch that is
  happening anyway — but it should no longer be the thing the D3D9Ex decision waits on.

That matters for scheduling: it removes one item from the set of things that must happen *before*
the Ex upgrade can be attempted at all.

## How this sits against the `-d3d10` alternative

§9 names two routes and says "decide after the `D3DPOOL_MANAGED` instrumented launch". With this
finding, the comparison is cleaner and does not need that launch to resolve:

| | (a) D3D9 + Ex upgrade | (b) `-d3d10` |
| --- | --- | --- |
| Camera injection | **the proven `SetVertexShaderConstantF(0,…,4)` hook** — already working, stereo already demonstrated | undesigned constant-buffer patch |
| Shared-texture path | D3D9Ex + `pSharedHandle`, no keyed mutex (needs an `IDirect3DQuery9` event query + double buffering) | ordinary DXGI shared resource, keyed mutexes available |
| Pool problem | solved generically, prior art, 4 named failure modes | does not arise |
| Unknowns | 4 reported compatibility classes, all cheap to observe | the entire injection design |

Route (a) keeps the one thing this project has already proven and pays for it in known, enumerated
risks. Route (b) throws away a working camera hook to avoid a problem that turns out to be solved.
**On this evidence (a) is the one to try first** — and the honest way to say that is: the argument
for (b) was largely that (a) was blocked on an unknown, and it is not.

## Sources

- [D3DPOOL enumeration](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dpool) — Microsoft.
  The 9-vs-9Ex differences box, the lockability restriction on DEFAULT, the pool × usage
  compatibility tables, and the "saves the application from having to deal with lost devices"
  rationale.
- [Lost Devices (Direct3D 9)](https://learn.microsoft.com/en-us/windows/win32/direct3d9/lost-devices)
  — Microsoft. "A Direct3D 9Ex device never returns D3DERR_DEVICELOST."
- [dxwrapper discussion #105, "Did you ever consider doing something with d3d9ex?"](https://github.com/elishacloud/dxwrapper/discussions/105)
  — elishacloud. The `D3d9to9Ex` option, the MANAGED → DEFAULT + DYNAMIC strategy credited to
  Special K, the 7-of-8 result, and the four named failure modes.
- [elishacloud/DirectX-Wrappers](https://github.com/elishacloud/DirectX-Wrappers) — the interface
  wrapper headers the above builds on.

## Cross-project note

Nothing in this is UE3- or Enslaved-specific — it is a property of the D3D9 API and of any
`d3d9.dll` proxy. A pointer has been filed to `flat-to-vr-cross-engine-research/inbox/` for `/sr`,
because every D3D9 project in the estate that eventually wants a shared texture on the compositor
side hits this identical wall, and the answer is the same for all of them.
