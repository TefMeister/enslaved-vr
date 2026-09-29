# Nobody has windowed Enslaved's DirectX 10 mode in public; the DX9 successes do not transfer

*For the board's decided road (Tefa, 2026-09-29): VR output through the game's DirectX 10 mode, which on the dev PC
ignores `-windowed ResX ResY` and rewrites `Fullscreen=False` back to True.*

## What people report `[reported]`

- **Steam discussions** (app 245280): `-windowed` does not start the game in a 720p window, Engine.ini edits did not
  work, and Alt+Enter does nothing. The threads end unresolved.
- **DxWnd** (its SourceForge forum): windowing worked after updating DxWnd and setting its "Initial resolution" flag,
  so the game believed higher resolutions existed from the start (it boots at 800×600). The user's log shows
  `CreateDevice: D3DVersion=9`, so that success was the **DirectX 9** path.
- PCGamingWiki's "Essential Fix Collection" (resolution and frame-rate fixes) could not be read by an automated
  fetch (HTTP 403); whether it touches the DX10 mode is unknown. ⚠️ Not a negative.

## What it means for this project `[hypothesis]`

There is no ready-made DX10 windowing trick to borrow. Our own DX10-side proxy has to do it, which is also the usual
technique: at swap-chain creation (`IDXGIFactory::CreateSwapChain`, or `D3D10CreateDeviceAndSwapChain`) force
`Windowed = TRUE` and a 1280×720 back buffer, refuse `IDXGISwapChain::SetFullscreenState(TRUE)`, and size the window's
client area to match. The DX9 proxy already does the equivalent, so the logic ports. It is the first job of the DX10
re-plan on the board.

## Sources

- Steam Community discussions for app 245280: "Game will not start in windowed mode", "Help to Windowed Mode",
  "Windowed mode?".
- DxWnd general discussion on SourceForge, the Enslaved threads (ebb1ab40, 41a8cbf7).
- PCGamingWiki community files: Enslaved Essential Fix Collection (not readable by automated fetch).
