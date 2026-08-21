# Engine Dossier — Enslaved: Odyssey to the West (Premium Edition)

> Distilled, current-truth reference for this game's engine. Updated whenever a
> finding graduates from session notes to established fact. The chronological
> record lives in `enslaved-vr-dev-archive` and `enslaved-vr-modding-notes`.

**Status line (2026-08-21):** Initial static recon complete. Engine identified,
renderer confirmed, foothold route chosen. Verdict so far: **one of the
friendliest VR-conversion targets we have assessed** — unpacked 32-bit D3D9
Unreal Engine 3 with debug assert strings intact and the developer console
still bound. Next step: live capture to confirm how the view-projection matrix
reaches the GPU.

---

## 1. Identity

| Fact | Value |
|---|---|
| Game | Enslaved: Odyssey to the West — Premium Edition (PC, 2013 port of the 2010 game) |
| Developer / publisher | Ninja Theory / BANDAI NAMCO |
| Engine | Unreal Engine 3 (circa 2009–2010 branch) with Ninja Theory's custom **NTEngine** layer |
| Internal codename | "Congo" — assert strings reference `e:\Projects\Congo\EnslavedMaster\MasterArchives\UnrealEngine3\Development\Src\...` |
| UE3 project name | `MonkeyGame` (all config/content folders use the `Monkey` prefix) |
| Architecture | 32-bit (`Binaries\Win32\Enslaved.exe`, ~34 MB) |
| DRM / packer | **None beyond plain Steamworks.** Clean PE: `.text .rdata .data .rsrc .reloc` — no SteamStub `.bind`, no packer. `.reloc` present, so the image is relocatable. |
| Symbols | No PDB, but the exe is full of assert/format strings with full source paths — near-symbol-quality orientation for static RE. |

## 2. Renderer

- **Direct3D 9 is the active RHI.** `AllowD3D10=False` in both
  `Engine\Config\BaseEngine.ini` and `MonkeyGame\Config\MonkeyEngine.ini`.
- D3D10 and D3D11 RHI code paths are compiled into the exe (strings reference
  `D3D10CreateDevice`, `ID3D11ShaderReflection`, DXGI swap chains) but the
  config gate keeps the game on D3D9. Flipping `AllowD3D10=True` is untested
  and not on the critical path — the D3D9 path is the well-trodden one.
- Referenced system DLLs: `d3d9.dll`, `d3d10.dll`, `dxgi.dll`, `dinput8.dll`,
  `xinput1_3.dll`, `winmm.dll`. Several viable proxy targets.
- Default display config: `Fullscreen=True`, 1280x720
  (`MonkeyGame\Config\MonkeyEngine.ini`).

## 3. Middleware inventory (from `Binaries\Win32`)

| Component | Evidence | VR relevance |
|---|---|---|
| PhysX (2.x era) | `PhysXCore.dll`, `NxCharacter.dll`, `NxCooking.dll`, `physxcudart_20.dll` | None directly |
| NaturalMotion Morpheme | `morpheme*` binaries | Animation; none directly |
| Bink Video | `binkw32.dll`, `binkudk.dll` | Full-screen movies need a VR fallback later |
| FaceFX | `FxGraphLayout.dll` | None |
| Fonix TTS | `FonixTtsDtSimple*.dll` | None |
| Steamworks | `steam_api.dll`, `steam_appid.txt` | Overlay also hooks D3D9 Present — load-order awareness |
| EasyHook | `EasyHook32.dll` **ships with the game** | The game itself uses an injection framework; hooking is demonstrably tolerated by its runtime |

## 4. Camera / projection delivery (hypothesis — to verify by capture)

Standard UE3-on-D3D9 mechanism, until proven otherwise:

- UE3 D3D9 RHI delivers transforms to shaders via
  `IDirect3DDevice9::SetVertexShaderConstantF`. The `ViewProjectionMatrix` is a
  uniform in the low constant registers of nearly every vertex shader
  (classically `c0–c3` for UE3's `LocalToWorld`/`ViewProjection` pairing —
  register assignment must be confirmed from a capture, not assumed).
- Game-side, the camera is a UE3 `Camera`/`PlayerCamera` chain; Ninja Theory
  layers a chase-camera system on top (`MonkeyChaseCamera.ini`, third-person).
- The viewport client is custom: `GameViewportClientClassName=NTEngine.NTReplayGameViewportClient`.
- FOV is data-driven in the camera INIs; the chase camera has speed-based FOV
  code (disabled by default: `m_useSpeedFoV=false`).

**Two candidate altitudes for owning the camera:**
1. **RHI level (D3D9 proxy):** intercept `SetVertexShaderConstantF` /
   `SetTransform` and re-derive or replace view/projection per eye. Proven
   approach on UE3 D3D9 titles (Vireio/Helix lineage).
2. **Engine level:** UE3's script/native camera path
   (`APlayerCamera::UpdateCamera` or the NTEngine equivalent) — patch the view
   before the renderer consumes it. Cleaner single point, needs RE of the
   NTEngine camera override chain.

## 5. Constant/uniform mechanism

D3D9: no constant buffers; everything goes through
`SetVertexShaderConstantF`/`SetPixelShaderConstantF` register uploads. Shader
reflection strings in the exe (`D3D9SafeGetConstantDesc`, constant-table walks)
confirm the engine tracks constants by name at runtime — a capture of constant
uploads plus shader disassembly will map register slots to engine uniforms.

## 6. Pass inventory

Not yet captured. Expected UE3 D3D9 frame: depth pre-pass, base pass
(directional lightmaps per config), dynamic shadows, post chain (bloom, DoF,
motion blur, ambient occlusion — all enabled in `[SystemSettings]`), UI.
To fill in from a frame capture.

## 7. Console / cvar cheat sheet

- `ConsoleKey=Tilde`, `TypeKey=Tab` are **already bound** in
  `MonkeyGame\Config\MonkeyInput.ini` and `Engine\Config\BaseInput.ini`.
  Whether the shipping build strips the console class is untested — first
  session in-game should just press Tilde.
- Usual UE3 suspects to try once a console/exec channel exists: `FOV <deg>`,
  `Show <group>`, `ToggleDebugCamera`, `Stat FPS`, `Stat D3D9RHI`,
  `ViewMode <mode>`, `SloMo`.
- All engine INIs are plain text and unsigned; `MonkeyEngine.ini` /
  `MonkeyInput.ini` accept edits directly (Premium Edition also honours
  per-user copies under `Documents` — confirm exact path on the dev machine).

## 8. Foothold plan (chosen route)

1. **Proxy `d3d9.dll`** in `Binaries\Win32` (or `dinput8.dll`/`winmm.dll` if
   the Steam overlay fights us). Log device creation, Present, and
   `SetVertexShaderConstantF` traffic.
2. Confirm console access (Tilde) for a free in-game exec channel.
3. Frame capture with the proxy logging constants; identify the
   view-projection registers and which passes consume them.
4. Keystone proof: perturb the view matrix in-flight → world camera moves →
   go/no-go for stereo.

## 9. Open risks

- **Third-person game:** VR comfort/design questions (chase camera vs.
  first-person conversion) — deferred until the North Star renders.
- **D3D9 + modern VR runtimes:** the compositor submission path from a D3D9
  game needs a D3D9Ex/D3D11 texture-sharing bridge — known-solvable (prior art
  exists), but it is extra plumbing to plan for.
- **NTEngine divergence:** Ninja Theory's layer may have moved camera logic out
  of stock UE3 paths; the `NTReplayGameViewportClient` name suggests a replay
  system wrapping the viewport.
- **Full-screen Bink movies** bypass the 3D pipeline; needs a flat-screen
  fallback in VR.
- Shipping build may have the console class stripped despite the binding
  (common in UE3 releases); fallback is exec via injected native calls.

## 10. Dead ends

None yet.
