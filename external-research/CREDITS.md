# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and creative work of many people who came before us. None of
this would be possible without them. We list every source, tool, and prior
work we have drawn on below — by name or handle, as accurately as we could
verify it — including those that helped only as inspiration.

## The original game

Enslaved: Odyssey to the West (2010; Premium Edition PC port 2013) is the
creative work of its developer and publisher. We are only modding it; we did
not make it, and all rights to the game and its assets belong to their
owners. **No game files, code, or assets are distributed in any of this
project's repositories.**

| Work | Creator(s) | Note |
|---|---|---|
| Enslaved: Odyssey to the West, original game | Ninja Theory (developer); BANDAI NAMCO (publisher) | Built on Unreal Engine 3 with Ninja Theory's custom engine layer. |
| Premium Edition PC port (2013) | QLOC (port work, as commonly credited); BANDAI NAMCO | The version this project targets. |
| Unreal Engine 3 (the base engine) | Epic Games | The foundation Ninja Theory built on. |

## Tools, frameworks, and prior research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| REFramework / UEVR (D3D VR-injection methodology and reference) | praydog | https://github.com/praydog |
| MinHook (function-hooking library) | Tsuda Kageyu (TsudaKageyu) and contributors | https://github.com/TsudaKageyu/minhook |
| R.E.A.L. VR mods (alternate-eye D3D injection approach, inspiration) | Luke Ross | https://www.patreon.com/realvr |
| Vireio Perception (open-source D3D9 stereo injection, prior art for the D3D9 route) | Cybereality and the Vireio contributors | https://github.com/OpenVR-Advanced-Settings/Vireio-Perception |
| Helix Mod (D3D9 stereo shader-hacking methodology, inspiration) | Helix and the 3D Vision modding community | https://helixmod.blogspot.com |
| vorpX (proof that UE3/D3D9 titles can render stereo, inspiration) | Ralf Ostertag | https://www.vorpx.com |
| x64dbg (debugger) | Duncan Ogilvie (mrexodia) and contributors | https://x64dbg.com |
| Ghidra (static analysis) | NSA Research | https://ghidra-sre.org |
| OpenVR / SteamVR and OpenXR (VR runtimes) | Valve; The Khronos Group | https://github.com/ValveSoftware/openvr |
| UE3 community documentation (INI/console/cvar knowledge) | Epic Games and the wider UE3 modding community | https://docs.unrealengine.com |
| NVIDIA 3D Vision / UE3 stereo announcement (background research) | NVIDIA | https://www.nvidia.com |
| Epic Developer Community Forums (UE3 3D Vision failure-mode research) | Epic Games forum community | https://forums.unrealengine.com |
| PCGamingWiki (game-specific config/fix research) | PCGamingWiki contributors | https://www.pcgamingwiki.com |
| FearLess Revolution / CheatHappens / Plitch / GameCopyWorld (trainer prior-art research) | Respective site communities | https://fearlessrevolution.com |
| 3d-fixes (checked for UE3 stereo prior art) | DarkStarSword | https://github.com/DarkStarSword/3d-fixes |
| "Surface Sharing Between Windows Graphics APIs" and the `D3DPOOL` reference | Microsoft Learn | https://learn.microsoft.com/en-us/windows/win32/direct3darticles/surface-sharing-between-windows-graphics-apis |
| Special K wiki (D3D9 wrapper compatibility notes; not readable by automated fetch this pass) | Kaldaien and the Special K community | https://wiki.special-k.info/ |

(Matches the credit list already established in `enslaved-vr-engine-research`
as of this repo's creation — kept in sync going forward.)

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
