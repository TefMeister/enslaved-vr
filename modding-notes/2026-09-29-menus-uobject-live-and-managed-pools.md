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
