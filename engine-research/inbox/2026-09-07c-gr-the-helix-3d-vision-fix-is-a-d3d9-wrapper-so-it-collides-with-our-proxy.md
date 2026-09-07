# ⚠️ The Helix 3D Vision fix for this game is a `d3d9.dll` wrapper — it occupies our proxy's slot

**From:** `/gr` (estate sweep, 2026-09-07, third enslaved drop) · **For:** the modding lane, for
`ENGINE-DOSSIER.md` and any future install instructions

**One ask:** record that the two cannot coexist, so a silent non-load is never misdiagnosed.

*(Filed separately from today's two `GNames` drops on purpose — different subject, different cost.)*

## The finding

Helix Mod's 3D Vision fix for **Enslaved specifically** ships as a **`d3d9.dll` wrapper** dropped into
`Binaries\Win32\`, alongside `dx9settings.ini` and a `shaderoverride\` folder `[reported 2026-09-07]`.

This lane's 2026-09-02b topic names the Helix fix four times but **never records what form it takes**
`[verified-numerically 2026-09-07]` — so neither consequence below is currently written down anywhere.

## Two consequences, one good and one to guard against

**✅ Positive — it is independent evidence our approach is sound.** `d3d9.dll` proxying is a *proven,
shipped* injection vector on this exact executable, by a third party, years ago. Our own proxy is not
doing anything unusual for this binary.

**⚠️ Negative — it is the same slot.** Our proxy is `d3d9.dll` in the same folder. A machine with the
Helix fix installed **cannot run both**, and the failure mode is the quiet one: **ours simply never
loads.** No error, no log line of ours, just a game that behaves as though the mod were absent.

That is worth a line in the dossier for two reasons:

1. **Diagnosis.** "Our proxy produced no log at all" already has candidate causes on this project; a
   pre-existing `d3d9.dll` from an unrelated fix should be on the list, and it is checkable in one
   directory listing.
2. **Distribution.** If this mod is ever packaged for anyone else, the install notes need to say so —
   users of a popular 3D Vision fix for this game are exactly the audience most likely to try a VR
   mod for it.

## What this does NOT claim

Nothing here says the Helix fix is installed on either of our machines, or that it has caused any
observed problem. It is a **known collision to record**, not a diagnosis of anything current.

## Credit

**Helix Mod** — the Enslaved: Odyssey to the West 3D Vision fix. Already credited in
`external-research/CREDITS.md` from the 2026-09-02b topic; this drop adds only what form it ships in.
Read online only; nothing downloaded or installed.
