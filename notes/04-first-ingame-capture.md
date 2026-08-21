# 04 — First in-game capture, windowed mode, instrument upgrade

**Session 3, 2026-08-21.**

## Proxy confirmed working in-game

The proxy ran inside the shipped game and produced a 2890-line log of real
gameplay. Device creation (from the log):

```
[CreateDevice] adapter=0 devtype=1 behavior=0x00000142
   BackBuffer 1920x1080 fmt=21 count=1 windowed=0 swap=1
   MultiSample=0 RefreshHz=0 PresentInterval=0x80000000
```

- `fmt=21` = D3DFMT_A8R8G8B8.
- `PresentInterval=0x80000000` = IMMEDIATE (vsync off — matches
  `UseVsync=False`).
- `behavior=0x142` = HARDWARE_VERTEXPROCESSING | PUREDEVICE | FPU_PRESERVE.

## Windowed mode

Switched the game to windowed 1280×720 by editing the **per-user** config
`Documents\My Games\UnrealEngine3\MonkeyGame\Config\MonkeyEngine.ini`
(`[SystemSettings] Fullscreen=False`, `ResX=1280`, `ResY=720`). That user
config is authoritative — the game-dir INIs are only defaults — and there is no
competing `StartupFullscreen` key under `[WinDrv.WindowsClient]`. Windowed mode
also makes RE far easier (alt-tab, console, debugger).

## VS-constant histogram analysis (gameplay frame ~600)

| Register | Vec | Calls/frame | Reading |
|---|---|---|---|
| `c6`  | x4 | 189 | busiest 4×4 — main base-pass world/WVP matrix |
| `c231`(+`c235` x3) | x4 | 124 | separate vertex factory (likely skinned characters); c235 is a 4×3 LocalToWorld |
| `c0`  | x4 | 47  | per-object 4×4 matrix |
| `c10` | x4 | 19  | per-object 4×4 matrix |
| c4/c5, c11–c21, c236–c248 | x1 | various | scalar/vector params (light, fog, colour) |

**Key observation:** every 4×4 upload in gameplay is *per-object*; none appears
once-per-frame. That strongly suggests the camera is folded into a per-draw
World×ViewProjection rather than sitting in one shared view-projection
register. Distinguishing shared-VP from per-object-WVP is the pivotal question
for the injection strategy.

(During loading/menu, frame ~240 showed `c0 x128` and `c128 x128` — large
one-shot arrays, i.e. skinning palettes, not camera data.)

## Instrument upgrade — shared-matrix detection

To settle the question directly, the proxy was upgraded to fingerprint each
matrix register per frame (FNV-1a over the first 4×4 block). If every upload to
a register within a frame carries an identical value, it is flagged as a
**SHARED matrix (view-projection candidate)** and its 4×4 is auto-dumped; a
register that varies per draw is not flagged. Validated off-game: a constant
register flagged SHARED and dumped its matrix; a per-draw register did not.
Rebuilt and redeployed.

## Resume point

Relaunch (now windowed), play a few seconds of real gameplay, and grep
`Binaries\Win32\d3d9_proxy_log.txt` for `SHARED matrix`:

- **If a register is flagged SHARED** → likely the pure view-projection, a
  clean single injection point. Confirm by moving the camera and re-capturing.
- **If nothing is flagged** → camera is baked into per-object WVP (c0/c6/c231);
  plan shifts to intercepting those per-draw matrices and replacing the view
  portion. More involved, still workable.

Either result is the go/no-go input for the keystone camera-perturbation proof.
Also worth trying the Tilde console now that the game is windowed.
