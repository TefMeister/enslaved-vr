# 02 — Static recon

**Session 1, 2026-08-21.** Engine identification from the installed files, no
live run yet.

## Install layout

```
Enslaved\
  Binaries\Win32\Enslaved.exe   (32-bit, ~34 MB)
  Binaries\ntjobcode\
  Engine\{Config,Content,Shaders,Localization,...}
  MonkeyGame\{Config,CookedPC,Localization,Movies,SaveData,ScriptFinalRelease}
  MonkeyGame\PCTOC.txt
```

## Findings

- **Engine:** Unreal Engine 3 (~2009–2010 branch) with Ninja Theory's custom
  **NTEngine** layer. Internal codename **"Congo"** (from assert strings like
  `e:\Projects\Congo\EnslavedMaster\MasterArchives\UnrealEngine3\Development\Src\NTEngine\...`).
  UE3 project name **`MonkeyGame`**.
- **Architecture:** 32-bit (`Binaries\Win32\Enslaved.exe`).
- **Renderer:** **Direct3D 9** active. `AllowD3D10=False` in both
  `Engine\Config\BaseEngine.ini` and `MonkeyGame\Config\MonkeyEngine.ini`.
  D3D10/D3D11 RHI code is compiled in (D3D10CreateDevice, ID3D11ShaderReflection,
  DXGI strings) but config-gated off.
- **Binary is clean and unpacked:** standard PE sections
  (`.text .rdata .data .rsrc .reloc`), no SteamStub, no packer, relocations
  present, and assert strings with full source paths throughout — near
  symbol-quality orientation for static RE.
- **Developer console is bound** in shipping configs: `ConsoleKey=Tilde`,
  `TypeKey=Tab` (`MonkeyInput.ini`, `BaseInput.ini`).
- **Custom viewport client:** `GameViewportClientClassName=NTEngine.NTReplayGameViewportClient`.
- **Camera:** third-person chase camera, data-driven via `MonkeyChaseCamera.ini`
  (speed-FOV present but disabled: `m_useSpeedFoV=false`).
- **Display default (game-dir config):** `Fullscreen=True`, 1280×720.

## Middleware inventory (Binaries\Win32)

- PhysX 2.x: `PhysXCore.dll`, `NxCharacter.dll`, `NxCooking.dll`,
  `physxcudart_20.dll`, `cudart.dll`
- NaturalMotion **Morpheme** (runtime + asset compiler, incl. a PC PDB)
- **Bink** video: `binkw32.dll`, `binkudk.dll`
- FaceFX (`FxGraphLayout.dll`), Fonix TTS (`FonixTtsDtSimple*.dll`)
- Steamworks (`steam_api.dll`, `steam_appid.txt`)
- **`EasyHook32.dll` ships with the game** (plus `AgentInterface.dll`,
  `DebuggerInterface.dll`, `Interop.XDevkit.1.0.dll` — leftover Ninja Theory
  dev/test tooling) — the game's own runtime already tolerates hooking.

## d3d9 imports

The exe imports only four names from d3d9.dll:
`Direct3DCreate9`, `D3DPERF_BeginEvent`, `D3DPERF_EndEvent`,
`D3DPERF_SetOptions`. See `recon/enslaved_exe_imports_d3d9.txt`.

## Verdict

One of the friendliest VR-conversion target classes assessed: unpacked 32-bit
D3D9 UE3, prior art exists (Vireio/Helix/vorpX lineage), multiple viable proxy
and camera-ownership altitudes. Chosen foothold: a `d3d9.dll` proxy.
