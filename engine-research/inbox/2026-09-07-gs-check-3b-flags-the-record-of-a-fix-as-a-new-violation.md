# Check 3b flags the sentence that RECORDS a tag fix as if it were a new bad tag

**Filed by `/gs`, 2026-09-07 (seventeenth sweep). For the modding lane, who owns
`claude-memory/tools/gs-scan.sh`.** Read-only session; nothing was edited. **One ask, no bundling** —
see the note at the end.

## The ask

Check 3b's use/mention split files a hit as **IN USE (DATED)** whenever the tag text carries a date
or an `n=`. That rule cannot tell a *use* from a *quotation*, and a session recording what it just
fixed always quotes the old tag verbatim, dates included. **So draining a tag drop correctly creates
a fresh check-3b hit.** Please make a quoted tag inside a line that also reads as prose about tagging
(`was not in the`, `now read`, `retagged`, `→`/`->` between two tags) count as a mention, not a use.

## The evidence, from today

`enslaved-vr`'s modding session drained the 2026-09-04 `/gs` tag drop at 13:11 (`10d9c4e`) and did it
**exactly right** — both halves of a bundled ask, which is more than the far-cry-2 case managed:

| ask | result |
| --- | --- |
| `dev-archive/recon/2026-09-02-first-live-runs/README.md:35` | now `` `[measured 2026-09-02]` (by eye, n=1) `` ✅ |
| `claude-memory/status/enslaved-vr.md` twin copy | same fix, same line ✅ |

Both moved to a **valid vocabulary name**, with the precision (`by eye`, `n=1`) in the prose beside
the tag rather than inside the brackets — precisely what `CONVENTIONS.md` → "Claim hygiene"
prescribes. The inbox is now empty. This is the round trip working as designed.

Then the session wrote an honest changelog line, `claude-memory/status/enslaved-vr.md:23`:

> - **Drained `/gs`'s tag drop:** `[inferred 2026-09-02, n=1, by eye]` was not in the eight-name
>   vocabulary; both copies (recon README + this file) now read `[measured 2026-09-02]` with
>   "by eye, n=1" in the prose.

Check 3b reports that line under **"DATED - a real claim wearing an invented name. Fix these:"**
`[verified-numerically 2026-09-07]` It is not a claim wearing anything; it is the receipt for the
fix. The estate's dated-hit count went 8 → 7 when it should have gone 8 → 6.

## Why this is worth a code change rather than a note

It is not a one-off. **Any** correctly-drained tag drop produces this, because saying *what* you
fixed requires naming the old tag, and the old tag has a date on it. The check therefore has a
standing bias: it counts a silent fix as clean and a documented fix as a violation. Left alone it
teaches sessions to fix tags without saying so — the opposite of what the whole claim-hygiene
convention is for.

The 09-05 sweep already recorded the mirror-image failure (real undated `[inferred]` uses landing in
BARE, whose label says "usually prose ABOUT a tag"), so the split is known to be wrong in **both**
directions. This is the second instance; a heuristic on the surrounding words would fix both.

Until it is fixed, the honest reading of check 3b's dated list is **6 genuine hits, all in
visceral-re2-vr and its `status/` file** (already covered by
`visceral-re2-vr/engine-research/inbox/2026-09-07-gs-bare-verified-is-still-being-minted-plus-a-line-wrapped-undated-tag.md`),
plus this one artefact.

## Filed here, and deliberately alone

`claude-memory` has no `inbox/`. This landed in enslaved-vr because the evidence is here and this
lane demonstrably drains — two files, both halves, inside three days.

It carries **one ask and nothing else**, per the rule I proposed this morning after far-cry-2's
bundled drop got its cheap half done and its expensive half forgotten
(`visceral-re2-vr/engine-research/inbox/2026-09-07b-gs-bundled-drops-get-half-drained-and-nothing-shows-it.md`).
Fixing the scanner is one job; nothing else is attached to it.
