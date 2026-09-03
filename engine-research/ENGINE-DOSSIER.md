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
- **❌ ANSWERED 2026-09-03: the console does NOT open by keypress in this build.**
  `[verified-live 2026-09-03, n=3 keys]` Tilde (`0x29`), Tab (`0x0F`) and F10 (`0x44`) were each
  sent as scancodes to the focused window with a screen capture taken after; the scene was unchanged
  every time. **This confirms the "shipping build may have the console class stripped" risk below**
  and closes the "first session in-game should just press Tilde" item — it was pressed.
  ⚠️ `n=3` keys on one build rules out the *cheap* route, not every route.
- **❌ ANSWERED 2026-09-03b: the key-binding exec channel is DEAD TOO.** `[verified-live 2026-09-03,
  n=3 commands]` Tested three ways: **F9=`shot`** — a **developer** binding shipped in
  `MonkeyInput.ini`, not one we added — wrote no file anywhere; **F6=`FOV 120`** changed no framing;
  **F5=`ToggleDebugCamera`** did nothing and `W` still walked the character. The added bindings were
  verified still present in the live ini after launch (mtime unchanged), and F9 does not depend on
  our edit, **so the test could have produced a positive.**
- **⇒ THE COHERENT READING: this build kept its input/action bindings and STRIPPED ITS EXEC
  DISPATCH.** Movement, menus, ESC/ENTER/arrows all drive the game; console-style exec commands
  (`FOV`, `shot`, `ToggleDebugCamera`) dispatch nowhere. That is what a shipping UE3 build looks like
  with the console/cheat-manager path compiled out. It also retires the shipped
  `[NTGameFramework.NTCam_DebugInput]` debug-camera map as an input-reachable feature.
  > **⚠️ Transferable lesson: a binding surviving in a shipped config is NOT evidence the feature is
  > live.** This game ships console bindings with no console *and* a full debug-camera map with no
  > reachable debug camera. Config is a lead; running it is the evidence. Six keys across two
  > sessions is enough — stop trying keys.
- **❌ THE CONTROLLER-CHORD ROUTE IS ALSO DEAD (2026-09-03c).** `[verified-live 2026-09-03]` LS+RS
  held 1.2 s through a ViGEmBus virtual X360 pad produced no debug camera; `W` still walked the
  character. **The control passed** — the same pad then moved the character with the left stick
  (frame delta 48.9) and swung the camera with the right (62.5) against an idle baseline of ~2 — so
  the game reads the pad and the chord genuinely does nothing.
  **⇒ The debug camera is unreachable by ANY input route, pad or key**, for one reason:
  `ToggleDebugCamera` is an exec command, exec dispatch is stripped, and the chord's job is to
  *call* it. The input side works perfectly; nothing is left at the other end.
- **⭐ A virtual XInput pad DOES drive this game** `[verified-live 2026-09-03]` — movement on the
  left stick, camera on the right, hot-plugged into a running game with no restart. A third input
  route worth keeping for anything gated behind a controller.
  (`flat-to-vr-RE-toolkit/tools/virtual-pad.py`)
- **What remains for a command channel, best first:**
  1. **⭐ In-process exec from our own proxy.** We already own `d3d9.dll` and run inside the process
     every frame; locating the engine's exec entry point by pattern and calling it directly bypasses
     input, bindings and the console entirely. **`[PD]` work** — static, no game needed.
  2. **A virtual gamepad.** The debug camera's normal-play entry point is a controller thumbstick
     chord (`CheckDebugCamChord`/`DoDebugCamChord` in `[Engine.PlayerInput]`), so an emulated pad
     could send it. The estate already carries a `[USER]` ViGEmBus install item under
     `doom-2016-vr` — the two projects now share that dependency.
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
  - **`D3DPOOL_MANAGED` does not exist on a D3D9Ex device** — any
    `CreateTexture`/`CreateVertexBuffer`/`CreateIndexBuffer` asking for it fails.
    **✅ But this is SOLVED GENERICALLY, and is not a gate** (2026-09-03, via `/gr` — supersedes
    this bullet's former "one-line proxy change vs. resource-remapping project" framing, and the
    instruction to decide the route only after the instrumented launch):
    **rewrite `MANAGED → DEFAULT + D3DUSAGE_DYNAMIC` in the proxy's existing `Create*` wrappers.**
    `[reported 2026-09-03]`
    - MANAGED exists to survive device loss, and **a 9Ex device never loses** (`D3DERR_DEVICELOST`
      is never returned), so the pool has nothing left to do on Ex — rewriting it away is the
      migration the design implies, not a violation of it.
    - **The `D3DUSAGE_DYNAMIC` half is the load-bearing part:** DEFAULT textures cannot be locked
      unless they are dynamic, whereas MANAGED ones can, so plain DEFAULT would break any
      `Lock()`. DEFAULT × DYNAMIC is legal where MANAGED × DYNAMIC is not, so the rewrite can never
      collide with a usage flag the engine already set.
    - **Public prior art, twice:** `elishacloud/dxwrapper`'s `D3d9to9Ex` does exactly this upgrade
      and overrides MANAGED → DEFAULT + DYNAMIC following Special K's strategy; its maintainer
      reports **7 of 8 tested games working**.
    - **⇒ Whether UE3 asks for MANAGED SIZES the change; it does not gate it.** The instrumented
      launch is now a risk-sizing measurement (how much `Lock()` traffic gets re-pointed), worth
      riding along on a launch that is happening anyway — not a prerequisite.
  - **The real 9Ex risk list** (same source, `[reported 2026-09-03]`) — these, not MANAGED, are what
    decide whether this build cooperates, and **all four are cheap to observe on the first Ex
    launch**: no paletted textures on 9Ex; 16-bit textures only work in `SYSTEMMEM`; **D3DX
    functions remain problematic** — directly relevant, this is a 2010-era UE3 build with a D3DX
    dependency chain; and some titles simply fail at device creation.
  - **`D3D11_RESOURCE_MISC_SHARED_KEYEDMUTEX` has no D3D9 equivalent** — there is
    no `IDirect3D9KeyedMutex`, so the synchronisation primitive every tutorial
    recommends is unavailable to a D3D9Ex producer. The established substitute is
    an `IDirect3DQuery9` event query plus double/triple buffering. `[reported]`

  One more for whatever submits: **OpenVR issue #1253** (open) — SteamVR keeps only
  the pose from the *last* `Submit`, so per-eye `Submit_TextureWithPose` ghosts.
  Submit both eyes together rather than racing per-eye pose timing. `[reported]`

  **The D3D10 path sidesteps this whole trap, at a different cost.** `[reported 2026-09-02, via
  /gr]` `-d3d10` is a public launch argument for this game (same switch as `AllowD3D10`; PCGamingWiki
  summary — the page itself 403s). On that RHI a shared texture is an ordinary DXGI resource
  (`D3D10_RESOURCE_MISC_SHARED`), keyed mutexes exist, and no Ex upgrade is needed at all — no public
  source says whether `D3DPOOL_MANAGED` is used either way, so the instrumented launch stays the only
  answer to that question regardless of route. The cost: the camera injection would have to become a
  constant-buffer patch (SM4 shader cache on disk as the reflection source) instead of the proven
  `SetVertexShaderConstantF(0,…,4)` hook — undesigned. **⇒ TRY (a) FIRST; (b) IS THE FALLBACK** (revised 2026-09-03,
  via `/gr`): route (a) D3D9+Ex keeps **the proven `SetVertexShaderConstantF(0,…,4)` hook that has
  already produced a stereo picture**, whereas (b) `-d3d10` discards it for an undesigned cbuffer
  injection point. (b)'s main appeal was that (a) looked blocked on the MANAGED unknown — **it is
  not**, per the bullet above. Fall back to (b) only if one of the four named 9Ex limits bites.
  Check `-d3d10` on a separate launch so the stereo run stays clean.
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
  - **✅ NO SHADOW SWIM DETECTED, 2026-09-03b** `[measured 2026-09-03, n=2 scenes]`. Ground-band
    tiles split by brightness (dark = shadow, bright = lit) and phase-correlated separately: shadow
    tiles measured **−9 to −13 px, tracking the same depth gradient as the rest of the world**, not
    sitting near zero. Shadows move WITH the world here.
    - **✅ UPGRADED to a MATCHED-DEPTH test, same day** `[measured 2026-09-03, n=2 depth bands x 3
      eye-pairs]`: a close cast shadow and lit grass **on the same screen rows** measured
      −14/−13/+13 vs −14/−14/+14, and a mid-distance pair measured −8/−8/+8 vs −8/−8/+8.
      **Identical within 1 px, signs flipping together — shadows are offset correctly and do not
      swim.** Closes the highest-prior watch item.
    ⚠️ Three daylight exteriors only.
    It says nothing about **screen-space** effects — reflections, water surfaces, decals — which are
    the likelier home of the pixel-stage problem. The "get close to water / a wet floor / a decal"
    item is **not** answered.

## 10a. A public 3D Vision fix for this exact binary exists — corroboration and practical setup (2026-09-02, via `/gr`)

`[reported 2026-09-02]` unless noted; study material only (what the fix had to address), nothing
copied, and its DLL must never be installed beside our proxy. **Supersedes the 2026-08-24
external-research claim that no Helix Mod / 3DMigoto entry exists for Enslaved — that was wrong**:
eqzitara shipped one for the Premium Edition, 2013-10-28 (updated 2013-12-21).

- **Independent corroboration of the separation scale.** UE3 is conventionally 1 UU ≈ 1–2 cm (Epic's
  own guidance: don't vary beyond ×2), so this project's own `Separation=6.0` sits at 6–12 cm —
  already at or above a real IPD (~6.4 cm). That matches the run-6/7 finding (§ status file: "2
  monkeys with a little gap" at 60 ⇒ ~6.5 the fitted value) from a completely different method — the
  small-hop symptom at 6.0 was a correct-magnitude value read on a flat screen, not a wrong one.
- **⭐ Motion blur must be OFF for any stereo judgement** (`MotionBlur=False` in `MonkeyEngine.ini`, or
  the in-game option). Motion blur reprojects using the view-projection at the **pixel stage** — the
  copy this project's vertex hook does not touch (§4, §9's 310-pixel-shader risk) — so a stereo run
  judged with motion blur on is judging an uncorrected pass, not the fix.
- **What the public fix had to correct, independently arriving at the same 310-shader shape this
  project predicted from the CTAB reflection:** shadows, crosshairs, "visual effects", menu screens.
  **HUD depth stayed broken even in that fix** — consistent with this project's ortho-`c0` finding
  (§ modding-notes 2026-09-02, now handled: the proxy skips offsetting orthographic `c0` uploads).
  Shadows are the highest-prior thing to watch on the next stereo run, ahead of a generic "watch for
  anything odd".
- **Two convergence regimes**: F3 cinematic, F4 gameplay, auto-switches after the tutorial — the
  cutscene and chase cameras sit at different depth scales and likely need tuning separately.
- **`useAutoTiltup` can be disabled** in the chase-camera ini — an automatic camera tilt is a VR
  comfort hazard and the game ships the off-switch (same class as Alan Wake's `-rigidcamera`).
- **Exec commands confirmed reaching this build via key bindings** —
  `Bindings=(Name="F1",Command="FOV 0")` under `[MonkeyGame.MKInput]` in `MonkeyInput.ini` is reported
  working, so §7's "console class may be stripped" risk has a working fallback channel regardless of
  whether Tilde itself is live.

## 10. Dead ends

- **The barrel/fisheye warp with heavy vignetting on loading and transition screens is THE GAME'S
  OWN EFFECT** — user-confirmed 2026-09-03. It is authored, not an artefact of the d3d9 proxy, the
  stereo offset, or the forced windowed mode. **Do not chase it as a projection bug.** It is also a
  useful state marker: a lens-warped frame means loading/transitioning, not gameplay.

- **NVIDIA 3D Vision UE3 branch as a shipped stereo path — absent from this build.**
  `[inferred-static 2026-09-02]` No `NvStereoEnabled`/`NvStereoFixTexture` in any shader cache or
  source, no `AllowNvidiaStereo3d` in any INI (§4). Sibling Alice has it; Enslaved does not.
- Related, for anyone testing 3D-Vision-style tricks on a UE3 title here: UE3's 3D Vision
  integration is **fullscreen-only and does not run in the editor** `[reported 2026-09-01, via /gr
  from Epic's UDK page]` — a windowed negative is not a negative.
