# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and creative work of many people who came before us. None of
this would be possible without them. We list every source, tool, and prior
work we have drawn on below — by name or handle, as accurately as we could
verify it — including those that helped only as inspiration.

If we have missed someone, the omission is a mistake, not a slight. Please see
the "Get credited, or ask us to stop" section at the bottom.

## The original game

Enslaved: Odyssey to the West (2010; Premium Edition PC port 2013) is the
creative work of its developer and publisher. We are only modding it; we did
not make it, and all rights to the game and its assets belong to their owners.
No game files are included anywhere in this repository.

| Work | Creator(s) | Note |
|---|---|---|
| Enslaved: Odyssey to the West, original game | Ninja Theory (developer); BANDAI NAMCO (publisher) | Built on Unreal Engine 3 with Ninja Theory's custom engine layer. |
| Premium Edition PC port (2013) | QLOC (port work, as commonly credited); BANDAI NAMCO | The version this project targets. |
| Unreal Engine 3 (the base engine) | Epic Games | The foundation Ninja Theory built on. |

## Tools, frameworks, and prior research this project builds on

| Source / Work | Creator(s) | Link |
|---|---|---|
| REFramework / UEVR (D3D VR-injection methodology and reference) | praydog | https://github.com/praydog |
| MinHook (function-hooking library) | Tsuda Kageyu (TsudaKageyu) and contributors | https://github.com/TsudaKageyu/minhook |
| R.E.A.L. VR mods (alternate-eye D3D injection approach, inspiration) | Luke Ross | https://www.patreon.com/realvr |
| Vireio Perception (open-source D3D9 stereo injection, prior art for the D3D9 route) | Cybereality and the Vireio contributors | https://github.com/OpenVR-Advanced-Settings/Vireio-Perception |
| Helix Mod (D3D9 stereo shader-hacking methodology, inspiration) | Helix and the 3D Vision modding community | https://helixmod.blogspot.com |
| vorpX (proof that UE3/D3D9 titles can render stereo, inspiration) | Ralf Ostertag | https://www.vorpx.com |
| x64dbg (debugger used throughout) | Duncan Ogilvie (mrexodia) and contributors | https://x64dbg.com |
| Ghidra (static analysis) | NSA Research | https://ghidra-sre.org |
| OpenVR / SteamVR and OpenXR (VR runtimes) | Valve; The Khronos Group | https://github.com/ValveSoftware/openvr |
| UE3 community documentation (INI/console/cvar knowledge) | Epic Games and the wider UE3 modding community | https://docs.unrealengine.com |

Community knowledge from years of UE3 modding forums, wikis, and write-ups
informs almost every step of this work, even where no single author can be
pinpointed. Thank you.

## Get credited, or ask us to stop

- If you should be credited here and are not, or are credited incorrectly,
  email us at **td3kxlvr@proton.me** and we will fix it as soon as possible.
- We honour correction and removal requests from the actual rights holders of
  anything used here, promptly, via the same address.

---

*This root credits file was promoted on 2026-08-31 from the identical copies that already
sat in `dev-archive/` and `engine-research/`, so the project's credits are visible from the
repository's front page rather than only one folder in. The folder copies remain; the
`external-research/` one carries extra research-lane entries.*
