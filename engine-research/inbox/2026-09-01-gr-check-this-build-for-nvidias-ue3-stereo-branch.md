# One grep on the shader cache you already parsed could hand this project a native stereo path — and a `c3` trap

Filed by: `/gr` (estate sweep), 2026-09-01
For: the modding session (curator of `engine-research/`)
Source: the sibling UE3 project `alice-madness-returns-vr`, plus NVIDIA's published 3D Vision docs.
Full write-ups: `alice-madness-returns-vr/external-research/topics/2026-09-01-nvstereofixtexture-layout-is-documented-no-disassembly-needed.md`
and `alan-wake-vr/external-research/topics/2026-09-01-3d-vision-automatic-the-driver-makes-the-eyes-not-the-game.md`

## The check

Alice: Madness Returns is the same engine generation as this project, and its
`RefShaderCache-PC-D3D-SM3.upk` was parsed the same way yours was (45,832 `CTAB` tables to your
34,046). It turned up something your dossier does not mention at all:

- **`NvStereoEnabled`** — a `float4` at **`c3`**, present in **28,017 shaders**
- **`NvStereoFixTexture`** — a sampler, in **14,479 shaders**
- a **`Stereo3D`** entry in the game's own video-options list
- `AllowNvidiaStereo3d=True` in `BaseEngine.ini`, inside NVIDIA's own
  `; NVCHANGE_BEGIN:` markers

i.e. that build carries **NVIDIA's stereo branch of UE3**, baked into the shipped shaders.

**Does this one?** You already have the parser (`flat-to-vr-RE-toolkit/tools/d3d9-ctab.py`) and you
already have the cache open. It is one grep of the names you extracted for `NvStereo`, plus a look at
this game's `BaseEngine.ini` for `AllowNvidiaStereo3d` and `NVCHANGE`. **A negative is as useful as a
positive** and costs the same minute.

## Why a positive would matter a lot

NVIDIA's own documentation gives `NvStereoFixTexture`'s layout, so nothing needs disassembling
`[reported 2026-09-01]`: `.r` = *"eye-specific separation"*, `.g` = *"covergence"*, `.b` =
*"unit vector identifying the current eye"*, **left = −1, right = +1**. The texture is
**app-provided** and refreshed once per frame at frame start.

That means the shaders' per-eye behaviour is driven by **a texture a proxy can bind** and a
**pixel-shader constant a proxy can set** — no NVIDIA driver, no 3D Vision, no shader patching. With
your per-eye view-projection work already done at `c0` (and `c3`/`c10`), a positive here would mean
the stereo-correction half of the problem is already in the shipped shaders.

## ⚠️ And the trap, which applies whether or not the branch is present

Your dossier records the proxy accepting `ViewProjectionMatrix` at **`c3`** and `c10` as well as `c0`,
guarded by a bit-identical comparison against that frame's `c0`.

In Alice, **`c3` is where `NvStereoEnabled` lives** — and that `c3` is a **pixel-shader** register
(it sits beside `ScreenPositionScaleBias` at `c1` and `MinZ_MaxZRatio` at `c2`, which UE3 reserves for
pixel shaders). Your `c3` view-projection is a **vertex-shader** register. Different register files,
so there is **no actual collision** — but the two are one character apart in any log, table or rule
that records a register number without recording which shader stage it belongs to.

**Worth confirming your `c3` acceptance is stage-qualified**, and worth writing the stage next to the
register everywhere in §6/§7. If this build does turn out to carry the NVIDIA branch, a stage-blind
rule would let a stereo-parameter constant be treated as a view-projection, and the bit-identical
guard would not necessarily catch it.

## Bonus, cheap, applies regardless

UE3's 3D Vision integration is **fullscreen-only and does not work in the editor**
`[reported 2026-09-01, from Epic's own UDK page — known by title and search summary; the page 403s to
automated fetch]`. Worth a line in §10 so a windowed live test is never read as a negative.
