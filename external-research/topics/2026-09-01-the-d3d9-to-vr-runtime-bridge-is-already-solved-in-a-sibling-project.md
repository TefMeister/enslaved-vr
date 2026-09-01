# The D3D9→VR-runtime submission risk is already researched — in a sibling project on this account, down to the gotcha that bites this exact pairing

**Status:** 🆕 new · **Priority:** medium now, high the moment a frame needs submitting. This targets
`ENGINE-DOSSIER.md` §9's second open risk verbatim: *"**D3D9 + modern VR runtimes:** the compositor
submission path from a D3D9 game needs a D3D9Ex/D3D11 texture-sharing bridge — known-solvable (prior
art exists), but it is extra plumbing to plan for."*

**It is solvable, the prior art is Microsoft's own documentation, and the specific trap in it has
already been found and written up by `far-cry-2-vr` — which is on Dunia, a different engine, but the
same Direct3D 9.** This topic exists so that plumbing is not researched twice.

## The technique, and it is a documented interop path rather than a hack

Microsoft's *"Surface Sharing Between Windows Graphics APIs"* explicitly covers **D3D9Ex ↔ D3D11**
sharing. The shape:

1. Create the shared texture as a **D3D11** resource with `D3D11_RESOURCE_MISC_SHARED`.
2. Get its `HANDLE` via `IDXGIResource::GetSharedHandle`.
3. Open that handle from the D3D9Ex side with `IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)`.
4. The game's own D3D9Ex device then renders — or `StretchRect`s from its backbuffer — **directly
   into the shared surface**, with no CPU round-trip. The D3D11 side hands it to the VR runtime.

## 🪤 The gotcha, which is specific to this pairing and is the reason this topic is worth reading

**`D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` — the "clean" cross-API synchronisation primitive that is
normally the recommended answer — is not understood on the D3D9 side at all.** There is no
`IDirect3D9KeyedMutex` equivalent. So the standard answer to *"how do I know the other API has
finished with this surface"* is **simply unavailable to a D3D9Ex producer**.

The established alternative, for this specific gap, is an **`IDirect3DQuery9` event query** on the
D3D9 side to know when a copy has landed (or a `Flush` plus a frame of latency tolerance), combined
with **double- or triple-buffering** so the D3D11/OpenVR side is never reading the surface the game
is writing.

This is exactly the kind of thing that costs a day: the obvious primitive is well-documented,
universally recommended, and silently inapplicable here.

## A second finding from the same sibling that applies to any D3D9 stereo submission

**OpenVR issue #1253** (open, no Valve fix recorded) documents that
`IVRCompositor::Submit(..., Submit_TextureWithPose)` — the mechanism that is *supposed* to let each
eye carry its own pose — **only keeps the pose from whichever `Submit` call happened last** on
SteamVR. Submit left then right and only the right eye's pose is honoured. It is a compositor-level
gap, not fixable from the application side, and the reported consequence is **severe ghosting**. It
works correctly on the Oculus/Meta runtime, which has an explicit per-eye `RenderPose` field.

**Why it matters before any code is written here:** it means an alternate-eye design that tags each
eye with its own independently-timed pose will not behave as documented on SteamVR. The sibling
project's response was to **double-buffer both eye textures and submit them together** rather than
racing per-eye pose timing — and this finding is *why* that is the right call rather than merely a
tidy one.

## Why this is a genuinely cheap win for this project specifically

This project is in an unusually good position on everything *upstream* of submission. §4 was settled
statically on 2026-09-01: there **is** a shared view-projection at `c0`–`c3`, the world-space camera
position is handed over directly at `c4`, and `SetVertexShaderConstantF(StartRegister == 0,
Vector4fCount == 4)` is a clean single injection point for a per-eye offset. So the camera half of
the problem is unusually tractable here, and **submission is the part left to plan.**

Reading a sibling's already-published research is strictly cheaper than rediscovering Microsoft's
interop docs and then finding the keyed-mutex gap the hard way.

## What is NOT established, and where the two projects genuinely differ

- **None of this has been run on Enslaved**, and the sibling has not run it either — its own note is
  research for a roadmap item, not a shipped bridge. `[reported]` throughout.
- **The two projects differ in what they are submitting.** The sibling reaches the shared surface
  from its own backbuffer via `StretchRect`; a per-eye design here would want to render into the
  shared texture directly. The interop mechanism is identical, the copy step is not.
- **Whether Enslaved's device is D3D9 or D3D9**Ex** is the first thing to check**, and it is not
  recorded in the dossier. The interop path above **requires D3D9Ex** — plain D3D9 cannot open a
  shared handle. If the game creates a plain `IDirect3D9` device, an extra step is needed (creating
  our own D3D9Ex device, or a different bridge entirely), and that changes the plumbing estimate
  materially. **Check this before planning around the technique.**
- Nothing here touches §9's other risks — the NTEngine divergence, the Bink full-screen movies, or
  whether the shipping build kept its console class.

## Concrete next steps

1. **Determine whether the game creates a D3D9 or a D3D9Ex device** (`Direct3DCreate9` vs
   `Direct3DCreate9Ex`, or a `QueryInterface` for `IDirect3DDevice9Ex` on the device it does create).
   One static check; it decides whether the whole technique above applies unchanged.
2. When submission work starts, **read the sibling's topic first** rather than starting from
   Microsoft's docs — it already carries the keyed-mutex gap and the buffering discipline.
3. Record the answer to (1) in §9 in place of the current open-risk wording, since "known-solvable"
   can then become either "solved, technique named" or "needs an extra device".

## Sources

- **Sibling project research on this account** —
  [`far-cry-2-vr/external-research/topics/2026-08-24-aer-steamvr-ghosting-and-cpu-readback-techniques.md`](https://github.com/TefMeister/far-cry-2-vr/blob/main/external-research/topics/2026-08-24-aer-steamvr-ghosting-and-cpu-readback-techniques.md)
  — §3 (the D3D9Ex↔D3D11 shared-surface technique and the keyed-mutex gap) and §1 (the SteamVR
  per-eye-pose bug). That topic is the primary write-up; this one is a pointer so the work is not
  repeated.
- [Surface Sharing Between Windows Graphics APIs — Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/surface-sharing-between-windows-graphics-apis)
- [OpenVR issue #1253 — `VRTextureWithPose_t::mDeviceToAbsoluteTracking` with alternate eye rendering](https://github.com/ValveSoftware/openvr/issues/1253)
