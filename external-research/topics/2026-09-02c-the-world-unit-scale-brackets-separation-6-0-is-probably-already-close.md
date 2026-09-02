# The world-unit scale brackets the separation: `6.0` is probably already about right, not ten times too small

**Status:** 🆕 new · **Priority:** high — it targets the board's live `[FLAT]` item *"retune
`Separation` — 6.0 reads as 'a very quick left-right teleport, not a big gap'; raise 10× and check it
scales linearly, the world-unit scale is still a guess."*

## The scale is not a guess any more — it is a two-value bracket

Unreal Engine 3's documented convention `[reported 2026-09-02]`:

| Source | Figure |
| --- | --- |
| UDK documentation and the UE3 modelling community | **1 Unreal Unit = 2 cm** — a 96-UU character is ~192 cm |
| Common licensee practice, noted in the same discussions | **1 UU = 1 cm** ("most licensees use 1 UU to 1 cm") |
| Gears of War (a UE3 licensee that differs again) | ~2 UU per inch — a 156-UU Marcus |

Epic's own guidance is not to vary the scale by more than a factor of two, so **1–2 cm per unit is
the real bracket** for a UE3 title, and which end Enslaved sits at is a per-title question.

## What that says about `Separation = 6.0`

A human interpupillary distance is about **6.4 cm**. So the value already in the ini is:

| if the scale is | `Separation = 6.0` means | verdict |
| --- | --- | --- |
| 1 UU = 1 cm | **6 cm** | ≈ one IPD — **correct** |
| 1 UU = 2 cm | **12 cm** | ~2 IPD — already wide |

Either way `6.0` is in the right order of magnitude, and **the reported symptom fits that**: "a very
quick left-right teleport, not a big gap between images" is what a correct-magnitude separation looks
like when the two eyes are shown *alternately on one flat screen* rather than one per eye. A frame
sequence at IPD spacing should read as a small hop. It is not evidence the number is too small.

**Raising it 10× (to 60–120 cm) would put the eyes a metre apart** — the world would look like a
tabletop model. That is still worth doing **as a linearity diagnostic** (does the hop scale
proportionally? does anything break?), which is what the board actually asks for — but it should not
be read as a search for the right value, and the setting should come back down afterwards.

## How to settle which end of the bracket this game uses, cheaply

The game ships its camera configuration as plain text: `MonkeyGame\Config\MonkeyChaseCamera.ini` and
`DefaultChaseCamera.ini` carry the chase camera's distances and offsets in world units, and
`MonkeyEngine.ini` carries `FOVAngle` `[reported 2026-09-02]`. A third-person camera sits a
knowable real-world distance behind a character — read the configured distance, judge it against how
far the camera plainly is on screen, and the scale falls out to within the factor of two. No launch
needed to *read* it; one glance at a running frame to judge it.

## Two adjacent config facts worth having

- **`useAutoTiltup` in the chase-camera ini can be turned off.** `[reported]` An automatic camera
  tilt is a comfort hazard in a headset — the camera moves without the player asking — and this is
  the same class of find as Alan Wake's `-rigidcamera`: the game ships the off-switch.
- **FOV is reachable as an exec command bound in `MonkeyInput.ini`** under `[MonkeyGame.MKInput]`
  (`Bindings=(Name="F1",Command="FOV 0")`), and community FOV tweaks report it working. `[reported]`
  That matters beyond FOV: it means **exec commands reach this build through a key binding even if
  the console class is stripped** — a usable command channel for §7's open question, without needing
  the tilde console at all.

## Sources

- https://docs.unrealengine.com/udk/Three/UnrealUnits.html (403 to automated fetch; the 1 UU = 2 cm figure and the 96-UU example are quoted consistently across the discussions below)
- https://polycount.com/discussion/74537/udk-player-scale · https://polycount.com/discussion/95513/confused-about-udk-units-and-scale — the 2 cm figure, the "most licensees use 1 cm" note, and the Gears of War exception
- https://steamcommunity.com/app/245280/discussions/0/487877107141205916/ — `FOVAngle` in `MonkeyEngine.ini` and `FOV` bindings in `MonkeyInput.ini`
- https://steamcommunity.com/app/245280/discussions/0/3829691612498924840/ — `MonkeyChaseCamera.ini` / `DefaultChaseCamera.ini` and `useAutoTiltup`
