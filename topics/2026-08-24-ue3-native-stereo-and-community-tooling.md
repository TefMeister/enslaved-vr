# UE3's native "3D Vision" stereo path (why to skip it) + what public tooling already exists for this game

**Status:** 🆕 new — informational; nothing here requires a live-game test, and nothing found blocks
or unblocks the live capture directly.

Pure public-research pass (web search/fetch only, zero game execution). Focus, per
`enslaved-vr-modding-notes/00-status.md` session 3: the pivotal open question is whether Enslaved's
D3D9 vertex shaders carry a **shared per-frame view-projection constant register**, or bake the camera
into **per-object WorldViewProjection matrices** (the resume point is a live capture with the
SHARED-matrix-detecting proxy — that capture is still the only way to actually answer it). This pass
looked for public information that could shortcut or inform that question, and for any existing
camera/stereo work on this exact game.

## 1. Unreal Engine 3 has a native "NVIDIA 3D Vision Direct" stereo mode — but it's a dead end for VR, not a shortcut

UE3 ships a built-in stereo toggle, `AllowNvidiaStereo3d=True` (engine.ini, documented at
`docs.unrealengine.com/udk/Three/ThreeDVision.html`; Epic/NVIDIA jointly announced this for UE3 in
2010 — the NVIDIA press release specifically credits **Batman: Arkham Asylum** as a showcase title).
It sounds like it could be relevant (an engine-level per-eye camera path already built into UE3), but
digging into how it actually works rules it out as a VR mechanism:

- It is **NVIDIA's driver-level "automatic stereo"** blit correction, not an engine-side second camera
  render. The engine flags eligible pixel-shader constants (**`NvStereoEnabled`** at constant register
  c3, plus a **`NvStereoFixTexture`** sampler at s1) so the NVIDIA 3D Vision driver can apply its
  per-pixel parallax-shift formula to the final image based on depth. There is no independent per-eye
  view/projection matrix pair anywhere in this path, no asymmetric frustum, and critically **no head
  tracking** — it's fixed-parallax stereo for glasses, built for a 2D depth-shift, not a 6DOF headset.
  Even if it worked flawlessly it would not give us what a VR mod needs.
  Source: NVIDIA/Epic 2010 press release (`nvidia.com/ja-jp/about-nvidia/press-releases/2010/...`);
  Epic Developer Community forum thread "[UE3] 3D Vision Issues".
- It also requires real 3D Vision hardware (IR emitter + shutter glasses) and the legacy NVIDIA 3D
  Vision driver stack, both effectively defunct on current GPUs/drivers — not something reachable on
  either project machine even for a quick experiment.
- It's known to actively **break rendering** in some UE3 titles when enabled. A detailed developer
  account (Epic forum thread, re: *Life Is Strange*, also UE3) describes the failure mode precisely:
  newer UE3 versions moved to reading screen position from the `vPos` semantic (already correct), but
  the driver's stereo-correction formula still gets applied on top of it when `NvStereoEnabled` is set,
  double-correcting and breaking fog, shadows, light shafts, bloom, ground reflections, and decal
  clipping across roughly 3,000 shaders in that game until `NvStereoEnabled` was manually disabled on
  every `vPos`-using shader.
- **Weak, indirect relevance to the actual open question:** that `vPos`-vs-driver-correction conflict
  is a pixel-shader-level detail (screen-position semantics), not proof about vertex-shader WVP
  register layout — so it doesn't answer SHARED-vs-per-object for Enslaved's vertex shaders. It's only
  a soft signal that UE3-era titles in this generation already have non-trivial, per-shader-customized
  handling around camera/screen-position rather than one clean global path.

**Bottom line:** don't spend time testing `AllowNvidiaStereo3d` in Enslaved's ini — even if it's
compiled into this build, it's the wrong mechanism for a headset and has a documented history of
actively breaking things in sibling UE3 titles. Confirms the project's own `d3d9.dll` proxy /
manual-matrix-injection route (already underway) is the correct path — there's no engine-native
shortcut to skip it with.

## 2. No existing camera, free-cam, or stereo/3D mod found for this exact game — greenfield confirmed

Checked for prior art specifically on Enslaved: Odyssey to the West (Steam/Premium Edition, the
version this project targets):

- **PCGamingWiki** (`pcgamingwiki.com/wiki/Enslaved:_Odyssey_to_the_West`) confirms the FOV/widescreen
  fix in circulation is a **Widescreen Fixer plugin** (third-party ASI tool, not studied/used here —
  described only, per the no-copy rule) that edits `MonkeyHUDWidgets.ini` under the same per-user
  config path this project already found (`Documents\My Games\UnrealEngine3\MonkeyGame\Config`, "v1.1.1
  - Steam" plugin profile). It targets HUD/aspect stretching, not the 3D camera FOV directly, and does
  it through config rather than a memory patch — consistent with (not contradicting) the project's own
  finding that the game exposes a normal, stock-UE3 camera/console surface rather than something
  NTEngine heavily walled off.
- **Cheat Engine trainers exist** (FearLess Revolution `t=12617`/`t=2896`/`t=3874`, CheatHappens,
  Plitch, GameCopyWorld) — feature lists found (via search snippets; FearLess Revolution 403s automated
  fetches, so these weren't read directly) are standard trainer fare: unlimited health/shield, easy
  kills, tech-credits, **teleport, and save/load position**. Teleport + position save/load confirms a
  findable player-position pointer (unsurprising for any UE3 `AActor.Location`), but **no camera hack,
  free-cam, or FOV-memory-patch feature was found in any listing** — nobody has published camera-level
  work on this game.
- No UE3-era stereo-3D fix community (Helix Mod / 3DMigoto / DarkStarSword's `3d-fixes` GitHub repo,
  which has folders for many D3D9-era UE3-adjacent titles) has an Enslaved entry.

**Bottom line:** this really is greenfield — the project isn't missing a public camera/stereo lead for
this specific game, it's genuinely ahead of anything published. The live in-game capture (session 3's
resume point) remains the only path to the SHARED-vs-per-object answer.

## Sources (see [CREDITS.md](../CREDITS.md) for the full standing credit)

- Epic Games — UE3 `ThreeDVision.html` UDK documentation (native 3D Vision config keys).
- NVIDIA / Epic Games — 2010 joint press release on UE3 NVIDIA 3D Vision support (Batman: Arkham
  Asylum as showcase title).
- Epic Developer Community Forums — "[UE3] 3D Vision Issues" thread (Life Is Strange `vPos`/
  `NvStereoEnabled` failure-mode writeup).
- PCGamingWiki — Enslaved: Odyssey to the West page (Widescreen Fixer plugin behavior, config path).
- FearLess Revolution, CheatHappens, Plitch, GameCopyWorld — Enslaved trainer feature listings (via
  search snippets only).
- DarkStarSword — `3d-fixes` GitHub repo (checked for prior art; no Enslaved entry found).
