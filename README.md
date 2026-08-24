# Enslaved: Odyssey to the West — VR Engine Research

Reverse-engineering research toward a 6DOF VR conversion of **Enslaved:
Odyssey to the West — Premium Edition** (Ninja Theory, 2010; PC port 2013), a
game built on Unreal Engine 3 with Ninja Theory's custom "NTEngine" layer and
no existing VR conversion.

This repository holds two things:

- **[`PLAYBOOK.md`](PLAYBOOK.md)** — a reusable, engine-agnostic, point-by-point
  method for taking *any* game whose engine nobody has converted to VR and
  getting it there. It is oriented around one North Star: **the game rendering
  in a headset with head tracking**, with everything else built on top. The same
  playbook is copied into each of our VR projects' research repos.
- **[`ENGINE-DOSSIER.md`](ENGINE-DOSSIER.md)** — the distilled, current-truth
  reference for *this* game's engine: renderer, how the camera transform
  reaches the GPU, the shader-constant mechanism, the pass inventory, the
  console/cvar cheat sheet, and the dead ends that cost us time so they don't
  cost the next engine's.

The blow-by-blow development history lives in the sibling repositories
(`enslaved-vr-dev-archive` for the messy in-progress record,
`enslaved-vr-modding-notes` for readable field notes). This repo is the
consolidated engine knowledge, not the diary.

## The six repositories for Enslaved VR

Everything for this project lives in six repositories, each with one job — so
you always know where to look. You are in **enslaved-vr-engine-research**.

| Repository | What lives here |
| --- | --- |
| [enslaved-vr-mod](https://github.com/TefMeister/enslaved-vr-mod) | The mod itself — releases only (not yet playable in VR). |
| [enslaved-vr-dev-archive](https://github.com/TefMeister/enslaved-vr-dev-archive) | Full development history — snapshots, probes, dead ends, raw recon. |
| [enslaved-vr-modding-notes](https://github.com/TefMeister/enslaved-vr-modding-notes) | Readable field notes / progress ledger. |
| [enslaved-vr-staging](https://github.com/TefMeister/enslaved-vr-staging) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| **enslaved-vr-engine-research** ← you are here | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [enslaved-vr-external-research](https://github.com/TefMeister/enslaved-vr-external-research) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Status

Initial static recon complete (2026-08-21). The target looks unusually
friendly: unpacked 32-bit D3D9 UE3 with assert strings intact and the
developer console still bound in the shipping configs. Next milestone is the
live capture that confirms how the view-projection matrix reaches the GPU,
followed by the keystone proof: taking control of the world's camera. See the
dossier's status line and open-risks section.

## Scope, ethics, and legality

- This is a **non-commercial fan project**. It requires owning a legitimate
  copy of the game and **redistributes no original game assets** — only files
  we create. See [`.gitignore`](.gitignore).
- The techniques here (DLL proxying, hooking, injection, shader reflection)
  resemble malware only in tooling; the context is personal modding of a game
  we own.
- We **credit everyone** whose work or research this builds on, and we honour
  correction and removal requests from actual rights holders. See
  [`CREDITS.md`](CREDITS.md).

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
