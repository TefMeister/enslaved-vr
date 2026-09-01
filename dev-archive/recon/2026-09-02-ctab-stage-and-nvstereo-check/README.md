# 2026-09-02 — CTAB shader-stage table + NVIDIA stereo-branch check (home PC, static)

`stage_table.py <RefShaderCache.upk> <name,name,...>` walks every D3D9 `CTAB` block and counts
`(name, stage, register, width)`; the stage comes from the shader version token 8 bytes before
`CTAB` (`0xFFFE` = vertex, `0xFFFF` = pixel). Outputs here are counts and names only — no game
content. `nvstereo-grep.txt` is the raw-byte negative for NVIDIA's 3D Vision UE3 branch.

Write-up: `modding-notes/2026-09-02-viewprojection-c3-c10-are-pixel-shaders-no-nvidia-stereo-branch.md`.
The game was not launched.
