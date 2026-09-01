# Engine Dossier — Enslaved: Odyssey to the West (Premium Edition)

> Distilled, current-truth reference for this game's engine. Updated whenever a
> finding graduates from session notes to established fact. The chronological
> record lives in `enslaved-vr-dev-archive` and `enslaved-vr-modding-notes`.

**Status line (2026-08-21):** Foothold built. The logging `d3d9.dll` proxy is
written, validated off-game, and deployed to `Binaries\Win32`. Engine
identified, renderer confirmed. Verdict so far: **one of the friendliest
VR-conversion targets we have assessed** — unpacked 32-bit D3D9 Unreal Engine 3
with debug assert strings intact and the developer console still bound. Next
step: run the proxy in-game and read the per-frame VS-constant histogram to
confirm which register carries the view-projection matrix.

**Confirmed d3d9 imports (from the exe's import table):** only
`Direct3DCreate9`, `D3DPERF_BeginEvent`, `D3DPERF_EndEvent`,
`D3DPERF_SetOptions`. The proxy exports these plus the rest of the standard
d3d9 surface, all undecorated.

**Instrument in place:** fail-safe `d3d9.dll` proxy (source in staging
`proxy-d3d9/`) hooks `IDirect3D9::CreateDevice` (vtable 16), then device
`Present` (17), `Reset` (16), and `SetVertexShaderConstantF` (94). Logs
CreateDevice params, a per-frame register-upload histogram, and an optional 4×4
watch-register dump. Off-game smoke test passed (HAL device, 3 frames, no
crash).

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

## 4. Camera / projection delivery — SETTLED STATICALLY (2026-09-01)

> ### There IS a shared view-projection, and it is at `c0`. The per-object-WVP reading was wrong.
>
> `[inferred-static 2026-09-01, n=1 — from the game's own shipped `Engine/Shaders/*.usf`]`
>
> **Enslaved ships its UE3 HLSL sources**, and `Common.usf` reserves the engine registers
> explicitly, noting they must match `EVertexShaderRegister` in `RHI.h`:
>
> | Register | Contents |
> |---|---|
> | **`c0`–`c3`** | **`ViewProjectionMatrix`** — world space to projection space |
> | **`c4`** | **`CameraPosition` / `ViewOrigin`** — world-space camera position |
> | **`c5`** | **`PreViewTranslation`** — offset applied to `LocalToWorld` for far-from-origin precision |
>
> `LocalToWorld` / `PreviousLocalToWorld` are ordinary `float4x4`s declared in the **vertex
> factories** (`LocalVertexFactory.usf`, `GpuSkinVertexFactory.usf`, which also has a
> `float4x3 WorldToLocal` and `float4x3 BoneMatrices[]`) — i.e. **compiler-allocated**.
>
> **CONFIRMED 2026-09-01 (upgraded from `[hypothesis]` the same day) by reading the register
> assignments out of the cooked shader cache**, exactly as the hypothesis said would be needed.
> `RefShaderCache-PC-D3D-SM3.upk` carries **34,046 D3D9 constant tables (`CTAB`)** with names and
> register indices intact; `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py` reads them.
> `[inferred-static 2026-09-01, n=34046 tables]`
>
> | Constant | **Vertex** shaders | **Pixel** shaders |
> |---|---|---|
> | `ViewProjectionMatrix` | **vs c0 x4 (3325 — every one)** | ps c3 x4 (288), ps c10 x4 (22) |
> | `CameraPosition` | vs c4 (2824) | — |
> | `PreViewTranslation` | vs c5 (1089) | — |
> | `LocalToWorld` | vs c6 x4 (2308), **vs c231 x4 (469)**, vs c10 x4 (264) | — |
> | `LocalToView` | vs c14 x4 (132), vs c10 x4 (103) | — |
> | `ScreenPositionScaleBias` / `MinZ_MaxZRatio` | — | ps c1 (11644) / ps c2 (12849) |
>
> **Stage column added 2026-09-02** `[inferred-static 2026-09-02, n=34046 tables; SM2 cache agrees]`
> — the 2026-09-01 reading omitted it, and that mattered (next paragraph). **Write the stage next to
> every register in this project**: `c3` is a view-projection in a pixel shader here and a stereo
> parameter in Alice's pixel shaders, and a stage-blind rule cannot tell them apart.
>
> **The 2026-08-21 histogram's unexplained 4x4s at `c6`, `c10` and `c231` are all now named**, and
> `c0`/`c4`/`c5` match the reserved registers `Common.usf` declares.
>
> **⚠️ CORRECTED 2026-09-02: the "9% read it from `c3`/`c10`" paragraph that stood here was
> mis-staged.** Those 310 tables are **pixel** shaders. On the vertex side — the only side a
> `SetVertexShaderConstantF` hook sees — **the view-projection is at `c0` and nowhere else**, so a
> per-eye offset at vs `c0` covers every vertex position. The proxy's `c3`/`c10` acceptance (guarded
> by bit-identity with that frame's `c0`) is therefore unreachable for its intended matrix; kept as a
> harmless fallback, comment corrected. `[inferred-static 2026-09-02]`
>
> **What that leaves open instead:** 310 pixel shaders read the view-projection at **ps `c3` / ps
> `c10`**, and the proxy does not hook `SetPixelShaderConstantF`. In a stereo build whatever they
> project (screen-space effects, reflections, decals — which is unknown from the table) uses the
> un-offset matrix while geometry is per-eye correct. Visible or not is a live question; the fix, if
> needed, is the same hook + same guard on the pixel stage. `[hypothesis]`
>
> **NVIDIA's 3D Vision UE3 branch is NOT in this build** `[inferred-static 2026-09-02, n=8 files]` —
> `nvstereo` occurs zero times in all three `RefShaderCache` caches (SM4 included, via raw byte
> search), all three `GlobalShaderCache` bins, the exe and the shipped `.usf`; `AllowNvidiaStereo3d`
> is in no file. The only `NVCHANGE` markers are a particle-colour edit. Unlike Alice, there is no
> shipped stereo path to drive. Note `modding-notes/2026-09-02-viewprojection-c3-c10-are-pixel-shaders-no-nvidia-stereo-branch.md`.
>
> **Why the capture below reads as if it disproved this:** it measured how often a register was
> **written**, not what was written to it. UE3's D3D9 RHI re-applies the reserved view registers
> around bound-shader-state changes, so `c0`'s 47 uploads/frame are 47 writes of the *same* value.
> Upload frequency was never evidence about shared-ness. **The capture actually corroborates the
> mapping**: it records "scalar params occupy c4/c5", which are exactly `CameraPosition` and
> `PreViewTranslation`.
>
> **What this unlocks:** `SetVertexShaderConstantF(StartRegister == 0, Vector4fCount == 4)` is a
> clean single injection point for a per-eye offset, and **`c4` hands us the camera world position
> directly** — no solving it out of the matrix.
>
> **`PreViewTranslation` (`c5`) — narrowed 2026-09-01.** UE3 pre-translates the world so the camera
> sits near the origin for float precision; vertices arrive in *translated* world space and `c0` is
> built to match. **This does NOT complicate a per-eye offset**: a relative offset is a translation
> and translations commute, so the same `t` is correct in translated world space. The trap is real
> but narrower than first written — it applies to anything reasoning about **absolute** world
> positions (comparing `c4` against the matrix, for instance), not to the offset itself.
>
> **Matrix layout, also from the shipped source:** on PC `Common.usf` defines
> `MulMatrix(Mtx,Vect)` as `mul(Mtx,Vect)` (column vectors) and the shaders do
> `MulMatrix(ViewProjectionMatrix, WorldPosition)`. So the 16 uploaded floats are the matrix's
> **rows** and the translation is **column 3**, making `M' = M * T(t)` a column-3-only edit that
> needs no P/V split.
>
> **Implemented 2026-09-01** in `staging/enslaved-vr/proxy-d3d9/` behind `[stereo] Enabled` in
> `d3d9_proxy.ini` (default off). `[compile-verified]`, `[untested]`. **Also built on the home PC and
> deployed there 2026-09-02** (llvm-mingw i686, 9 exports; the home install had no proxy before, so
> deleting `d3d9.dll` + `d3d9_proxy.ini` from `Binaries\Win32` restores stock). See
> `modding-notes/2026-09-01b-...` — which also records that the committed **build recipe was broken**
> in two ways and could not produce a loadable proxy.
>
> Full write-up: `modding-notes/2026-09-01-shared-viewprojection-confirmed-at-c0.md`.
> Still to confirm live (cheap): that the SHARED-matrix detector flags `c0` and nothing else.

The original hypothesis, kept for the record:

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

**First in-game capture (2026-08-21).** Device: 1920x1080, D3DFMT_A8R8G8B8,
fullscreen, PresentInterval IMMEDIATE. VS-constant histogram (gameplay frame
~600) shows per-object 4x4 matrices at `c0` (47 draws/frame), `c6` (189),
`c10` (19), and `c231` (124, paired with a 4x3 `c235` LocalToWorld — a separate,
likely skinned, vertex factory). Scalar params occupy c4/c5, c11-c21,
c236-c248. **No 4x4 register was uploaded once-per-frame**, so the camera is
likely folded into a per-draw World x ViewProjection rather than a shared
view-projection register. The proxy now auto-flags any register whose 4x4 is
constant across all draws in a frame (SHARED = view-projection candidate); the
next capture will settle shared-VP vs per-object-WVP, which decides the
injection strategy.

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
- **D3D9 + modern VR runtimes — the bridge is understood, and the game is on the
  awkward side of it.** `/gr` pointed out (2026-09-01) that `far-cry-2-vr` already
  researched the D3D9→compositor path, so the technique is not ours to invent:
  create the texture on the **D3D11** side with `D3D11_RESOURCE_MISC_SHARED`, take
  its `HANDLE` from `IDXGIResource::GetSharedHandle`, and open it from D3D9Ex via
  `IDirect3DDevice9Ex::CreateTexture(..., pSharedHandle)` — a documented Windows
  interop path with no CPU round-trip. `[reported]`

  **But it requires a D3D9Ex device, and Enslaved does not create one.**
  `[inferred-static 2026-09-01, n=3 independent checks]` — three checks that fail
  in different ways, so agreement is meaningful:
  1. the import table names **`Direct3DCreate9` only** (with three `D3DPERF_*`
     markers) and no `…Ex` in the normal *or* delay-import directory — this
     matches `dev-archive/recon/enslaved_exe_imports_d3d9.txt`, dumped by an
     earlier session with a different tool;
  2. the string `Direct3DCreate9Ex` does not occur anywhere in the 34 MB
     executable, which rules out a runtime `GetProcAddress`;
  3. the `IDirect3D9Ex`, `IDirect3DDevice9Ex` and `IDirect3DSwapChain9Ex` IIDs
     occur **zero** times, which rules out a `QueryInterface` upgrade on a
     device created the legacy way.

  **The route that remains, and it is cheap:** our proxy already owns `d3d9.dll`
  and its `.def` already exports `Direct3DCreate9Ex`. Because `IDirect3D9Ex`
  derives from `IDirect3D9` (and `IDirect3DDevice9Ex` from `IDirect3DDevice9`),
  the proxy can call `Direct3DCreate9Ex` itself and hand the game the Ex object
  through the legacy interface; the game is compiled against the base vtable and
  need not know. `[reported]` — interface inheritance, not yet built or run here.

  **🪤 Two traps, both of which decide the design rather than tune it:**
  - **`D3DPOOL_MANAGED` does not exist on a D3D9Ex device.** Any
    `CreateTexture`/`CreateVertexBuffer`/`CreateIndexBuffer` asking for it fails.
    So the upgrade above is only viable if UE3's D3D9 RHI never asks for MANAGED
    on this build — **unverified, and it is the first thing to establish**, because
    it is the difference between a one-line proxy change and a resource-remapping
    project. `[reported]`
  - **`D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` has no D3D9 equivalent** — there is
    no `IDirect3D9KeyedMutex`, so the synchronisation primitive every tutorial
    recommends is unavailable to a D3D9Ex producer. The established substitute is
    an `IDirect3DQuery9` event query plus double/triple buffering. `[reported]`

  One more for whatever submits: **OpenVR issue #1253** (open) — SteamVR keeps only
  the pose from the *last* `Submit`, so per-eye `Submit_TextureWithPose` ghosts.
  Submit both eyes together rather than racing per-eye pose timing. `[reported]`
- **NTEngine divergence:** Ninja Theory's layer may have moved camera logic out
  of stock UE3 paths; the `NTReplayGameViewportClient` name suggests a replay
  system wrapping the viewport.
- **Full-screen Bink movies** bypass the 3D pipeline; needs a flat-screen
  fallback in VR.
- Shipping build may have the console class stripped despite the binding
  (common in UE3 releases); fallback is exec via injected native calls.
- **Pixel-side view-projection is not offset** (§4, 2026-09-02): 310 pixel shaders read
  `ViewProjectionMatrix` at ps `c3`/`c10`; the proxy hooks only the vertex stage. Unknown whether
  visible; watch reflections/decals during the first rock test. `[hypothesis]`

## 10. Dead ends

- **NVIDIA 3D Vision UE3 branch as a shipped stereo path — absent from this build.**
  `[inferred-static 2026-09-02]` No `NvStereoEnabled`/`NvStereoFixTexture` in any shader cache or
  source, no `AllowNvidiaStereo3d` in any INI (§4). Sibling Alice has it; Enslaved does not.
- Related, for anyone testing 3D-Vision-style tricks on a UE3 title here: UE3's 3D Vision
  integration is **fullscreen-only and does not run in the editor** `[reported 2026-09-01, via /gr
  from Epic's UDK page]` — a windowed negative is not a negative.
