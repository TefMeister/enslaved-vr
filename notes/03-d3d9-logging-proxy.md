# 03 — The d3d9 logging proxy

**Session 2, 2026-08-21.** Built the foothold: a fail-safe `d3d9.dll` logging
proxy. Source lives in `enslaved-vr-staging/proxy-d3d9/` (unverified work).

## Design

- **Forwards** every real d3d9 export to the genuine system DLL (resolved by
  absolute path from `System32`/`SysWOW64` at load, so no self-recursion).
  Exports the standard d3d9 surface (nine named exports), all **undecorated**
  to match the game's undecorated imports.
- **Intercepts `Direct3DCreate9`** → patches `IDirect3D9::CreateDevice`
  (vtable slot 16) → on device creation patches the device vtable for
  `Present` (17), `Reset` (16), and `SetVertexShaderConstantF` (94).
- **Logs:** CreateDevice params; frame counter at Present; a per-frame
  histogram of which VS constant registers are uploaded (start register ×
  vector4 count : call count). The hot path does **no file I/O** — only
  counter bumps — so it stays safe at thousands of calls per frame.
- **Doctrine:** fail-safe passthrough everywhere; any error falls through to
  the stock game and never crashes it.
- Configurable via `d3d9_proxy.ini` (log file, dump interval, watch register,
  max verbose frames).

## Toolchain

Built with llvm-mingw (32-bit clang). Exports controlled by a `.def` file;
`--enable-stdcall-fixup` maps the undecorated def names onto the stdcall
symbols. The build is reproducible via the repo's `build.ps1`.

## Validation (off-game)

A 32-bit smoke-test host created a HAL device against a hidden window and ran
three frames. The proxy loaded, resolved the real d3d9, intercepted
`Direct3DCreate9`, patched both vtables, logged CreateDevice params, and
produced the per-frame histogram correctly (`c0 x1 : 1`). No crash. The 4×4
watch-dump correctly stayed silent when only a single vector was uploaded
(guard requires four).

## Verified export table

The built DLL exported exactly the nine expected names, all undecorated,
including the four the game imports.
