# 2026-09-09 — `ProcessEvent` located, and the UObject probe built

`/pd` session on the dev PC. **The game was not launched and nothing here was run
against it.** Everything in this folder came from reading `Enslaved.exe` on disk
and from a self-test that runs against synthetic memory.

| file | what it is |
| --- | --- |
| `find_processevent-output.txt` | full output of `dev-archive/tools/find_processevent.py --prologue`, the run that located `UObject::ProcessEvent` |
| `selftest-output.txt` | the 8 checks of the UObject probe self-test, all passing |
| `selftest-probe.log` | the probe's own log from the last self-test attempt, i.e. what its output looks like |

## The finding in one line

`UObject::ProcessEvent = 0x00580990` `[inferred-static 2026-09-09]`, bounds
`0x00580990..0x00580EFB` (1387 bytes), `ret 0Ch`.

## What is NOT established

That the address is really `ProcessEvent`. The static evidence converges hard
(see the note in `modding-notes/`), but confirmation is runtime-only. Nothing
here has been read with the game running.

## Reproducing

```
python dev-archive/tools/find_processevent.py --prologue
```

Read-only; it never writes to the game folder and extracts no game content.
