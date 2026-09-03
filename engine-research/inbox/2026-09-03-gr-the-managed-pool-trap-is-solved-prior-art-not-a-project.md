# §9's `D3DPOOL_MANAGED` trap is solved prior art — the instrumented launch is a sizing measurement now

**From:** `/gr` (2026-09-03, estate sweep)
Supersedes: ENGINE-DOSSIER.md §9 — the sentence *"it is the difference between a one-line proxy
change and a resource-remapping project"*, and the framing "decide after the `D3DPOOL_MANAGED`
instrumented launch"
**Topic:** [`external-research/topics/2026-09-03-the-d3d9ex-upgrade-is-a-solved-bounded-proxy-problem.md`](../../external-research/topics/2026-09-03-the-d3d9ex-upgrade-is-a-solved-bounded-proxy-problem.md)

## The dossier line this answers

> **`D3DPOOL_MANAGED` does not exist on a D3D9Ex device.** […] So the upgrade above is only viable
> if UE3's D3D9 RHI never asks for MANAGED on this build — **unverified, and it is the first thing
> to establish**, because it is the difference between a one-line proxy change and a
> resource-remapping project. `[reported]`

The fact is correct. The **dichotomy** is not — there is a third option, and it is the one the D3D9
wrapper community standardised on.

## The three facts, in order

1. **MANAGED really is invalid on 9Ex.** Microsoft's `D3DPOOL` reference, differences box:
   *"D3DPOOL_MANAGED is valid with IDirect3DDevice9; however, it is not valid with
   IDirect3DDevice9Ex."*
2. **But MANAGED exists to survive device loss, and 9Ex has none.** Same page: applications should
   use MANAGED for most static resources *"because this saves the application from having to deal
   with lost devices"*. And "Lost Devices (Direct3D 9)": *"A Direct3D 9Ex device never returns
   D3DERR_DEVICELOST."* So the pool was not withdrawn arbitrarily — on 9Ex it has nothing left to
   do, and rewriting it away is the migration the design implies rather than a corruption of
   semantics.
3. **The one thing that genuinely changes is lockability.** DEFAULT textures *"cannot be locked
   unless they are dynamic textures"*, whereas managed ones can. **That is why the established
   rewrite is `MANAGED → DEFAULT + D3DUSAGE_DYNAMIC`, not plain DEFAULT** — and the same page's
   pool × usage table confirms DEFAULT × DYNAMIC is legal while MANAGED × DYNAMIC is not, so the
   rewrite can never collide with a flag the engine already set.

`[reported 2026-09-03]`, all three from Microsoft's own reference pages.

## The prior art, with a number attached

`elishacloud/dxwrapper` implements exactly the upgrade §9 describes — a `D3d9to9Ex` option handing a
legacy game an Ex device through the base interface — and its maintainer states the pool handling
outright: **override MANAGED to DEFAULT + DYNAMIC, following Special K's strategy**, which
*"opened up a lot more games"*; **7 of 8 tested worked**. `[reported 2026-09-03]`

So the translation is a handful of lines in the proxy's existing `CreateTexture` /
`CreateVertexBuffer` / `CreateIndexBuffer` wrappers, with two public implementations as evidence.

## Suggested dossier changes

1. **§9, the MANAGED trap:** keep the fact, replace the dichotomy. Suggested: *"MANAGED is invalid
   on 9Ex, but this is solved generically — rewrite `MANAGED → DEFAULT + D3DUSAGE_DYNAMIC` in the
   proxy's Create\* wrappers (the DYNAMIC usage is what preserves lockability). Public prior art:
   dxwrapper's `D3d9to9Ex`, after Special K, 7/8 games. Whether UE3 asks for MANAGED therefore sizes
   the change, it does not gate it."*
2. **§9, replace the single unknown with the real risk list** reported by the same source, since
   these are what actually decide whether this build cooperates: no paletted textures on 9Ex;
   16-bit textures only work in SYSTEMMEM; D3DX functions remain problematic (relevant — this is a
   2010-era UE3 build with a D3DX dependency chain); some titles fail outright at device creation.
   All four are cheap to observe on the first Ex launch.
3. **§9, the two-route decision:** it no longer needs to wait on the instrumented launch. Route (a)
   D3D9+Ex keeps **the proven `SetVertexShaderConstantF(0,…,4)` hook that has already produced a
   stereo picture**; route (b) `-d3d10` discards it for an undesigned cbuffer injection point, and
   its main appeal was that (a) looked blocked on an unknown. It is not. Suggested wording: *"try
   (a) first; (b) remains the fallback if one of the four named 9Ex limits bites."*

## Suggested board change

The `[FLAT]` row *"instrument one launch for `D3DPOOL_MANAGED` to settle whether the D3D9Ex upgrade
is a one-liner or a project"` should stay, but **its purpose and priority both change**: it now
measures how much `Lock()` traffic gets re-pointed (risk sizing), not whether the route exists. It
is still worth riding along on a launch that is happening anyway; it should no longer be something
the Ex decision waits for. That is one fewer prerequisite in front of the Ex upgrade.
