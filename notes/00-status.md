# Enslaved VR — dev-archive status / index

This is the chronological, in-progress record of the Enslaved: Odyssey to the
West VR reverse-engineering effort. It mirrors the session history; the
readable field-notes ledger lives in `enslaved-vr-modding-notes`, and the
distilled engine truth in `enslaved-vr-engine-research`.

**Current status (2026-08-21):** Foothold established and working in-game. The
logging `d3d9.dll` proxy runs inside the shipped game and has produced the
first real capture of the vertex-shader constant traffic. The pivotal open
question — is the camera in a shared view-projection register or baked into
per-object World×ViewProjection matrices — is set up to be answered by the next
capture (the proxy now auto-flags shared matrices).

## Session index

- [`01-project-and-repos.md`](01-project-and-repos.md) — project setup, the
  five-repo layout, backups.
- [`02-static-recon.md`](02-static-recon.md) — engine identification from the
  installed files (UE3/NTEngine, 32-bit D3D9, clean binary, console bound).
- [`03-d3d9-logging-proxy.md`](03-d3d9-logging-proxy.md) — building and
  validating the fail-safe d3d9 logging proxy.
- [`04-first-ingame-capture.md`](04-first-ingame-capture.md) — first in-game
  run, windowed-mode switch, register-histogram analysis, shared-matrix
  instrument upgrade.

## Raw dumps

- [`recon/enslaved_exe_imports_d3d9.txt`](recon/enslaved_exe_imports_d3d9.txt)
  — the game's d3d9 import set (interface metadata we generated).

## Where the code is

The proxy source is unverified work and lives in the private
`enslaved-vr-staging` repo (`proxy-d3d9/`) until it has been tested in VR at
home; it graduates to the public repos after that. These notes record what was
done and why.
