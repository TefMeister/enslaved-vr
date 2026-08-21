# Status / Progress Ledger — Enslaved VR

> One entry per working session, newest first. Each entry ends with a resume
> point so the next session (possibly on another machine) knows exactly where
> to pick up.

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
