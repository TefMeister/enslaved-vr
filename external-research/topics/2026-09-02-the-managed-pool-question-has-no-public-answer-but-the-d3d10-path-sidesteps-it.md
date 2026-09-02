# The `D3DPOOL_MANAGED` question has no public answer — but the compiled-in D3D10 path would sidestep it entirely

**Status:** 🆕 new · **Priority:** medium — it does not change the next launch (the stereo rock test),
but it reframes the submission-plumbing risk in §9 from "upgrade D3D9 to D3D9Ex and hope MANAGED is
never requested" to a choice between two routes, one of which has no such trap.

## 1. What this pass looked for and did not find

§9 hinges on whether UE3's D3D9 RHI ever creates a resource in `D3DPOOL_MANAGED` on this build,
because a D3D9Ex device rejects that pool. The dossier says it is not answerable statically and
queues one instrumented launch. This pass looked for a public statement of what UE3's D3D9 RHI does
and found **none** `[checked 2026-09-02]` — Epic's UE3 source was never public, the UDK
documentation does not describe pool choices, and the D3D9 wrapper communities (Special K, DXVK,
dgVoodoo2) document *their* handling of `MANAGED` rather than any engine's use of it. Special K's
wiki was not readable by automated fetch. **The instrumented launch stays the only way to know; do
not search this again.**

## 2. The route that has no such trap: the game ships a D3D10 renderer

Dossier §2 already records that the D3D10/D3D11 RHI code paths are compiled into `Enslaved.exe`
(`D3D10CreateDevice`, `ID3D11ShaderReflection`, DXGI swap-chain strings) behind
`AllowD3D10=False`, and calls flipping the ini "untested". Public sources say the same switch is
also exposed as a **`-d3d10` command-line argument** `[reported 2026-09-02, via a search summary of
PCGamingWiki — the page itself 403s automated fetch]`.

Why that matters for §9 specifically:

| | D3D9 route (current) | D3D10 route |
| --- | --- | --- |
| Camera injection | `SetVertexShaderConstantF(0, …, 4)` — one call, already built | constant **buffers** — the `ViewProjectionMatrix` lives in a cbuffer the RHI maps/updates; injection is the D3D11-style "patch the mapped buffer" problem the playbook's §3.5 warns about |
| Sharing a surface with the compositor | needs **D3D9Ex** (`CreateTexture(..., pSharedHandle)`), hence the MANAGED trap | native: a D3D10 texture with `D3D10_RESOURCE_MISC_SHARED` is a DXGI resource; D3D11 and OpenVR open it directly |
| Cross-API synchronisation | no keyed mutex on D3D9; event query + double buffering | keyed mutex exists on D3D10.1/D3D11; even plain shared resources are the documented DXGI case |
| Shader knowledge | 34,046 `CTAB` tables already mapped, stage-tagged | `RefShaderCache-PC-D3D-SM4.upk` exists on disk (the `nvstereo` byte search already read it); reflection would need `ID3D11ShaderReflection`-style parsing instead of `CTAB` |
| Risk | the untested Ex upgrade + MANAGED | an RHI path Ninja Theory shipped but the config default avoids — stability unknown |

So the trade is: keep the cheap, already-built camera injection and pay for the Ex upgrade at
submission time, or move the whole proxy to D3D10 and get sharing for free at the cost of a
cbuffer-based injection that has not been designed. **Neither is obviously right before the rock
test runs**; what this topic establishes is that the MANAGED trap is a property of one route, not
of the game.

## 3. The console

The dossier's §7 still says "first session in-game should just press Tilde". The one public thread
that would have answered whether the shipping build kept its console class (a GameFAQs "how do you
enable the command console?" thread) returns 403 to automated fetch, so the question remains a
live check, not a research one. `[unread 2026-09-02]`

## Concrete next steps

1. Nothing changes for the next launch — run the stereo rock test as planned.
2. On the *same* instrumented launch that answers MANAGED, also note whether the game accepts
   `-d3d10` at all (a separate launch, since it must not contaminate the stereo run) — that is the
   cheapest input to the route decision above.
3. If MANAGED is requested and the Ex upgrade turns into a resource-remapping project, the D3D10 route
   is the fallback to cost out, starting from the SM4 shader cache already on disk.

## Sources

- https://www.pcgamingwiki.com/wiki/Enslaved:_Odyssey_to_the_West — `-d3d10` argument (search summary only; 403 on fetch)
- https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dpool — `D3DPOOL_MANAGED` semantics
- https://learn.microsoft.com/en-us/windows/win32/direct3darticles/surface-sharing-between-windows-graphics-apis — the D3D9Ex/D3D10/D3D11 sharing matrix
- https://wiki.special-k.info/en/Compatibility/Issues — not readable by automated fetch this pass
- https://gamefaqs.gamespot.com/boards/736624-enslaved-odyssey-to-the-west/67692514 — console thread, 403
