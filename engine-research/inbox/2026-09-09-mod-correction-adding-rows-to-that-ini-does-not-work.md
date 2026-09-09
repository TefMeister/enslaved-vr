# CORRECTION: adding rows to that layout ini does NOT work — read it, don't write it

Supersedes: inbox/2026-09-09-mod-check-for-a-second-input-ini-holding-the-action-bindings.md

*Dropped by: `/lm alice-madness-returns-vr`, 2026-09-09b, a few hours after the file it corrects.
Create-only inbox file; the modding lane curates `engine-research/`.*

## What the earlier drop got wrong

It said, of Alice's `AliceControlLayout.ini`:

> **A key binding that names an engine command IS a command channel, with no console in the path.**
> If Enslaved ships an equivalent layout file, some of what the missing console was wanted for may
> be one rebind away.

**The second sentence is wrong, and it was never tested when it was written.** What had actually
been verified was one thing only: that pressing `T` — a binding that *shipped* on `T` — enters
Alice's first-person camera.

## What was measured since

Three unused commands were bound to three free keys in **both** copies of Alice's layout file, with
the game closed: `BugItForGameController`, `StatUnitAndStatFPS`, `ChangeCameraMode`. All three did
nothing, and the rows were still in the file afterwards, so the game had not rewritten it.

Two explanations fitted that equally — added rows ignored, or those three commands absent from the
retail build the way the console is — so the discriminator was run: **a command KNOWN to work was
put on a new key.** `G` was rebound to `EnterFPSByRS`, the exact command `T` carries:

```
before   : third-person
after G  : third-person      <- the command that works on T, on a new key
after T  : FIRST-PERSON      <- seconds later, same run
```

`[verified-live 2026-09-09, n=1 launch, alice-madness-returns-vr]`

**The game does not honour rows added to that file.** How it does load its layout is not
established `[hypothesis]` — profile cache, compiled defaults, or a fixed row count are all
consistent with what was seen.

## What still stands, and what it means for Enslaved

- **Reading every input-related ini is still worth doing, and is still the recommendation.** It is
  how Alice's first-person camera was found. The value is that such a file tells you **what the
  game can do** — a vocabulary of real engine commands and, sometimes, a shipped key that already
  invokes one.
- **What it does NOT give you is a way to invoke them.** Treat a name in that file as a lead about
  the build's capabilities, and look for a key the game **already ships** carrying it. That is the
  half that worked.
- So for Enslaved: still grep for the vocabulary, but **do not plan on rebinding.** If a wanted
  command has no shipped key, the routes left are the game's own controls UI (Alice exports
  `ExecRebindKey` / `ExecResetKeyBindings`, and its CONFIGURATION → CONTROLS screen clearly rebinds
  — untried), or the proxy.

## The general lesson, which is the reusable part

The project's own rule — *a binding surviving in a shipped ini is not evidence the feature is live*
— was applied correctly to the individual command names, and then quietly not applied one level up,
to the **mechanism**. "The file lists commands next to keys" was read as "the file is how commands
get bound to keys". The first is an observation; the second is a claim about who reads the file,
and nobody had checked.
