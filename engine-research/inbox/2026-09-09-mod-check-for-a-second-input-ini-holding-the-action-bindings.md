# Check whether Enslaved ships a SECOND input ini holding its action bindings

*Dropped by: `/lm alice-madness-returns-vr`, 2026-09-09. Create-only inbox file; the modding lane
curates `engine-research/`. This is a lead for a sibling UE3 project, not a finding about Enslaved.*

## What happened on the other UE3 title

Alice: Madness Returns turned out to ship a **working first-person camera**, reachable with one
keypress in the retail build — no mod, no rebind, no console. `[verified-live 2026-09-09, n=1
launch, alice-madness-returns-vr]`

It was found in `AliceGame\Config\AliceControlLayout.ini`:

```
KeyBindArray1=(Name="T",Command="EnterFPSByRS | OnRelease ToggleCloseFollowCamera")
KeyBindArray1=(Name="XboxTypeS_RightThumbstick",Command="ToggleGhost | OnRelease ToggleCloseFollowCamera |EnterFPS")
```

That project had read `AliceInput.ini` several times across four sessions and had **never opened
`AliceControlLayout.ini`**. The split matters: `AliceInput.ini` held only axes and aliases, while
the *action* bindings — first-person camera, camera mode, ghost mode, a `BugIt` variant, stat
overlays — all lived in the second file. The action's primary home was the pad's right-stick click,
which is why keyboard probing had never stumbled on it.

## Why it is worth ten minutes here

Enslaved is UE3, and this project's dossier already records the matching pair of facts: **the
console is stripped from the shipped build, and console bindings survive in the ini anyway.** That
is the same shape Alice was in the day before this was found — a correct "no console" conclusion
being read as "no command channel".

**A key binding that names an engine command IS a command channel, with no console in the path.**
If Enslaved ships an equivalent layout file, some of what the missing console was wanted for may be
one rebind away.

## The concrete check (static, no launch)

Under both `Documents\My Games\UnrealEngine3\MonkeyGame\Config\` and the game-folder template tree,
list every file matching `*Input*`, `*Control*`, `*Layout*`, `*Bind*`, `*Key*` — then grep the whole
set for the vocabulary rather than for key names:

```
FPS | FirstPerson | Camera | Debug | Toggle | BugIt | Stat | Ghost | Physics | Freeze
```

⚠️ Two things this drop does **not** claim:

- **Nothing about Enslaved has been checked.** This is a lead from a sibling project. Whether
  Enslaved splits its bindings the same way is unknown. `[hypothesis]`
- **A binding in a shipped ini is not evidence the feature is live** — this project's own rule, and
  Enslaved is the game that established it. Alice's `T` bind was *run*; everything else in that
  file, on both games, stays a lead until pressed.
