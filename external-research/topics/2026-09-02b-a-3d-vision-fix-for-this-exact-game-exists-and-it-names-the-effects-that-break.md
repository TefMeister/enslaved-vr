# A 3D Vision fix for this exact game exists — and it names the effects that break in stereo

**Status:** 🆕 new · **Priority:** ⭐ high — it corrects a claim in this lane's own 2026-08-24 topic,
and it answers the board's live `[FLAT]` question ("which effects stay put while the world rocks?")
from a source that had to fix precisely those effects thirteen years ago.

## ⛔️ First, a correction to this lane's own record

`topics/2026-08-24-ue3-native-stereo-and-community-tooling.md` states:

> No UE3-era stereo-3D fix community (Helix Mod / 3DMigoto / DarkStarSword's `3d-fixes` GitHub repo
> …) has an Enslaved entry.

**That is wrong.** `[disproved 2026-09-02]` A Helix Mod fix for *ENSLAVED: Odyssey to the West
Premium Edition* has existed since **2013-10-28**, updated **2013-12-21**, by **eqzitara**, installed
into the same `Binaries\Win32\` folder our proxy occupies. The earlier pass searched the GitHub
`3d-fixes` repository and the wrong blog index; the fix lives on the Helix Mod blog itself. The
"greenfield, nobody has published camera-level work on this game" conclusion in that topic stands
only for *camera* work — **stereo-correction work on this exact binary was published and is
readable.**

## What the fix had to repair, and why that is a prediction for us

`[reported 2026-09-02, from the fix's own page]` It lists as fixed: **shadows, crosshairs, visual
effects, menu screens**, plus dynamic per-scene convergence. Left unfixed: *"Hud related [some
elements are at different depth]"*.

Set that beside the board's own open items and the overlap is exact:

| The fix had to repair | Our board already predicted |
| --- | --- |
| shadows | the 310 pixel-stage shaders reading an un-offset `ViewProjectionMatrix` at ps `c3`/`c10` |
| "visual effects" | same |
| crosshair / HUD depth (and HUD *stayed* broken) | `[PD]` skip orthographic `c0` uploads so the HUD stops wobbling |
| menu screens | the UI ortho `c0` the run-6 log captured |

**This is independent corroboration that the vertex-only offset is not sufficient on this game** —
not a hypothesis any more but the thing a previous stereo implementation on this binary had to spend
a fix on. `[reported]`

## ⭐ The single most actionable line: motion blur must be off

The fix requires **motion blur disabled** — via the in-game option, or by setting `MotionBlur = False`
in `MonkeyEngine.ini`. `[reported 2026-09-02]`

Motion blur is a screen-space, reprojection-style effect: it reconstructs where a pixel *was* using
the view-projection, which on this build is the pixel-stage copy our proxy does not touch. A per-eye
world with a mono motion-blur reprojection smears each eye toward the other's history — a strong,
specific candidate for "looks wrong and nobody knows why". **Turn motion blur off before the next
stereo run**, so the retune is not judged through it. This costs nothing and removes a confound.

## The convergence hotkeys say something about scene structure

The fix binds **F3 to cinematic depth/convergence and F4 to gameplay depth/convergence** separately,
with automatic convergence switching after the tutorial. `[reported]` That a fixer needed *two*
convergence regimes says the cutscene camera and the gameplay chase camera sit at materially
different depth scales — worth knowing before comfort tuning, and consistent with a chase-cam game
whose cinematics frame much closer.

## What this does not give us

The fix is a shader-override package for the discontinued 3D Vision driver stack, and its DLL sits
where our proxy sits. It is **study material, not a component**: we take the *list of what breaks*
and the *motion-blur constraint*, not its files, and the two must not be installed together.

## Concrete next steps

1. **Before the next stereo run:** set `MotionBlur = False` in `MonkeyEngine.ini`.
2. On that run, judge reflections, water, decals and **shadows** specifically — shadows are now the
   highest-prior candidate, not a general "watch for anything odd".
3. When the pixel-stage twin hook is built, treat the fix's list as its acceptance test.

## Sources

- https://helixmod.blogspot.com/2013/10/enslaved-odyssey-to-west.html — eqzitara's 3D Vision fix for this game (2013-10-28, updated 2013-12-21)
- https://www.vorpx.com/forums/topic/enslaved-odyssey-to-the-west/ — vorpX community profile: Geometry 3D works in all modes with head tracking, but *cinema is the default recommendation because of mouse/camera issues* `[reported]`
