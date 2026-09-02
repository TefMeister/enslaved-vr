# The `rejected` `c0` population is statically enumerable — the shader cache already names what else lives at `c0`

**Status:** 🆕 new · **Priority:** medium-high — it turns the board's `[PD]` item *"classify the
`rejected` count"* from a live-log exercise into an off-disk enumeration, and it needs no launch.

## The open item

The board records that the proxy's `rejected N as not-a-viewproj` counter went from a steady
840 per 120 frames to a scene-dependent 680–4,259 after the re-index, and reads those as *"`c0`
uploads with a zero row 0, i.e. global-shader params sharing `c0`, not VPs"* `[inferred-static]`.

**That reading can be confirmed and made exhaustive from the shader cache the project has already
parsed**, rather than by classifying matrices in a log.

## The arithmetic that makes it a static question

The dossier records, from `RefShaderCache-PC-D3D-SM3.upk` via `d3d9-ctab.py`:

- **34,046 constant tables** in total, and
- **`ViewProjectionMatrix` at `vs_3_0` `c0` in 3,325 vertex shaders — "every one"**, i.e. every
  vertex shader that *declares* the constant puts it at `c0`, with no exceptions.

The second figure counts shaders that declare `ViewProjectionMatrix`. It does **not** count the
vertex shaders that do not. Those are the interesting ones: a vertex shader with no view-projection
still has a `c0`, and whatever it declares there is uploaded through the same
`SetVertexShaderConstantF(0, …)` call the hook watches. **That population is the `rejected` count.**

So the classification is two queries against a file already on disk:

1. **How many `vs_3_0` tables are in the cache in total?** Subtract 3,325 and you have the size of
   the non-view-projection population. (Alice, the sibling UE3 title, is 2,431 of 2,807 vertex
   shaders — 13% do not carry it — so a non-trivial remainder here is expected, not surprising.)
2. **For those tables, what is declared at `c0`?** `CTAB` names it. That converts "global-shader
   params, probably" into a list of actual constant names — and any name that turns out to be a 4×4
   matrix at `c0` deserves attention, because it would upload through the hook looking exactly like a
   view-projection.

## Why this is worth doing before more live runs

The board's own concern is that the count is **scene-dependent** (680–4,259). A static enumeration
explains that without needing to reproduce a scene: different scenes draw different shader sets, so
the count tracks how many non-view-projection vertex shaders that scene happens to use. If the static
list is small and clearly unrelated (post-process, UI, sky), the counter is noise and can be
downgraded to a debug statistic. If it contains anything matrix-shaped, that is a real hazard the
guard needs to know about.

It also feeds the **other** open `[PD]` item directly: the ortho-`c0` skip
(`float[11]==0 && float[15]==1`). The same enumeration says whether orthographic uploads are the only
non-perspective thing arriving at `c0`, or one of several.

**Caveat, stated plainly:** the cache is the *reference* shader cache. If the game compiles or loads
shaders outside it, the enumeration is a lower bound rather than the whole population. The project has
already read all three `RefShaderCache` caches and the three `GlobalShaderCache` bins for the
`nvstereo` check, so the same sweep covers this.

## ✅ Confirmed while this was being written: the world scale is ~1 unit per centimetre

The live session measured it at 16:10 (`dev-archive`, runs 6–7). That lands on the **lower end of the
1–2 cm bracket** this lane filed earlier the same day, and it settles the separation question:
`Separation = 6.0` is **≈ 6 cm**, against a human interpupillary distance of about 6.4 cm — so the
value already in the ini was close to correct, and the reported "very quick left-right teleport, not a
big gap" was the right appearance rather than a symptom. `[measured 2026-09-02, live session]`
The 10× test remains worth running as a **linearity check**; it was never a target value.

## Sources

- This project's own `ENGINE-DOSSIER.md` §4 (the CTAB figures) and `dev-archive/recon/2026-09-02-ctab-stage-and-nvstereo-check/`
- `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py` — the tool that produced them
- The live scale measurement: this project's `dev-archive` runs 6–7, 2026-09-02
