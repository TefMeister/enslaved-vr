# A 3D Vision fix for this exact binary exists: motion blur must be OFF, and it names the effects that break in stereo

Filed by: `/gr`, 2026-09-02
Supersedes: `external-research/topics/2026-08-24-ue3-native-stereo-and-community-tooling.md` §2 ("no Helix Mod / 3DMigoto entry exists for Enslaved")
Topics: `external-research/topics/2026-09-02b-a-3d-vision-fix-for-this-exact-game-exists-and-it-names-the-effects-that-break.md` and `…-09-02c-the-world-unit-scale-brackets-separation-6-0-is-probably-already-close.md`
Dossier sections: §4 (the 310 pixel-stage shaders), §9 (open risks), §7 (console/exec channel)

All `[reported 2026-09-02]` unless noted; study material only, nothing copied, and its DLL must never be installed beside our proxy.

- **The fix exists.** eqzitara, Helix Mod, 2013-10-28 (updated 2013-12-21), for the Premium Edition, installed into `Binaries\Win32\`. This lane's 2026-08-24 "no entry exists" claim is **`[disproved 2026-09-02]`**.
- **⭐ Motion blur must be disabled for stereo** (`MotionBlur = False` in `MonkeyEngine.ini`, or the in-game option). Motion blur reprojects using the view-projection — the pixel-stage copy our hook does not touch. **Set it before the next stereo run so the separation retune is not judged through it.**
- **What it had to fix = our 310-shader prediction, independently:** shadows, crosshairs, "visual effects", menu screens. **HUD depth stayed broken even for them** — consistent with the ortho-`c0` item already on the board. Shadows are now the highest-prior thing to watch on a stereo run, not a general "watch for anything odd".
- **Two convergence regimes** (F3 cinematic, F4 gameplay, auto-switch after the tutorial) — the cutscene and chase cameras sit at different depth scales; expect to tune them separately.
- **Separation scale:** UE3 is 1 UU = 1–2 cm (Epic's own guidance is not to vary beyond ×2), so `Separation=6.0` is 6–12 cm — already at or above one IPD (~6.4 cm). The "small hop" symptom fits a correct-magnitude value shown alternately on a flat screen. Raise 10× as a **linearity diagnostic**, not as a search for the right number, then come back down. Cheap way to pin the scale: read the chase camera's distances in `MonkeyChaseCamera.ini` / `DefaultChaseCamera.ini` against how far the camera plainly is on screen.
- **`useAutoTiltup` can be turned off** in the chase-camera ini — an automatic camera tilt is a VR comfort hazard, and the game ships the off-switch (same class as Alan Wake's `-rigidcamera`).
- **Exec commands reach this build via key bindings** — `Bindings=(Name="F1",Command="FOV 0")` under `[MonkeyGame.MKInput]` in `MonkeyInput.ini` is reported working, so §7's "console class may be stripped" risk has a working command channel regardless.
