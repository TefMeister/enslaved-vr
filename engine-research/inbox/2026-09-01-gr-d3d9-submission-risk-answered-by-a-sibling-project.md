# §9's D3D9→VR-runtime risk is already answered — by `far-cry-2-vr`, and it carries a trap

**From:** `/gr`, 2026-09-01 (estate-wide sweep)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §9.
**Full write-up:** `external-research/topics/2026-09-01-the-d3d9-to-vr-runtime-bridge-is-already-solved-in-a-sibling-project.md`

## The dossier text this targets

§9: *"**D3D9 + modern VR runtimes:** the compositor submission path from a D3D9 game needs a
D3D9Ex/D3D11 texture-sharing bridge — known-solvable (prior art exists), but it is extra plumbing to
plan for."*

The prior art is on this account. `far-cry-2-vr` is a different engine on the same Direct3D 9, and
its lane researched this on 2026-08-24, including the part that would otherwise cost a day.

## The technique

Microsoft's documented **D3D9Ex ↔ D3D11** surface sharing: create the texture on the **D3D11** side
with `D3D11_RESOURCE_MISC_SHARED`, get its `HANDLE` from `IDXGIResource::GetSharedHandle`, open it
from D3D9Ex with `IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)`. The game's device then
renders or copies straight into the shared surface — **no CPU round-trip**. It is an intentional,
Windows-documented interop path, not a hack.

## 🪤 The trap, and it is the reason this drop exists

**`D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` — the primitive normally recommended for exactly this
job — has no D3D9-side equivalent whatsoever.** There is no `IDirect3D9KeyedMutex`. The obvious,
well-documented, universally-suggested synchronisation answer is simply unavailable to a D3D9Ex
producer.

The established alternative: an **`IDirect3DQuery9` event query** on the D3D9 side to know when a
copy has landed (or `Flush` plus a frame of latency tolerance), **plus double/triple buffering** so
the runtime never reads the surface the game is writing.

## One more, for any per-eye submission design here

**OpenVR issue #1253** (open, no Valve fix): `Submit(..., Submit_TextureWithPose)` is meant to let
each eye carry its own pose, but **SteamVR keeps only the pose from the last `Submit`**. Submit left
then right and only the right eye's pose is honoured; the reported consequence is severe ghosting.
It works on the Oculus/Meta runtime, which has a real per-eye `RenderPose` field. **Consequence:
submit both eyes together from double-buffered textures rather than racing per-eye pose timing.**

## Suggested dossier change, and the one thing to check first

Replace §9's "known-solvable, extra plumbing" wording with the technique above, the keyed-mutex
trap, and the OpenVR caveat — all `[reported]`, neither project has run it.

**But check this first, because it decides whether any of it applies:** the interop path **requires
D3D9Ex**. Plain D3D9 cannot open a shared handle. The dossier does not record which this game
creates. One static check — `Direct3DCreate9` vs `Direct3DCreate9Ex`, or a `QueryInterface` for
`IDirect3DDevice9Ex` on the device it does create — turns §9's open risk into either "solved,
technique named" or "needs an extra device", and those are very different estimates.

## Why this reached you now

Nothing new was found on the web for it. This is the estate-wide `/gr` sweep holding every project's
dossier at once and noticing that one project's open risk is another's finished research. §4 here was
settled statically on 2026-09-01, so the camera half of this conversion is unusually far along —
submission is the part left to plan, and it does not need planning from scratch.
