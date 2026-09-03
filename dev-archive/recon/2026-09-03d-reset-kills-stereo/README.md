# 2026-09-03d — evidence: a Reset disarms the stereo, and glancing-angle water is clean

Home PC, `/lm`, autonomous. Write-up:
`modding-notes/2026-09-03d-reset-kills-the-stereo-and-glancing-water-measures-clean.md`

| file | what it shows |
| --- | --- |
| `d3d9_proxy_log-run2-reset-at-frame120000.txt` | the full proxy log of the run that reset. Search `[reset]`: one healthy `offset 2054` summary follows it, then `offset 0` for the remaining 22,500+ frames. `Present` keeps advancing throughout. |
| `water-chapter4-glancing-angle.jpg` | the measured scene — chapter 4's flooded pool at a shallow glancing angle, static camera |
| `water-bottom-row-measured-dx.jpg` | the same frame with the bottom tile row annotated with its measured per-tile dx (red = flagged as un-offset) |
| `suspect-tile-left-is-the-HUD-radial.jpg` | why the left flag was a false positive: the tile is dominated by the `LEAP`/`EMP` ability radial |
| `suspect-tile-right-is-the-item-counters.jpg` | why the right flag was a false positive: the item counters |
| `facade-scene-depth-gradient.jpg` | the earlier scene where the depth gradient was reproduced (far alley ~+0.95, near foliage ~+4.8) |

⚠️ The proxy log is overwritten on every launch — it is copied here because it exists nowhere else.
