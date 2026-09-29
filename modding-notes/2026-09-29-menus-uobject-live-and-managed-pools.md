# 2026-09-29: menus automated, the UE3 globals confirmed live, and the pool answer

*Dev PC, `/lm`. Tefa rehearsed and recorded the menus; the rest was driven by Claude.*

## Menus

One recording by Tefa became three routes: closed → gameplay (proven by opening and closing the pause menu),
gameplay → main menu (pause → EXIT TO MAIN MENU → confirm), main menu → closed (QUIT). The whole cycle replays in
60-66 s, twice `[verified-live 2026-09-29, n=2]`. The game opens a tiny 160×28 window with the same title first;
Menu-o-matiC now picks the largest match (lanes 0.35.1). Routes: `ai-game-control-profiles/routes/enslaved/`.

## The UE3 globals are real

The read-only UObject probe (`[uobject] Probe=1`, switched back off afterwards) ran during Tefa's rehearsal:
`ProcessEvent` prologue at `0x00580990` matches the file; `GObjObjects` shape OK (124,758 objects, the first 4,000
all live with in-module vtables); `GNames` entry 0 is "None"; `UObject::Name` at +0x28 `[verified-live 2026-09-29,
n=1]`. The PlayerController matches it printed are the class and function objects of that name, not the live
controller instance, so route (B) is not yet proven. Evidence: `dev-archive/recon/2026-09-29-uobject-probe-live/`.

## D3DPOOL_MANAGED: the D3D9Ex upgrade is a project, not a one-liner

Build `c3bab82d5324` counts which pool each texture and buffer is created in (`[pools] Count=1`, one launch, kept off
the stereo run). Into gameplay: of 4,500 creations, **4,455 were MANAGED** (2,481 textures, 12 cubes, 1,550 vertex
buffers, 412 index buffers); only 43 DEFAULT `[verified-live 2026-09-29, n=1]`. D3D9Ex refuses MANAGED, so an Ex
device would mean moving all of that to DEFAULT and restoring it on device loss. The board's fallback, the public
`-d3d10` launch option, becomes the better road to a shared texture for VR output. Evidence:
`dev-archive/recon/2026-09-29-pools/`. The counter stays in the build, off.

## Later: the DirectX 10 mode runs (Tefa chose this road)

Tefa decided VR output goes through the game's DirectX 10 mode (reworking the MANAGED memory "will cause ALL sorts
of issues", and side-by-side is not an option). The quick check:

- **Started directly** (`Enslaved.exe -d3d10 ...`): it crashed at start (`unreal-v6165-2026.09.29-17.00.54.dmp` in
  `Documents/My Games/UnrealEngine3/MonkeyGame/Logs`), and a second copy came up full screen. Start it through Steam.
- **Through Steam** (`steam://run/245280//-d3d10/`): it runs, loads `d3d10.dll`, `d3d10core.dll`, `dxgi.dll` and
  `d3dx10_41.dll`, and closes cleanly on WM_CLOSE `[verified-live 2026-09-29, n=2]`. Our `d3d9.dll` still loads but is
  not the renderer.
- **It will not window itself:** `-windowed ResX=1280 ResY=720` was ignored, and `Fullscreen=False` / `ResX=1280`
  written into `Documents/My Games/UnrealEngine3/MonkeyGame/Config/MonkeyEngine.ini` was rewritten back to
  `Fullscreen=True` / 1920×1080 at start-up (the file came back byte-identical to its backup) `[verified-live
  2026-09-29, n=1]`. In D3D9 mode our proxy forces the window; in D3D10 mode a proxy of ours will have to do the same
  (DXGI swap-chain override), so the window is part of the D3D10 re-plan, and until then a D3D10 run is full screen.
