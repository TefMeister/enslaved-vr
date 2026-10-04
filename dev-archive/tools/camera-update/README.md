# camera-update: how the per-tick camera update was found (2026-10-04, static)

Two small readers. Neither touches the running game.

- `xref.py <hex VA> ...`: finds code that uses an address (as an immediate or a displacement)
  in `Enslaved.exe`, and `dis(va, n, back)` disassembles around a spot. Used to go from the
  wide string `UpdateCamera` (0x01C040A0) to its FName global (0x0243AC10) to the one native
  caller of `eventUpdateCamera` (the camera loop at 0x008BEF70..0x008BEFE6).
- `script_funcs.py <Class> ...`: lists a script class's functions from the cooked packages with
  their flags (`NATIVE`, `event`, `static`). Needs `staging/enslaved-vr/reader-tools/ue3_props.py`.
  It showed that `Camera.FillCameraCache`, `UpdateCamera` and `GetCameraViewPoint` are all
  script here, not native.

Write-up: `modding-notes/2026-10-04-pd-the-camera-is-decided-in-one-loop-and-the-yaw-test-is-built.md`,
dossier §9h.
