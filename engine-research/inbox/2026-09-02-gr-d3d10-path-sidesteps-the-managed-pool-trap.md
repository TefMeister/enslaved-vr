# §9: the `D3DPOOL_MANAGED` trap belongs to the D3D9Ex route, not to the game — the shipped D3D10 RHI has native DXGI sharing

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02-the-managed-pool-question-has-no-public-answer-but-the-d3d10-path-sidesteps-it.md`
Dossier sections: §2 (D3D10 path "untested"), §9 (D3D9 + modern VR runtimes)

- **No public source states whether UE3's D3D9 RHI requests `D3DPOOL_MANAGED`** `[checked 2026-09-02]`. The instrumented launch stays the only answer; suggest §9 says so explicitly so it is not researched again.
- **`-d3d10` is a public launch argument for this game** `[reported 2026-09-02, search summary of PCGamingWiki; page 403s]`, the same switch as `AllowD3D10`. On that RHI a shared texture is a DXGI resource (`D3D10_RESOURCE_MISC_SHARED`), keyed mutexes exist, and no Ex upgrade is needed — at the cost of re-doing the camera injection as a constant-buffer patch (the playbook §3.5 case) instead of `SetVertexShaderConstantF(0,…,4)`, with the SM4 shader cache on disk as the reflection source.
- Suggested §9 wording: two routes — (a) D3D9 + Ex upgrade, blocked on the MANAGED check; (b) D3D10, blocked on nothing known but with an undesigned cbuffer injection. Decide after the rock test, and check `-d3d10` on a separate launch so the stereo run stays clean.
