# 2026-09-07 — `GObjObjects` is located to the byte, and the pause menu is unreachable on the dev PC

*Session: `/lm enslaved`, dev PC, ONE FLAT LAUNCH, fully autonomous after the launch (Tefa at work).
Game closed through `WM_CLOSE` — **not** the profile's graceful menu route, because that route needs
the pause menu and the pause menu could not be opened. See §2.*

Headline: **the `[PD]` route-(B) row is essentially closed**, and the ⭐ `[FLAT]` reset row is
**blocked by a newly discovered input regression** that also puts a question mark over the build it
was going to test.

---

## 1. ✅ `GObjObjects` — located, and cross-checked three ways `[inferred-static 2026-09-07]`

The `/gr` drop of 2026-09-05 was right on every count, and its method worked exactly as described.
`DO_CHECK` is on in this retail build, so `check()` leaves the stringified expression in `.rdata`,
and `appFailAssert` is called from *inside* the function that tests the global — which puts the
global in the preceding instructions as a **direct memory operand**.

```
UObject::GObjObjects    .Data     = 0x0242B984
                        .ArrayNum = 0x0242B988
                        .ArrayMax = 0x0242B98C

UObject::GObjAvailable  .Data     = 0x0242B990
                        .ArrayNum = 0x0242B994
                        .ArrayMax = 0x0242B998

appFailAssert                     = 0x0058E580
ImageBase                         = 0x00400000   (.text 0x00401000, .data 0x02312000)
```

**Three different assertion expressions, in three different functions, all landing on the same
array** — the row asked for two cross-checks:

| assertion string | site | the code that proves it |
| --- | --- | --- |
| `GObjObjects.Num() == 0` | `0x005BC4F7` | `cmp dword ptr [0x242B988], 0` — literally `Num() == 0` |
| `GObjObjects(InIndex)==NULL` | `0x005B187F` | `mov eax,[0x242B984]` then `cmp dword ptr [eax+edi*4], 0` — loads `.Data`, indexes it |
| `GObjObjects.IsValidIndex(CurObjectIndex)` | `0x005CAAFD` | `mov eax,[0x242B988]` used as the bound |

**And a fourth, independent corroboration nobody asked for:** `GObjAvailable.Num()` resolves to
`0x0242B994`, which is **exactly 12 bytes** — `sizeof(TArray)` on 32-bit — after `GObjObjects`. UE3
declares those two statics consecutively and the linker laid them out consecutively. Two separate
`TArray`s each showing `ArrayNum` at `Data+4` also confirms the struct layout itself.

### Free extras

- **`__FILE__` beside the assertion gives Ninja Theory's build path**:
  `e:\projects\congo\enslavedmaster\masterarchives\unrealengine3\development\src\core\inc\Array.h`.
  "congo" appears to be their internal codename. Reusable for every later hunt in this binary.
- The 7th `GObjObjects` occurrence is not an assertion at all but a **decorated MSVC symbol**,
  `?GObjObjects@UObject@@0V?$TArray@PAVUObject@@VFDefaultAllocator@@@@A` at `0x021C09BC` —
  i.e. `private: static TArray<UObject*, FDefaultAllocator> UObject::GObjObjects`. Not yet chased.

### ⚠️ What is NOT found, and a tool defect worth recording

- **`GNames` has no string in the binary in EITHER encoding** `[measured 2026-09-07]`. The
  assertion-string route does not reach it; it needs a different locator.
- **`AddCheats`, `ToggleDebugCamera`, `AllowCheats`: absent from the exe in both encodings.** As the
  board already predicted, they are script-side, in the compressed `.u` packages.
- **My scanner was ASCII-only at first and wrongly reported `ProcessEvent` absent.** The 2026-09-04
  census was right: `ProcessEvent` is there as **1 ASCII + 2 UTF-16**, and `CheatManager` ×3 /
  `ConsoleCommand` ×4 are **UTF-16 only**. UE3's `TCHAR` is `wchar_t`, so engine *names* are wide
  while the assertion strings are narrow. Anything scanning this binary must do both.
  `find_uobject_globals.py` is committed with that limitation documented in its header.

---

## 2. ⛔️ THE PAUSE MENU CANNOT BE OPENED ON THE DEV PC — and that blocks the ⭐ reset row

Every route was tried. The game was live and driveable throughout.

| route | result |
| --- | --- |
| keyboard `W` / `S` movement | **WORKS** — Monkey walks; verified by eye across four captures |
| `Escape` (profile's documented pause route) | **nothing**, at 90 ms and at 300 ms hold, twice, in two different spots |
| `F4` → `DoPause` (added to `[Engine.PlayerInput]`) | nothing |
| `F2` → `Pause`, `F1` → `FOV 0`, `F3` → `Pause` | nothing |
| `F8` → `stat fps` (shipped binding) | no overlay |
| `F12` → `FreezeRendering` (shipped binding) | render never froze — no identical frame pair |
| **virtual X360 pad, `START`** | game showed a **"Controller Connected — Xbox 360 controller"** toast, so it *enumerated* — but no pause menu |
| **virtual pad, `thumbLX=29490`** (the exact value 2026-09-03d used to verify the pad on the home PC) | **Monkey did not move at all** |

So: **keyboard movement reaches the game; nothing else does, and the virtual pad connects but does
not drive.** With no pause menu there is no `RESTART FROM LAST CHECKPOINT`, no `OPTIONS`, and no way
back to the main menu — which is why this session closed with `WM_CLOSE` instead of the profile's
graceful route.

### ⚠️ This CONTRADICTS the record, on the same machine

`ai-game-control-profiles/profiles/enslaved.json` carries `gameplay -> main_menu` as
**`verified-live 2026-09-03`** with `Escape` as step 1, and 2026-09-03/03b/03c were **dev PC**
sessions. Today, on the dev PC, Escape does nothing. One of the two observations is wrong, or
something changed between them.

**Two candidate causes, neither tested, both cheap to test:**

1. **My ini edit today.** I added `F4`/`F2` to `[Engine.PlayerInput]` and *created* a
   `[MonkeyGame.MKInput]` section. **Reverted at end of session** — the stock file is restored and
   today's version is kept beside it as `MonkeyInput.ini.claude-pausetest-2026-09-07`.
2. **⭐ The 2026-09-04 self-healing proxy build, which had NEVER BEEN RUN BEFORE TODAY.** The
   deployed `d3d9.dll` is dated **Sep 4 13:55** and the 2026-09-04 session was `/pd`, static only,
   no launch. It hooks two device methods the earlier builds did not (`BeginStateBlock`,
   `EndStateBlock`) and re-patches five vtable slots every `Present`
   (`[hook] … self-heal Rearm=1`). Today is its first live run, and today input is broken.

**This matters beyond the inconvenience.** That build exists *specifically* to answer the reset row.
If it is what broke input, then it cannot be trusted to answer anything until that is settled — and
the reset row's whole reading table is written against its log output.

### The decision tree for the next launch (two relaunches at most)

1. Relaunch **as it stands now** (stock ini restored, 2026-09-04 proxy). Press `Escape`.
   - **Pauses** ⇒ my ini edit caused it. Cause closed; reinstate the test file if the bindings are
     still wanted, and the reset row proceeds normally.
   - **Does not pause** ⇒ the ini is exonerated; go to 2.
2. Swap `d3d9.dll` for `d3d9.dll.bak-2026-09-04-pre-rearm` (73,728 B, the pre-self-heal build) and
   relaunch. Press `Escape`.
   - **Pauses** ⇒ **the 2026-09-04 self-healing build breaks input.** Regression; the reset row is
     blocked behind fixing it, and every claim that build was going to produce is void until then.
   - **Does not pause** ⇒ neither candidate; the change is elsewhere (driver, Windows, game update)
     and the 2026-09-03 route claim needs re-examining on its own terms.

---

## 3. ⭐ `[Engine.PlayerInput]` IN THIS BUILD IS GAMEPAD-ONLY — which reframes two sessions of results

Dumping every `Bindings=` line in that section: it contains **the action aliases** (`DoJump`,
`DoPause`, `MoveForward`, …) and **`XboxTypeS_*` gamepad bindings**, and **not one keyboard key**
`[measured 2026-09-07]`. `DoPause` is reachable from exactly one place: `XboxTypeS_Start`.

Yet `W` walks Monkey. So **keyboard movement is not coming from this ini at all** — it comes from
engine-level defaults elsewhere.

**The implication for the exec question is uncomfortable and should not be glossed:** the F-key
bindings that 2026-09-03 added, and the ones added today, were inserted into a section that this
build appears to populate **only** with gamepad entries. "The exec command did not fire" and "a
keyboard binding added to a gamepad-only section is inert" produce *identical* observations. That is
a cheaper explanation than "exec dispatch is stripped", and it means the exec question is **still**
`[hypothesis]` — the 2026-09-04 downgrade was right, and today did not lift it.

Also: **`Escape` is bound only in `[NTGameFramework.NTCam_DebugInput]`**, the class 2026-09-04 proved
is dead (`CloseEditorViewport | DoPause`, line 171). So Escape *should never have* paused the game
by way of a binding — if it did on 2026-09-03, that pause came from native handling, not config.

**`[MonkeyGame.MKInput]` does not exist in this build's shipped ini** `[measured 2026-09-07]`. The
board's row said to bind there; I created the section to test the community report properly. Nothing
in it fired — though given §3 that is not yet a verdict on the section name.

---

## 4. ❌ `ALT+ENTER` and window resizing do NOT cause a device Reset `[disproved 2026-09-07]`

Tried as a way to reach the reset row without menus. Both are absorbed:

- `ALT+ENTER` — the game *did* respond (it reverted the window to its own style `0x94080000`, client
  1286x749) and the proxy restyled it back at `present#8700`. **No `[reset]` line.**
- External `SetWindowPos` to 1024x576 and 1600x900 — the proxy forced 1280x720 back each time
  (`present#69300`, `#69600`). **No `[reset]` line.**

The reason is in the proxy's own design note: the backbuffer stays 1920x1080 and D3D stretches it
into the window, so resizing the window never invalidates the device. **A Reset on this game
genuinely requires the in-game options resolution change or a checkpoint restart** — both behind the
pause menu.

---

## 5. Stereo was healthy for the whole session, and never reset

290 `[stereo]` summaries, `offset` 2338–2824 per window throughout, `ortho-skipped` 164–1440,
`slot94=ours` on every line, `re-arms 0, state blocks 0`, and **zero** `[reset]` / `[stateblock]` /
`[rearm]` lines across 10,901 log lines. Four `[liveness]` stamps, all with `last Reset at frame -1`
(i.e. no reset had occurred). The proxy behaved perfectly; it simply never got the event it was
built to observe.

---

## 6. ⚠️ Method note: whole-frame luma diff is worse than useless while wiggle is on

The proxy runs `Mode=0` (alternate eyes each frame). Alternate captures are therefore *different
eyes*, and differ by **~27.5 mean luma** — which swamps everything else and is stable enough to look
like a signal. I read `27.58 / 0.00 / 27.58 / 0.00` after one keypress and briefly took it for a
pause (a static scene renders exactly two images, so same-eye pairs are byte-identical). **It was
Monkey standing still against a wall.** Looking at the frame settled it in one step.

The profile already carried "whole-frame mean-luma difference is too blunt to score input routes in
this game". It is blunter still with wiggle enabled: **set `Mode=1` or `Mode=2` in `d3d9_proxy.ini`
before any run that judges anything by image comparison.**

---

## Automation (§5a), scored by name

1. **Menu → gameplay ✅** — title → CONTINUE JOURNEY → Chapter 1, driven cold and unassisted.
2. **Commands ✗** — no exec route works; see §2 and §3. Unchanged from the last two sessions and now
   with a cheaper competing explanation.
3. **Character movement ✅ / camera ✗** — `W`/`S` walk Monkey. Camera not exercised (mouse support is
   in the new harness but untested; the pad that would normally turn the camera does not drive).
4. **Self-close — PARTIAL.** `WM_CLOSE` worked (window gone in 2 s, proxy logged its summary), but
   the profile's graceful `main_menu -> process_exit` route was **unreachable** for the first time.

**New tool:** `dev-archive/tools/enslaved_harness.py` — no harness survived the 2026-09-02/03
sessions, only their outputs, so this is a rebuild and it is committed. BitBlt not `PrintWindow`,
scancodes with the extended flag, relative-mouse support, and burst/diff helpers.

---

## 7. ⚠️ Cross-project: `MonkeyGame` is THIS game's config tree, not Alice's

Recorded here because it was found here and it corrects an Alice claim.
`Documents\My Games\UnrealEngine3\MonkeyGame\` belongs to **Enslaved** — "Monkey" is Ninja Theory's
codename, and the tree's `MonkeyEngine.ini` carries `EditPackages=NTEngine`,
`EditPackages=NTGameFramework` and `EditPackagesOutPath=..\..\MonkeyGame\Script`, with **zero**
Alice references `[verified-numerically 2026-09-07]`.

Alice's 2026-09-05 board row claims "UE3 names it after the script package, which is `Monkey`", and
on that basis a home-PC `/pd` session set `Fullscreen=False` in `MonkeyEngine.ini` believing it was
configuring Alice. **On the home PC that edited Enslaved's engine ini.** Harmless for Enslaved (this
build ignores `[SystemSettings] Fullscreen`, and our proxy forces windowed regardless) — but Alice
never received its windowed fix there, and the home PC has a file edited under a false belief. The
correction is filed on the Alice side too.
