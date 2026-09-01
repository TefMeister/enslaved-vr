# Status / Progress Ledger — Enslaved VR

> One entry per working session, newest first. Each entry ends with a resume
> point so the next session (possibly on another machine) knows exactly where
> to pick up.

---

## 2026-09-02 — `/pd` static pass (home PC, no launch)

**Done:**
- `/gr` inbox check answered: **no NVIDIA 3D Vision branch** in this build (zero `nvstereo` in every
  shader cache, the exe and the `.usf`; no `AllowNvidiaStereo3d`).
- Re-read the SM3/SM2 `CTAB` tables **with the shader stage**: every vertex-shader
  `ViewProjectionMatrix` is at `c0`; the `c3`/`c10` ones (310) are **pixel** shaders. Dossier §4
  corrected, proxy comment corrected (no behaviour change).
- Proxy **built here** (llvm-mingw i686, 9 exports) and **deployed** to `Binaries\Win32` — the home
  install had none; two files added, nothing overwritten.

**Resume point:** launch once with stereo off (log must appear), then `[stereo] Enabled=1` and look
for the rock. Full order in `2026-09-02-viewprojection-c3-c10-are-pixel-shaders-no-nvidia-stereo-branch.md` §4.

---

## 2026-08-21 — Session 3: first in-game capture, windowed mode, instrument upgrade

**Done:**
- Confirmed the proxy runs **in-game**: it produced a 2890-line log of real
  gameplay. Device created at 1920x1080, fullscreen (windowed=0), fmt=21
  (D3DFMT_A8R8G8B8), PresentInterval=0x80000000 (IMMEDIATE, i.e. vsync off,
  matches `UseVsync=False`).
- **Switched the game to windowed 1280x720** by editing the per-user config
  `Documents\My Games\UnrealEngine3\MonkeyGame\Config\MonkeyEngine.ini`
  ([SystemSettings] `Fullscreen=False`, `ResX=1280`, `ResY=720`). This is the
  authoritative config (the in-repo game-dir INIs are defaults); no competing
  `StartupFullscreen` key exists. Windowed mode also makes RE far easier
  (alt-tab, console, debugger).
- **Analysed the VS-constant histogram** (gameplay frame ~600):
  - Per-object 4x4 matrices at `c0` (x4, 47 draws), `c6` (x4, 189 draws),
    `c10` (x4, 19), and `c231` (x4, 124) — the last paired with `c235` (x3,
    124 = a 4x3 LocalToWorld). High registers (c231/c235) = a distinct vertex
    factory, likely skinned characters.
  - Many x1 scalars (c4/c5, c11-c21, c236-c248) = light/fog/colour params.
  - **Key point:** in gameplay, every 4x4 upload is per-object; none appears
    once-per-frame. That means the camera is probably folded into a per-draw
    World x ViewProjection, not sitting in one shared register. Deciding
    shared-VP vs per-object-WVP is the pivotal question for the injection
    strategy.
- **Upgraded the instrument** to answer that directly: the proxy now
  fingerprints each matrix register per frame and flags any register whose 4x4
  value is **identical across all draws in the frame** as a SHARED
  view-projection candidate, auto-dumping its matrix. Validated off-game (a
  constant register flags SHARED + dumps; a per-draw register does not).
  Rebuilt and redeployed.

**Resume point:** relaunch (now windowed) and play a few seconds of real
gameplay. In `Binaries\Win32\d3d9_proxy_log.txt` look for any
`<== SHARED matrix` line:
  - If a register is flagged SHARED, that is very likely the pure
    view-projection — the clean single injection point. Note it and its dumped
    values; move the camera and re-capture to confirm the numbers track the
    camera.
  - If NOTHING is flagged SHARED, the camera is baked into per-object WVP
    matrices (c0/c6/c231). Then the plan shifts to intercepting those per-draw
    matrices and decomposing/replacing the view portion — workable, just more
    involved. Either way this capture is the go/no-go input for the keystone.
Also still worth trying the Tilde console now that we are windowed.

---

## 2026-08-21 — Session 2: d3d9 logging proxy built and validated

**Done:**
- Confirmed from the import table that `Enslaved.exe` imports only four names
  from d3d9.dll: `Direct3DCreate9`, `D3DPERF_BeginEvent`, `D3DPERF_EndEvent`,
  `D3DPERF_SetOptions`. Clean, minimal surface for a proxy.
- Built a fail-safe `d3d9.dll` logging proxy (llvm-mingw, 32-bit) in staging
  under `proxy-d3d9/`. It:
  - forwards all real d3d9 exports (resolved from the system DLL at load);
  - intercepts `Direct3DCreate9` and patches `IDirect3D9::CreateDevice`
    (vtable slot 16), then patches the device vtable for `Present` (17),
    `Reset` (16), and `SetVertexShaderConstantF` (94);
  - logs CreateDevice params, a per-frame histogram of which VS constant
    registers get uploaded (hot path does no I/O), and an optional 4×4 dump of
    a watched register — the instrument for finding the view-projection matrix.
  - Config via `d3d9_proxy.ini`; every path is fail-safe passthrough.
- Verified the built DLL exports the nine names **undecorated** (matching the
  game's undecorated imports).
- Smoke-tested off-game with a 32-bit host (HAL device on a hidden window,
  3 frames): proxy loaded, real d3d9 resolved, `Direct3DCreate9` intercepted,
  both vtables patched, CreateDevice logged, and the histogram printed
  `c0 x1 : 1` correctly. No crash.
- **Deployed** `d3d9.dll` + `d3d9_proxy.ini` into `Binaries\Win32\` (no
  pre-existing d3d9.dll there; delete the DLL to revert).

**Resume point:** launch the game with the proxy installed, play a few seconds
of real gameplay, then read `Binaries\Win32\d3d9_proxy_log.txt`. In the
per-frame histograms find the register uploaded as `x4` (a full 4×4) once per
object/frame — the view-projection candidate. Set `DumpRegister` to it,
relaunch, read the values, and confirm by moving the in-game camera and
watching which numbers change. That feeds dossier sections 4–6 and sets up the
keystone camera-perturbation proof. (Also still worth doing: test the Tilde
console in-game.)

---

## 2026-08-21 — Session 1: project setup and static recon

**Done:**
- Created the five project repositories (`-mod`, `-dev-archive`,
  `-modding-notes`, `-staging`, `-engine-research`) per the standard layout,
  with local backup clones in the usual backups folder.
- Copied the engine-agnostic VR playbook into `enslaved-vr-engine-research`
  and started this game's `ENGINE-DOSSIER.md`.
- Static recon of the installed game (no live run yet). Established:
  - **Unreal Engine 3** (circa 2009–2010 branch) plus Ninja Theory's custom
    **NTEngine** layer; internal codename "Congo"; UE3 project name
    `MonkeyGame`.
  - **32-bit, Direct3D 9** at runtime (`AllowD3D10=False`; D3D10/11 RHI code
    is compiled in but config-gated off).
  - **Clean, unpacked executable** — standard PE sections, no SteamStub, no
    packer, relocations present, and assert strings with full source paths
    throughout. Near-ideal static-RE conditions.
  - **Developer console keys are still bound** in the shipping configs
    (`ConsoleKey=Tilde`, `TypeKey=Tab`).
  - Middleware: PhysX 2.x, NaturalMotion Morpheme, Bink, FaceFX, Fonix TTS,
    Steamworks — and, notably, the game itself ships `EasyHook32.dll`.
  - Custom viewport client: `NTEngine.NTReplayGameViewportClient`.
- Chosen foothold route: **`d3d9.dll` proxy** logging device creation,
  `Present`, and `SetVertexShaderConstantF` traffic, then locate the
  view-projection registers and do the keystone camera-perturbation proof.

**Feasibility read after session 1:** strong. This is a well-trodden engine
class for VR injection (UE3 on D3D9), the binary is friendly, and there are
multiple viable altitudes for owning the camera. Main open risks: possible
console stripping in the shipping build, NTEngine camera-path divergence from
stock UE3, D3D9→VR-compositor submission plumbing, and third-person comfort
design (deferred until the North Star renders).

**Resume point:** launch the game once on the dev machine; press Tilde to test
the console; note the per-user config path under `Documents`; then build the
logging `d3d9.dll` proxy and capture one frame's constant traffic. Dossier
sections 4–6 are waiting on that capture.
