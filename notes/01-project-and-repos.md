# 01 — Project setup and repositories

**Session 1, 2026-08-21.**

Set up the standard five-repository layout for a new game VR project, plus
local backup clones.

## Repositories (all under the account, suffix-unified)

| Repo | Visibility | Purpose |
|---|---|---|
| `enslaved-vr-mod` | public | the released mod — releases only |
| `enslaved-vr-dev-archive` | public | this repo — messy in-progress history |
| `enslaved-vr-modding-notes` | public | readable field notes / progress ledger |
| `enslaved-vr-staging` | private | unverified session work / cross-machine handoff |
| `enslaved-vr-engine-research` | public | distilled engine dossier + reusable VR playbook |

Local backup clones are kept under the standard `github-backups` folder.

The engine-research repo received the engine-agnostic `PLAYBOOK.md` (copied
into every project) and a new Enslaved-specific `ENGINE-DOSSIER.md`.

## North Star

Per the playbook: the one milestone that decides everything is the game
rendering in a headset with head tracking. The critical path is
foothold → engine model → own the camera → stereo → VR + head tracking, and
the keystone is proving we can own the world camera transform.
