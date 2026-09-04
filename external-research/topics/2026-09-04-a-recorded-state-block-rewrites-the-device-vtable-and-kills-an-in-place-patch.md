# A recorded state block rewrites the device's method table — the likeliest reason slot 94 dies after a Reset while `Present` and `Reset` survive

**Date:** 2026-09-04 · **Status:** 🆕 new · **Answers:** the board's `[PD]` row *"WHY DOES A DEVICE
RESET DISARM THE STEREO?"* and ENGINE-DOSSIER.md §9a

## The row this addresses

> A Reset makes the proxy record ZERO vertex-shader constant uploads for the rest of the process's
> life (`offset 0, ortho-skipped 0`) `[verified-live 2026-09-03, n=2 resets]` … `Present` and
> `Reset` hooks both survive, and the forced-window logic still re-applies — only
> `SetVertexShaderConstantF` stops being reached. Prime suspect: UE3 re-creating its RHI/device
> objects post-reset onto a vtable our patch no longer covers.

The prime suspect does not fit the evidence, and there is a better-fitting one with two independent
public witnesses. Neither needs the game to check — the discriminating instrumentation is a few
lines in the proxy and a log line to read on the next launch that was going to happen anyway.

## Why "UE3 re-created the device" cannot be it

The proxy (`staging/enslaved-vr/proxy-d3d9/dllmain.cpp`) hooks by **patching the device's vtable in
place** — `PatchVTableEntry` writes `My_Reset`, `My_Present` and `My_SetVSConstF` into slots 16, 17
and 94 of the table the device object points at, once, guarded by `g_deviceHooked`. Two facts
follow from that design, and together they rule the suspect out `[inferred-static 2026-09-04]`:

1. **A D3D9 vtable is shared by every device of the same runtime class.** A second `CreateDevice`
   would return an object pointing at the *same* table, already patched — the hook would keep
   firing. And a second `CreateDevice` would have logged `[CreateDevice]` through `My_CreateDevice`
   regardless of the `g_deviceHooked` guard; the run notes record no such line.
2. **`Present` (slot 17) kept firing after the reset.** `Present` and `SetVertexShaderConstantF`
   live in the same table. If the game had moved to a device with a different table, `Present`
   would have gone silent too. It did not. So after the reset the game is still calling through the
   patched table — and **slot 94 alone no longer points at `My_SetVSConstF`**.

Something rewrote one slot (or one subset of slots) and left the rest alone.

## ⭐ The better-fitting cause: the D3D9 runtime rewrites its own method table when a state block is recorded

Two independent reports, years apart, from people who hooked D3D8/D3D9 device vtables in place and
watched their hooks vanish:

- **gho, author of DxWnd (2014-06-02, updated 06-05):** *"D3DDevice9::BeginStateBlock recover all
  COM method pointers invalidating the hook patching. It's sufficient to hook this method to
  restore back the DxWnd routines."* Found while chasing exactly our symptom — *"the D3D9 methods
  seem to be unhooked"* after a fullscreen/resolution reset. `[reported]`
- **Paul Roussin, on the D3D8 device (Microsoft DirectX newsgroup):** *"If you are going to hook
  the D3D device table that way then you will have to hook calls like BeginStateBlock and
  EndStateBlock. BeginStateblock will reset the device table so you have to make the code return
  control back to you so you can reset your modified addresses."* `[reported]`

The mechanism they describe is simple. `BeginStateBlock` puts the device into recording mode by
**swapping the state-setting methods** (`SetRenderState`, `SetTexture`,
`SetVertexShaderConstantF`, …) for recording versions; `EndStateBlock` puts the **runtime's own
originals** back. The runtime does not know or care that a third party had written into those
slots — it restores from its own prototype. `Present`, `Reset` and `CreateDevice` are not
state-block-recordable, so they are never touched. That is precisely the pattern in the log:
`Present`/`Reset` alive, slot 94 dead, permanently. `[hypothesis]` for *this* game until the
instrumentation below confirms it — but it is the only explanation on the table that predicts
which hooks survive.

**Who records a state block after a reset, when nobody did at startup?** Not UE3 itself: the public
UE3 source mirror's D3D9 RHI contains no `BeginStateBlock`/`CreateStateBlock` call outside the SDK
header (`[inferred-static 2026-09-04]`, one code search). The candidates are the other residents of
the process that rebuild their D3D9 resources on a reset — the Steam overlay's renderer, a driver
overlay, anything using `ID3DXSprite`/`ID3DXFont` (which record state blocks unless told not to).
Any of them re-initialising a couple of seconds after the reset would produce exactly the
observed delay. The proxy's log can name the culprit without guessing — see below.

## ⚠️ One caveat on the "not instantaneous" clue

The board reads *"one more HEALTHY summary prints after the reset"* as proof the killer runs
120–240 frames later. That inference is weaker than it looks: the stereo summary is printed **every
`g_frameInterval` frames and counts "since last summary"**, so a summary printed after the reset
still covers the frames *before* it in the same window. A reset landing mid-window would show
exactly one healthy post-reset summary even if the hook died at the instant of `Reset`.
`[inferred-static 2026-09-04]` from the proxy source. The delay may be real (an overlay
re-initialising lazily), but it should be re-measured with a per-frame stamp, not inferred from a
windowed counter.

## What to do — all `[PD]`, in the order that costs least

1. **Instrument, don't fix, first.** In `My_Present`, compare `vtbl[94]` against `&My_SetVSConstF`
   and log the frame number and the *new* value the first time they differ. If the new value equals
   `orig_SetVSConstF` (the runtime's own function), the runtime restored it — the state-block
   mechanism. If it is some third address, another hooker overwrote us, and the module that owns
   that address (`GetModuleHandleEx` with `FROM_ADDRESS`) names it.
2. **Hook `BeginStateBlock` (slot 60) and `EndStateBlock` (slot 61) to log the frame they fire on**,
   plus the caller module of each. One launch with a checkpoint restart then shows whether the slot
   reverts on the same frame `EndStateBlock` runs — that is the confirmation.
3. **Then choose the durable fix.** Three options, cheapest first:
   - **Self-healing slot:** re-apply the three patches after every `EndStateBlock` returns, and
     re-check them each `Present`. Smallest change, keeps the proven in-place design, and is what
     DxWnd shipped (*"sufficient to hook this method to restore back the DxWnd routines"*).
   - **Code hook instead of vtable hook:** detour the runtime's `SetVertexShaderConstantF` function
     body (the address already saved in `orig_SetVSConstF`) with MinHook, which the estate already
     carries in `far-cry-2-vr`. A code hook is immune to table rewrites because the table still
     points at the (now-detoured) original.
   - **Wrap the device** — return the game a proxy object whose vtable is ours. Immune by
     construction and what ReShade/dxwrapper do, but it means implementing the whole interface;
     not worth it for one slot.

Whichever is chosen, the operational rule in §9a ("read `offset` before trusting a run") stays
until the log shows a reset survived.

## What was NOT found

No public write-up of the d3d9.dll internals that documents the swap at the byte level, and no
statement of exactly which slots the recording mode replaces — the two witnesses agree on the
behaviour, not on the list. Hence `[reported]` for the mechanism and `[hypothesis]` for its
application here; step 1 above converts it to `[verified-live]` with one run.

## Sources

- [DxWnd discussion — "d3d9 Device::Reset troubles!" (gho, 2014-05/06)](https://sourceforge.net/p/dxwnd/discussion/general/thread/9b1c8171/)
  — the BeginStateBlock observation and the re-hook fix.
- [Microsoft DirectX graphics newsgroup — "Hooking D3Device8 by replacing the VTable fails" (Paul Roussin)](https://microsoft.public.win32.programmer.directx.graphics.narkive.com/PbJcO31s/hooking-d3device8-by-replacing-the-vtable-fails-info-needed)
  — the same behaviour on D3D8, with the same remedy.
- [IDirect3DDevice9::BeginStateBlock (Microsoft Learn)](https://learn.microsoft.com/en-us/windows/win32/api/d3d9helper/nf-d3d9helper-idirect3ddevice9-beginstateblock)
  and [EndStateBlock](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-endstateblock)
  — the documented recording model the swap implements.
- [CodeRedModding/UnrealEngine3 (public UE3 source mirror)](https://github.com/CodeRedModding/UnrealEngine3)
  — searched for `BeginStateBlock`/`CreateStateBlock`: no use in the D3D9 RHI. Read online, nothing
  taken.
- Our own `staging/enslaved-vr/proxy-d3d9/dllmain.cpp` — `PatchVTableEntry`, `HookDevice`,
  the `g_deviceHooked` guard and the windowed summary.

## Cross-project note

Every proxy in the estate that patches a D3D8/D3D9 device vtable in place is exposed to the same
rewrite: `manhunt-2003-vr` (`proxy-d3d8`) and `XIII2003-vr` (its `*_hook.cpp` files) do, on the
D3D8 runtime Paul Roussin was describing `[inferred-static 2026-09-04, grep for VirtualProtect]`.
Filed once, engine-agnostic, to `flat-to-vr-cross-engine-research/inbox/`.
