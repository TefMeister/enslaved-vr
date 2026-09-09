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
- **⇒ THE 2026-09-03 READING — "this build kept its input/action bindings and STRIPPED ITS EXEC
  DISPATCH" — IS DOWNGRADED TO `[hypothesis]` (2026-09-04, via `/gr`, folded by `/pd`).** It wore the
  `[verified-live 2026-09-03, n=3 commands]` tag above, but none of the three negatives is a valid
  negative, each for a cheaper reason `[inferred-static 2026-09-04, public UE3 source + the shipped
  ini]`:
  - **F9=`shot` is bound only inside `[NTGameFramework.NTCam_DebugInput]`** (live ini lines 129–183,
    F9 at line 158, re-read on the dev PC 2026-09-04) — the debug camera controller's *own* input
    class, which does not exist in normal play. "F9 does not depend on our edit" was true and
    irrelevant: **that test could never have produced a positive.**
  - **F5=`ToggleDebugCamera` is a `GameFramework.GameCheatManager` exec.** A CheatManager exists only
    if `PlayerController.AddCheats()` ran, gated on `GameInfo.AllowCheats()`; the `EnableCheats` exec
    that forces it is FINAL_RELEASE-guarded. The bound-command chain (`UnPlayer.cpp:2923–2954`) tries
    PlayerInput → PlayerController → Pawn → InvManager → Weapon → HUD → GameInfo → CheatManager-if-
    non-null and **returns false silently when no object owns the name — with dispatch fully alive.**
    The pad chord (below) ends at the same missing object.
  - **F6=`FOV 120` → `PlayerController.FOV` → `PlayerCamera.SetFOV`**, a one-shot the game's chase
    camera (`MonkeyChaseCamera.ini`) can overwrite each tick. The community FOV recipe for this game
    is that binding under `[MonkeyGame.MKInput]` (§10a), reported working. `[hypothesis]`
  - **Section placement is an open variable:** our test lines went into `[Engine.PlayerInput]`; the
    community uses `[MonkeyGame.MKInput]`, present in the game-folder ini (line 389) but absent from
    the Documents copy the game loads.
  - **The one-key re-test that settles it (`[FLAT]`):** bind `Pause` — an unguarded
    `PlayerController` exec, no CheatManager needed, world visibly freezes — in **both** sections of
    the Documents `MonkeyInput.ini`, plus the community `FOV` line verbatim. Pauses ⇒ dispatch is
    alive, this reading is `[disproved]`, and the in-process rows become "construct a CheatManager".
    Does not pause in either section ⇒ the first *valid* negative for stripped dispatch.
  - What stands: movement, menus, ESC/ENTER/arrows all drive the game; the shipped
    `[NTGameFramework.NTCam_DebugInput]` map is not input-reachable **in normal play** because its
    owning controller does not exist there — not because dispatch is gone.
  > **⚠️ Transferable lesson: a binding surviving in a shipped config is NOT evidence the feature is
  > live.** This game ships console bindings with no console *and* a full debug-camera map with no
  > reachable debug camera. Config is a lead; running it is the evidence. Six keys across two
  > sessions is enough — **one more is budgeted, and only one: the `Pause` re-test above**, because
  > it is the first key whose negative would actually mean something.
- **❌ THE CONTROLLER-CHORD ROUTE IS ALSO DEAD (2026-09-03c).** `[verified-live 2026-09-03]` LS+RS
  held 1.2 s through a ViGEmBus virtual X360 pad produced no debug camera; `W` still walked the
  character. **The control passed** — the same pad then moved the character with the left stick
  (frame delta 48.9) and swung the camera with the right (62.5) against an idle baseline of ~2 — so
  the game reads the pad and the chord genuinely does nothing.
  **⇒ The debug camera is unreachable by the routes tried — key and pad — none of which is yet a
  valid negative** (corrected 2026-09-04, see above). The input side works perfectly; the chord's
  job is to call `ToggleDebugCamera`, which lives on a CheatManager that normal play never builds.
  **That the debug systems SHIP in this PC build is now `[reported 2026-09-04]`:** dron_3 (2020-11-02)
  opened this game's **PC debug menu** with a `dinput8.dll` patch (Backspace+Escape during play), and
  on PS3 (v1.01) a single `li r3,0` enables *both* the debug menu and the debug camera — one function
  forced to return zero, the shape of a defeated "debug allowed" predicate. The earlier "no camera
  hack exists for this game" (2026-08-24) is `[disproved 2026-09-04]` for the menu. Nothing was
  downloaded or examined; only that it works.
- **⭐ A virtual XInput pad DOES drive this game** `[verified-live 2026-09-03]` — movement on the
  left stick, camera on the right, hot-plugged into a running game with no restart. A third input
  route worth keeping for anything gated behind a controller.
  (`flat-to-vr-RE-toolkit/tools/virtual-pad.py`)
- **What remains for a command channel, best first (re-shaped 2026-09-04):**
  0. **The `Pause` re-test** (`[FLAT]`, one key, above) — decides whether exec dispatch is alive.
  1. **⭐ In-process, route (B): call script functions directly through `UObject::ProcessEvent`.**
     Not "locate the exec entry point by pattern" — the dispatcher is a chain of eight
     `ScriptConsoleExec` calls, not a function. The public, MIT-licensed UE3 SDK-generator recipe
     (ItsBranK's UE3SDKGenerator, the CodeRed Generator; both document 32-bit UE3): pattern-find
     `GObjects`/`GNames`, walk to the live `PlayerController` and the `UFunction`s by name, call via
     `ProcessEvent` (vtable index or pattern). Sequence: `ProcessEvent(PC, AddCheats, {bForce=true})`
     (a plain script function, not FINAL_RELEASE-guarded) → `ProcessEvent(PC.CheatManager,
     ToggleDebugCamera)`; and `ProcessEvent(PC, ConsoleCommand, "…")` restores the whole command
     vocabulary through the engine's own chain. `[inferred-static]` **Anchors are in the binary**
     `[measured 2026-09-04]`: `Enslaved.exe` contains `GObjObjects` (×7 ASCII), `ProcessEvent`,
     `CheatManager` and `ConsoleCommand`. It does **not** contain `ToggleDebugCamera`/`AddCheats`/
     `AllowCheats` — expected, not evidence: script names live in cooked packages whose name tables
     are compressed. The one unknown is whether `CheatClass` still names a real class in this build;
     if not, route (A). **This is the `[PD]` row.**
  2. **In-process, route (A): find and defeat the gate** — `GameInfo.AllowCheats` or Ninja Theory's
     override, which decides whether `AddCheats()` builds the `GameCheatManager` owning
     `ToggleDebugCamera`; or the game-specific check behind `CheckDebugCamChord`/`DoDebugCamChord`,
     whose exec-name strings are in the exe. dron_3's PS3 patch is exactly this shape.
  3. **A virtual gamepad** already drives this game (2026-09-03c) — the chord itself is proven to
     reach the engine, so once a CheatManager exists the pad route is live for free.
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

## 9a. ⚠️ A D3D9 device **Reset** disarms the stereo for the life of the process (2026-09-03d)

**The single most important operational fact about this proxy.** After any `Reset`, the hook stops
seeing vertex-shader constant uploads entirely — the per-frame histogram prints its header with no
rows and the stereo summary reads `offset 0, ortho-skipped 0` — and it never recovers.
`[verified-live 2026-09-03, n=2 resets]`

- **Both a deliberate and an incidental reset do it.** One came from changing resolution in the
  options menu; the other from an ordinary **checkpoint restart**. It is not avoidable by leaving
  settings alone.
- **Nothing else breaks.** `Present` keeps firing at a clean 60 fps, the `Reset` hook logs the
  event, and the forced-window logic correctly re-applies. Only `SetVertexShaderConstantF` stops
  being reached.
- ~~**⭐ It is not instantaneous.** One MORE healthy summary prints after the reset, and only the next
  one is dead — so the cause runs roughly **120–240 frames after `Reset` returns**, not inside it.~~
  **WITHDRAWN 2026-09-04:** the stereo summary counts "since last summary" over a `FrameInterval`
  window (`dllmain.cpp` lines 423–443), so one healthy post-reset summary is expected **even if the
  slot died inside `Reset` itself**. The figure was an artefact of the window, not a measurement
  `[inferred-static 2026-09-04]`. The 2026-09-04 build stamps the moment to the frame instead.
  ~~Prime suspect: UE3 re-creating its RHI/device objects onto a vtable the patch no longer covers.~~
  **Excluded 2026-09-04** (`/gr`): D3D9 vtables are shared per runtime class, a second
  `CreateDevice` would have been logged by our own hook, and slot 17 in the *same table* kept working
  — only slot 94 was rewritten.
- **Recovery is a relaunch.** A fresh process always reads healthy (`offset 2690`/`3360`/`4000`).

**⚠️ Operational rule for every session: read `offset` in the log before trusting any stereo
observation.** Nothing on screen indicates the mod has been disarmed. *(Since the 2026-09-04 build the
summary line also prints `slot94=ours|NOT OURS`, which is the direct check.)*

### 2026-09-04: the leading explanation, and a build that survives it either way

- **Leading `[hypothesis]`: a recorded STATE BLOCK rewrites the vtable.** Two independent public
  witnesses — gho (DxWnd, 2014): *"BeginStateBlock recover all COM method pointers invalidating the
  hook patching"*; Paul Roussin (D3D8 newsgroup): *"BeginStateblock will reset the device table so you
  have to … reset your modified addresses"* — describe the D3D9 runtime swapping the state-**setting**
  methods for recording variants between `BeginStateBlock` and `EndStateBlock` and restoring its own
  originals afterwards. Slot 94 is a state-setting method; `Present`/`Reset` are not. That is the
  observed pattern exactly. `[reported]` in general; `[hypothesis]` for this game until the log says
  so. UE3's own D3D9 RHI records no state blocks (public source, one search), so the caller would be
  another resident — Steam overlay, driver overlay, anything on `ID3DXSprite`/`ID3DXFont` —
  re-initialising after the reset. (Via `/gr` 2026-09-04; topic
  `external-research/topics/2026-09-04-a-recorded-state-block-rewrites-the-device-vtable-and-kills-an-in-place-patch.md`.)
- **The proxy now heals itself** `[compile-verified 2026-09-04]`, `-Wall -Wextra` clean, 9/9 exports,
  **deployed on the dev PC** (`d3d9.dll` 78,336 B; previous kept as `d3d9.dll.bak-2026-09-04-pre-rearm`),
  **not yet on the home PC** (pull `staging`, `build.ps1`). Every `Present` compares slots 94/16/17/60/61
  against our functions and re-patches a slot that has reverted to **the runtime's original pointer** —
  the only unambiguous case; a *foreign* pointer is logged once with its module and left alone, since it
  might be a later hook that chains to us. `BeginStateBlock`/`EndStateBlock` (60/61, verified from the
  SDK header) are hooked to log frame, caller module and whether slot 94 survived; `[reset] returned …
  slot94=` is logged the instant `Reset` returns; `[liveness]` stamps the first frames with zero uploads.
  `[hooks] Rearm=0` observes without healing. Full reading table: `modding-notes/2026-09-04-the-vtable-patch-heals-itself-and-exec-dispatch-stripped-is-downgraded.md` §4.
- **Not run.** Whether state blocks are the rewriter here, and whether a re-armed slot yields a
  *working* stereo, are the next launch's questions — one launch, one checkpoint restart.

### ⭐⭐ 2026-09-09: RESOLVED LIVE — the re-arm works, and it is NOT a state block

First live run of the 2026-09-04 self-healing build. **Two Resets** (stepping the resolution in
DISPLAY OPTIONS and back), both reading identically `[verified-live 2026-09-09, n=2 resets]`:

- `[reset] returned hr=0x00000000 … slot94=NOT ours slot17=ours slot16=ours (before any re-arm)` —
  the Reset rewrites **exactly one slot**, the state-setting method. Slots 16 and 17 in the same
  table are untouched, confirming the 2026-09-04 exclusion of "UE3 re-created the device".
- `[rearm] … had REVERTED to the runtime's original … 0 frames after the last Reset … -> re-patched`
  — the heal fires in the same frame the Reset returns.
- Every summary afterwards: `offset 2760 … re-arms 1, slot94=ours`. **The stereo survives a Reset.**
  The 9a headline above is fixed as of this build.
- **`state blocks 0` for the entire session, either side of both Resets.** No `BeginStateBlock` /
  `EndStateBlock` pair was ever recorded, so **the recorded-state-block explanation is not what
  happens in this game** `[verified-live 2026-09-09, n=2 resets]`. It remains a real mechanism in
  general (DxWnd, the D3D8 newsgroup) — it is simply not the one here. The revert is at `Reset`.

**⚠️ A checkpoint restart did NOT reset the device on the dev PC** `[verified-live 2026-09-09, n=1]`
— a full `RESTART FROM LAST CHECKPOINT` produced **zero** `[reset]` lines with `offset` healthy
either side. 2026-09-03d recorded a checkpoint restart as one of its two resets, on the **home PC**
(3440x1440 desktop, stored resolution ignored). The 9a claim is therefore narrowed: **a resolution
change resets the device; a checkpoint restart does so on the home PC and did not on the dev PC.**
Which of machine, resolution or forced-window mode decides it is not established.

### The game ignores its own saved resolution at startup `[verified-live 2026-09-03, n=2 launches]`

`MonkeyEngine.ini` holds `ResX=1280 ResY=720`; `CreateDevice` asks for **3440x1440** (the desktop
size) every launch, and the options menu displayed `1920x1080` while the device was 3440x1440. Only
the *Reset* ever applies the stored value — which means **a matched-resolution backbuffer and a live
stereo are currently mutually exclusive**. Not a blocker for per-region tests: a uniform downscale
shifts every tile equally.

## 9b. Stereo correctness — what has now been measured, and what has not

| surface | verdict | strength |
| --- | --- | --- |
| depth-parallax curve | monotonic with distance | `[measured 2026-09-03, n=2 scenes]` |
| HUD / ortho | exactly 0 offset, as designed | `[measured 2026-09-03]` |
| shadows at matched depth | track the depth gradient | `[measured 2026-09-03]` |
| wet floor + caustics (Ch2) | clean, no un-offset region | `[measured 2026-09-03, n=4 eye-pairs]` |
| **reflective water, glancing angle (Ch4 pool)** | **clean — largest parallax in frame** | `[measured 2026-09-03, n=16 eye-pairs, 1 scene]` |
| **decals** | **NOT TESTED** | — |

⚠️ **The magnitude on the water is softer than the verdict.** The blocks standing in that pool are a
strongly repetitive ridged pattern and phase correlation can lock onto the wrong period; `+18`/`+19`
px should be read as "much larger than the `+2.01` frame median", not as a calibrated number.

⚠️ **Two tiles read exactly 0 and both were HUD** — the ability radial and the item counters. That is
the ortho fix working, not a defect. **Check what is behind a probe region before believing it**; this
is the second time that rule has paid on this project.

## 9d. ⭐⭐ `GNames` IS LOCATED: `0x0242B954`, BY CODE PATTERN, FOUR WAYS (2026-09-08, `/pd`, no launch)

Write-up: `modding-notes/2026-09-08-gnames-located-by-code-pattern.md`. Tool:
`dev-archive/tools/find_gnames.py`. Evidence: `dev-archive/recon/2026-09-08-gnames-located/`.

> **`GNames.Data = 0x0242B954`, `.ArrayNum = 0x0242B958`, `.ArrayMax = 0x0242B95C`**
> `[inferred-static 2026-09-08]`

Four independent signals, none of which is "it has the right name":

1. **The published UT3 signature matches exactly**, from **four** call sites (`0x00594368`,
   `0x006777FE`, `0x00677A24`, `0x00679D0E`), **all resolving to the same address**:
   `8B 0D ?? ?? ?? ?? 83 3C 81 00 74` - the identical pattern used for UT3, APB: Reloaded,
   Tribes: Ascend and Hawken in `polivilas/UnrealEngineSDKGenerator` `[reported 2026-09-07]`.
2. **The adjacency prediction lands on the nose.** `/gr` gave two published pairs where `GNames` sits
   BELOW `GObjects` by under `0x50` (Borderlands 1 `0x30`, Rocket League `0x48`). Ours is
   `0x0242B984 - 0x0242B954` = **exactly `0x30`**.
3. **It is in `.data`**, the only writable section - as a mutable global must be.
4. **The usage gradient matches a `TArray`, and was not predicted** - it fell out of the scan:
   `Data` 26 load sites, `ArrayNum` 12, `ArrayMax` 1. Exactly the descending frequency a
   `{Data, ArrayNum, ArrayMax}` triple produces. A coincidental address has no reason to show it.

**Why the name search could never have worked, and it is not an anomaly:** no public UE3 locator
searches for a `GNames` string or symbol - all six working ones, six games, two codebases, scan for
that code shape. `GNames` is the SDK community's name for the global, not necessarily the engine's.
So the 2026-09-07 "no string in either encoding" wall was a METHOD problem, not a missing thing.

⚠️ **NOT confirmed, and confirmation is runtime-only.** The validator - read `Data[0]`, follow it,
read `+0x10`, require `"None"` - cannot run statically, because `FNameEntry` objects are
**heap-allocated at startup** from the compiled-in `REGISTER_NAME` table and are not in the exe on
disk. Four agreeing signals make a strong candidate, not a verified one. Strongest runner-up:
`0x0242B950` (34 load sites).

**`ProcessEvent`: its vtable index is NOT stable** (APB 60, Rocket League 67) and no public table
exists. `unrealsdk` avoids the index entirely - scan `ProcessEvent`'s **prologue** and detour it.
That is the recommended route for the other half of route (B). `[reported 2026-09-07]`
**→ Executed 2026-09-09, but NOT by the prologue: see §9e. The published prologue BYTES do not fit
this build; the address came from the assertion strings instead.**

⚠️ **Helix Mod's 3D Vision fix for Enslaved is itself a `d3d9.dll` wrapper** in `Binaries\Win32\`
`[reported 2026-09-07]`. Independent evidence that `d3d9` proxying is the right seam here - **and it
occupies the exact slot our proxy uses, so the two cannot both be installed.**

## 9e. ⭐⭐ `ProcessEvent` IS LOCATED: `0x00580990` (2026-09-09, `/pd`, no launch)

`UObject::ProcessEvent = 0x00580990` `[inferred-static 2026-09-09]`, bounds
`0x00580990..0x00580EFB` (1387 bytes), `ret 0Ch`. Tool:
`dev-archive/tools/find_processevent.py`. Evidence:
`dev-archive/recon/2026-09-09-processevent-located/`.

Four converging signals, none of them a name match:

1. it lives in **`UnCorSc.cpp`**, UE3 Core's script VM, via the §9c assertion-string route;
2. it asserts **`!HasAnyFlags(RF_Unreachable)` at `UnCorSc.cpp:6470`** — `ProcessEvent`'s own entry
   check on `this`. The pushed line number decodes as `0x1946` = 6470, which is what proves the
   argument decode rather than assuming it;
3. it is the **only VIRTUAL function** among that file's seven assertion-bearing functions —
   **1835 `.rdata` vtable slots** against **0** for every other one. There is no second candidate;
4. **`ret 0Ch`** = thiscall + three stack args = `ProcessEvent(UFunction*, void* Parms, void* Result)`.

⚠️ **NOT confirmed; confirmation is runtime-only.** The live check is to detour it and see whether
the first argument resolves through `GNames` to a script function name.

⚠️ **The vtable INDEX is UNRESOLVED and no number should be quoted.** A reading of 64 was produced
and **withdrawn the same session** `[disproved 2026-09-09]`: it came from treating runs of code
pointers in `.rdata` as vtables, but adjacent vtables here abut with no separator, so runs merge and
every index derived that way is an artefact. This costs nothing — the index is not the route (§9d
above, and `unrealsdk`'s detour needs only the address).

### ⚠️ The published prologue signature DOES NOT FIT this build `[verified-numerically 2026-09-09]`

Reported shape (`unrealsdk`, via `/gr` 2026-09-07b): `push ebp / mov ebp,esp / push -1 /
push <scopetable> / push <handler> / mov eax,fs:[0] / push eax / sub esp,0x50 / ...`

Actual `ProcessEvent` here: `55 8b ec 6a ff 68 d0 ca 91 01 64 a1 00 00 00 00 50 83 ec 54 ...` —
`push ebp / mov ebp,esp / push -1 / push 0x191cad0 / mov eax,fs:[0] / push eax / sub esp,0x54`.

| reported | actual | why |
| --- | --- | --- |
| **two** `push imm32` | **one** | this build uses the older `_except_handler3` frame; the handler comes from the scope table, not a second push |
| `sub esp,0x50` | `sub esp,0x54` | a different local-frame size |

**A scanner built from those literal bytes matches exactly ONE function in 23 MB of code, and it is
not `ProcessEvent`** — reproduce with `find_processevent.py --prologue`. **The invariant (an SEH +
/GS frame) holds; the byte pattern does not transfer.** Recorded because the `[PD]` row said "scan
the prologue", and taken literally that returns nothing and looks like the function is absent.

### ⭐ ASLR is OFF — the static addresses ARE the runtime addresses

`Enslaved.exe` has `DYNAMIC_BASE` clear and image base `0x00400000`
`[measured 2026-09-09]`, so no runtime scanning or rebasing is needed for any address in §9d/§9e.
The proxy probe still checks `GetModuleHandle(NULL)` and refuses to read if the base differs.

### The UObject probe (built 2026-09-09, deployed, NEVER RUN)

`staging/enslaved-vr/proxy-d3d9/` — `[uobject] Probe=1` in `d3d9_proxy.ini`. Read-only: it never
calls `ProcessEvent`, never writes engine memory, and guards every read with `VirtualQuery`.
Validates the `GObjObjects` shape, requires element 0's vtable to be in-module, validates `GNames`
via entry 0 == `"None"` (which also tests `FNameEntry +0x10`), **calibrates `UObject::Name` instead
of assuming it**, and reports the live `PlayerController`.
`[compile-verified 2026-09-09]`, `-Wall -Wextra` clean, 9/9 exports.

⚠️ **A self-test against synthetic memory caught a real bug before any launch**
`[verified-numerically 2026-09-09, n=8 checks]`. **FName index 0 is the legal name `"None"`, so an
all-zero field resolves for 100% of objects** and calibration picked the first zero-filled offset.
Fixed by scoring only non-zero indices and requiring ≥4 distinct names. Generalisable: *any
FName-index heuristic that counts successful lookups must exclude index 0.*

## 9c. ⭐ `DO_CHECK` IS ON IN THIS RETAIL BUILD — assertion strings are a navigational resource for the WHOLE binary

*Folded from `engine-research/inbox/2026-09-05-gr-gobjobjects-is-an-assertion-string-and-do-check-is-on.md`
(`/gr`), then executed live on 2026-09-07. That drop also **supersedes** the 2026-09-04
⚠️ **NARROWED 2026-09-08:** this was written of the generator family and is true only of
`UE3SDKGenerator` and `CodeRed`. **`polivilas/UnrealEngineSDKGenerator` ships real, filled-in
signatures for six games** - and its UT3 signature is what located `GNames` (§9d). Original
wording follows, scoped to those two repos:
external-research claim that those two UE3 SDK generators "ship patterns" - they ship a `FindPattern`
harness with every pattern set to the literal string `"null"`; the pattern is per-game and is the
thing you have to find `[verified-live 2026-09-05, n=1 API read]`.*

UE3's assertion macro stringifies the asserted expression:

```
#define check(expr) { if(!(expr)) appFailAssert( #expr, __FILE__, __LINE__ ); ... }
```

`GObjObjects` is **never a string literal in UE3 source**, so seven copies of it in `Enslaved.exe`
means `DO_CHECK` was left enabled in a shipping build. Three consequences, all of which make hunting
this binary cheaper:

1. **`appFailAssert` is called from inside the function that tests the global**, so the global sits
   in the preceding instructions as a **direct memory operand** — the address itself, not a hint.
2. **`__FILE__` is pushed in the same call**, giving a free confirmation beside every hit and telling
   you which assertion you are standing in.
3. **Before hand-building a byte signature for anything in this binary, grep the strings for the
   symbol name first.**

### ✅ Executed 2026-09-07 — the addresses `[inferred-static 2026-09-07]`

```
UObject::GObjObjects    .Data = 0x0242B984  .ArrayNum = 0x0242B988  .ArrayMax = 0x0242B98C
UObject::GObjAvailable  .Data = 0x0242B990  .ArrayNum = 0x0242B994  .ArrayMax = 0x0242B998
appFailAssert                 = 0x0058E580
ImageBase 0x00400000   .text 0x00401000   .data 0x02312000
```

Cross-checked by three different assertion expressions in three different functions —
`cmp dword ptr [0x242B988],0` is `GObjObjects.Num()==0`; `mov eax,[0x242B984]` +
`cmp dword ptr [eax+edi*4],0` is `GObjObjects(InIndex)==NULL`; and `IsValidIndex` uses `[0x242B988]`
as its bound. **Fourth, independent corroboration:** `GObjAvailable` lands exactly 12 bytes
(`sizeof(TArray)` on 32-bit) after `GObjObjects`, as consecutive statics, and both show `ArrayNum` at
`Data+4`.

`__FILE__` beside the `Array.h` assertion gives the studio's build path —
`e:\projects\congo\enslavedmaster\masterarchives\unrealengine3\development\src\core\inc\Array.h`.
The 7th occurrence is a decorated MSVC symbol at `0x021C09BC`
(`?GObjObjects@UObject@@0V?$TArray@PAVUObject@@VFDefaultAllocator@@@@A`), not yet chased.

### ⚠️ Encoding: this binary needs BOTH scans

`TCHAR` is `wchar_t`, so engine *names* are UTF-16 while assertion strings are narrow ASCII
`[measured 2026-09-07]`:

| symbol | ASCII | UTF-16 |
| --- | --- | --- |
| `GObjObjects` | 7 | 0 |
| `GObjAvailable` | 4 | 0 |
| `ProcessEvent` | 1 | 2 |
| `CheatManager` | 0 | 3 |
| `ConsoleCommand` | 0 | 4 |
| `GNames` | **0** | **0** |
| `AddCheats`, `ToggleDebugCamera`, `AllowCheats` | 0 | 0 |

**`GNames` has no string at all** — the assertion route does not reach it and it needs a different
locator. The three script-side names are absent as predicted (compressed `.u` packages).
Tool: `dev-archive/tools/find_uobject_globals.py`.

## 9d. ⛔️ 2026-09-07: THE PAUSE MENU COULD NOT BE OPENED, AND `[Engine.PlayerInput]` IS GAMEPAD-ONLY

> **✅ SOLVED 2026-09-09 — the cause was OUR ini edit, specifically the invented section.**
> A three-launch A/B on the dev PC: the reverted ini pauses on the first Escape; the 2026-09-07 test
> ini restored verbatim reproduces the failure exactly (Escape and F-keys inert, `W` still walks);
> the same ini **minus the `[MonkeyGame.MKInput]` section** pauses again on the first press
> `[verified-live 2026-09-09, n=1 A/B pair]`.
>
> **Rule: never create a config section this build does not ship.** Adding `Bindings=` lines to a
> section that already exists is harmless — run 3 carried two and behaved normally. Inventing a
> section name silently disables Escape and the F-keys while leaving character movement alive, with
> no error anywhere, and it reads exactly like "this game ignores the keyboard".
>
> **The 2026-09-04 self-healing proxy is exonerated** — it was installed and running in all three
> launches, including both that worked. The concurrent-`/lm` focus-contention hypothesis is no longer
> needed to explain this failure; it stays a real hazard in general `[hypothesis]`.
>
> **Still true, and now with a control:** `F4 -> DoPause` and `F2 -> Pause`, both live in
> `[Engine.PlayerInput]` in run 3, **fired nothing** while Escape worked in the same session
> `[verified-live 2026-09-09, n=1]`. Bindings added to that section are inert in this build, so the
> exec question still has no valid control. Notes:
> `modding-notes/2026-09-09-the-pause-blocker-was-an-invented-ini-section-and-the-reset-rearm-works.md`


**Operationally the most important thing to know before the next launch.** Full detail:
`modding-notes/2026-09-07-gobjobjects-is-located-and-the-pause-menu-is-unreachable.md`.

Keyboard **movement** works (`W`/`S` walk Monkey, confirmed by eye). Nothing else does:
`Escape` (twice, two hold lengths, two locations), `F4`→`DoPause`, `F1`/`F2`/`F3`, the shipped
`F8`→`stat fps` and `F12`→`FreezeRendering` — all inert. A **virtual X360 pad enumerated** (the game
raised a "Controller Connected" toast) but **`START` did not pause and `thumbLX=29490` did not move
Monkey** — the exact value that verified the pad on the home PC on 2026-09-03d
`[verified-live 2026-09-07, n=1 session]`.

⇒ no pause menu ⇒ no checkpoint restart, no options screen, no route to the main menu ⇒ **the reset
row (§9a) cannot be exercised on the dev PC as things stand**, and the session had to close through
`WM_CLOSE` rather than the profile's graceful menu route.

### ⭐ Why this reframes the exec question rather than answering it

Dumping every `Bindings=` line in `[Engine.PlayerInput]`: it holds the action **aliases** and the
**`XboxTypeS_*` gamepad bindings**, and **not one keyboard key** `[measured 2026-09-07]`. `DoPause`
is reachable from exactly one entry, `XboxTypeS_Start`. Yet `W` walks Monkey — so keyboard movement
does not come from this ini at all.

**"The exec command did not fire" and "a keyboard binding added to a gamepad-only section is inert"
are indistinguishable observations.** That is a cheaper explanation than "exec dispatch is stripped",
so the exec question remains `[hypothesis]`; 2026-09-07 did not lift the 2026-09-04 downgrade.
Relatedly, **`Escape` is bound only in `[NTGameFramework.NTCam_DebugInput]`** (line 171,
`CloseEditorViewport | DoPause`) — the class 2026-09-04 proved is dead — so if Escape ever paused
this game, it did so through native handling, not through config.
**`[MonkeyGame.MKInput]` does not exist in this build's shipped ini**; it was created to test the
community report and nothing in it fired.

### ⚠️ Two untested suspects, and one of them is the build the reset row depends on

The profile records `gameplay -> main_menu` via `Escape` as `verified-live 2026-09-03` **on this same
dev PC**. Something changed since:

1. the 2026-09-07 ini edit (**reverted**; stock restored, the test copy kept beside it), or
2. **the 2026-09-04 self-healing proxy, which had never been run before 2026-09-07** (`d3d9.dll`
   dated Sep 4 13:55; that session was `/pd`, no launch). It hooks `BeginStateBlock` /
   `EndStateBlock` — which earlier builds did not — and re-patches five vtable slots every `Present`.

If (2) is the cause, that build cannot be trusted to answer §9a until it is fixed, and the reading
table written against its output is void. Two relaunches settle it; the decision tree is in the
modding note.

### ❌ There is no menu-free way to force a Reset `[disproved 2026-09-07]`

`ALT+ENTER` (the game *did* revert its window style; the proxy restyled it back at `present#8700`)
and external `SetWindowPos` resizes to 1024x576 / 1600x900 both produced **zero** `[reset]` lines.
The backbuffer stays 1920x1080 and D3D stretches it into the window, so resizing never invalidates
the device. A Reset here genuinely requires the in-game resolution change or a checkpoint restart —
both behind the pause menu.

### ⚠️ Turn wiggle OFF before judging anything by image comparison

With `Mode=0` alternate frames are different eyes and differ by **~27.5 mean luma**, which swamps
every other signal and is stable enough to look like one. On 2026-09-07 a
`27.58 / 0.00 / 27.58 / 0.00` series was briefly read as a pause; it was Monkey standing still (a
static scene renders exactly two images, so same-eye pairs are byte-identical). **Set `Mode=1` or
`Mode=2` in `d3d9_proxy.ini` for any run that judges by image comparison**, and look at the frame.

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
