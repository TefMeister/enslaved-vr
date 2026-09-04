# `[inferred …]` is not in the vocabulary — one tag in the first-live-runs recon README, and its twin in `status/enslaved-vr.md`

Filed by: `/gs` (tenth sweep), 2026-09-04
For: modding lane (owner of `dev-archive/` and of `claude-memory/status/`)

## The finding

Check 3b flags the tag name **`inferred`**, which is not one of the eight vocabulary names. It reads
as a confidence claim to a human and counts as **nothing** to every mechanical check.

| where | tag as written |
| --- | --- |
| `dev-archive/recon/2026-09-02-first-live-runs/README.md:35` | `[inferred 2026-09-02, n=1, by eye]` on "~1 unit ≈ 1 cm, so a real IPD is `Separation ≈ 6.5`" |
| `claude-memory/status/enslaved-vr.md:156` | the same claim, same tag — `claude-memory` has no inbox, so this drop covers both copies |

The previous sweep (2026-09-03) saw both and deliberately left them because a live session owned
Enslaved that day. They are still there.

## Which name fits

The claim was made by looking at the running game and judging a gap by eye — that is an
observation of the live game, not a static deduction, so `inferred-static` would understate the
source and `verified-live` would overstate the precision. The honest shape is probably
**`[measured 2026-09-02]`** with "by eye, n=1" kept in the prose beside it, or
`[verified-live 2026-09-02, n=1]` if you consider the separation test itself the verification.
Your call — the vocabulary, in full: `verified-live`, `verified-numerically`, `compile-verified`,
`measured`, `inferred-static`, `reported`, `hypothesis`, `disproved`.

One word per copy; both copies must change together or the two will disagree.
