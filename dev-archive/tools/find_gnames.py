#!/usr/bin/env python3
"""find_gnames.py - locate UE3's `GNames` in Enslaved.exe by CODE PATTERN.

WHY BY PATTERN AND NOT BY NAME
  `GNames` has no string in this binary in either encoding [measured 2026-09-07],
  and a /gr sweep established that is the NORMAL case: no public UE3 locator
  searches for a `GNames` string or symbol. All six working locators found - six
  games, two independent codebases - scan for the same code shape: an absolute
  load of a global followed immediately by an INDEXED READ WITH SCALE 4, i.e. the
  engine asking "is name slot Index empty?".

  The published signature, identical across UT3, APB: Reloaded, Tribes: Ascend and
  Hawken in polivilas/UnrealEngineSDKGenerator [reported 2026-09-07]:

      8B 0D ?? ?? ?? ?? 83 3C 81 00 74      &GNames = DWORD at match+2
      mov ecx,[imm32] / cmp dword ptr [ecx+eax*4],0 / jz

  UT3 is close to stock UE3, so it is the most likely to transfer. If the exact
  bytes miss, this widens to the INVARIANT the six locators share rather than
  giving up: any absolute load into a register followed by a scale-4 indexed read.

WHAT THIS CAN AND CANNOT SETTLE
  It is a STATIC scan, so it can produce candidate ADDRESSES and rank them. It
  cannot validate one: the validator (read Data[0], require the name "None") is
  runtime-only, because FNameEntry objects are heap-allocated at startup from the
  compiled-in REGISTER_NAME table and are NOT in the exe on disk.

  So the honest output is a short, ranked candidate list for one live check - not
  an answer.

RANKING SIGNAL, from two published UE3 pairs [reported, n=2]
  Borderlands 1: GNames 0x01FB4DA8, GObjects 0x01FB4DD8  -> delta 0x30
  Rocket League: GNames 0x0246D6F0, GObjects 0x0246D738  -> delta 0x48
  In BOTH, GNames is LOWER and under 0x50 away. Our GObjObjects.Data is
  0x0242B984 [inferred-static 2026-09-07], so a candidate just below it is
  strongly favoured - but n=2 is thin, so proximity RANKS candidates, it never
  eliminates them.

Read-only. Never writes to the game folder.
"""
import argparse
import os
import struct
import sys

DEFAULT_EXE = (r"D:\Program Files (x86)\Steam\steamapps\common"
               r"\Enslaved\Binaries\Win32\Enslaved.exe")
GOBJOBJECTS_DATA = 0x0242B984          # confirmed 2026-09-07, cross-checked four ways


def read_pe(path):
    """Return (image_base, [sections]) where each section is a dict."""
    data = open(path, "rb").read()
    if data[:2] != b"MZ":
        sys.exit("not a PE: %s" % path)
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        sys.exit("no PE signature")
    coff = e_lfanew + 4
    nsections = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic != 0x10B:
        sys.exit("this scanner is for 32-bit PE only (magic 0x%X)" % magic)
    image_base = struct.unpack_from("<I", data, opt + 28)[0]

    secs = []
    off = opt + opt_size
    for i in range(nsections):
        s = off + i * 40
        name = data[s:s + 8].rstrip(b"\0").decode("latin-1")
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, s + 8)
        chars = struct.unpack_from("<I", data, s + 36)[0]
        secs.append({
            "name": name, "vaddr": vaddr, "vsize": vsize,
            "raddr": raddr, "rsize": rsize, "chars": chars,
            "exec": bool(chars & 0x20000000),
            "write": bool(chars & 0x80000000),
            "data": data[raddr:raddr + rsize],
        })
    return data, image_base, secs


def va_of(sec, image_base, off_in_sec):
    return image_base + sec["vaddr"] + off_in_sec


def in_writable(secs, image_base, va):
    for s in secs:
        lo = image_base + s["vaddr"]
        if lo <= va < lo + max(s["vsize"], s["rsize"]):
            return s["write"], s["name"]
    return False, None


def scan_exact(sec, image_base, secs):
    """The published signature: 8B 0D imm32 83 3C 81 00 74."""
    body, hits = sec["data"], []
    i = 0
    while True:
        i = body.find(b"\x8b\x0d", i)
        if i < 0 or i + 11 > len(body):
            break
        if body[i + 6:i + 10] == b"\x83\x3c\x81\x00" and body[i + 10] == 0x74:
            imm = struct.unpack_from("<I", body, i + 2)[0]
            hits.append((va_of(sec, image_base, i), imm, "exact"))
        i += 1
    return hits


# An absolute load into a register: opcode -> (length of prefix before imm32)
ABS_LOADS = {
    b"\xa1":      (1, "mov eax,[imm32]"),
    b"\x8b\x0d":  (2, "mov ecx,[imm32]"),
    b"\x8b\x15":  (2, "mov edx,[imm32]"),
    b"\x8b\x05":  (2, "mov eax,[imm32]"),
    b"\x8b\x1d":  (2, "mov ebx,[imm32]"),
    b"\x8b\x35":  (2, "mov esi,[imm32]"),
    b"\x8b\x3d":  (2, "mov edi,[imm32]"),
}


def has_scale4_index(body, j):
    """Is there a SIB-addressed read with scale 4 within a few bytes of j?

    The invariant the six public locators share is "absolute load, then an
    indexed read with scale 4". Rather than enumerate every encoding, this looks
    for a ModRM/SIB pair whose SIB scale bits are 0b10 (x4) in the next few
    bytes - deliberately loose, because this branch only RANKS candidates and a
    missed real one costs far more than an extra false one."""
    for k in range(j, min(j + 8, len(body) - 1)):
        modrm = body[k]
        if (modrm & 0xC7) != 0x04:          # mod=00, r/m=100 -> SIB follows
            continue
        sib = body[k + 1]
        if ((sib >> 6) & 3) == 2:           # scale = 4
            return True
    return False


def scan_wide(sec, image_base, secs):
    hits = []
    body = sec["data"]
    for pat, (plen, desc) in ABS_LOADS.items():
        i = 0
        while True:
            i = body.find(pat, i)
            if i < 0 or i + plen + 4 + 8 > len(body):
                break
            imm = struct.unpack_from("<I", body, i + plen)[0]
            w, _ = in_writable(secs, image_base, imm)
            if w and has_scale4_index(body, i + plen + 4):
                hits.append((va_of(sec, image_base, i), imm, desc))
            i += 1
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exe", nargs="?", default=DEFAULT_EXE)
    ap.add_argument("--near", type=lambda v: int(v, 0), default=GOBJOBJECTS_DATA,
                    help="rank candidates by distance below this VA")
    ap.add_argument("--window", type=lambda v: int(v, 0), default=0x400,
                    help="how far from --near still counts as adjacent")
    args = ap.parse_args()

    if not os.path.exists(args.exe):
        sys.exit("no such file: %s" % args.exe)

    _, base, secs = read_pe(args.exe)
    print("%s" % os.path.basename(args.exe))
    print("  image base 0x%08X, %d sections" % (base, len(secs)))
    for s in secs:
        print("    %-8s VA 0x%08X..0x%08X  %s%s"
              % (s["name"], base + s["vaddr"], base + s["vaddr"] + s["vsize"],
                 "X" if s["exec"] else "-", "W" if s["write"] else "-"))
    print()

    code = [s for s in secs if s["exec"]]
    exact, wide = [], []
    for s in code:
        exact += scan_exact(s, base, secs)
        wide += scan_wide(s, base, secs)

    print("EXACT published signature (8B 0D imm32 83 3C 81 00 74): %d hit(s)" % len(exact))
    for site, imm, _ in exact:
        w, sec = in_writable(secs, base, imm)
        print("   at 0x%08X -> &GNames = 0x%08X  (%s%s)"
              % (site, imm, sec or "outside any section", "" if w else ", NOT writable"))
    if not exact:
        print("   none. UT3's exact encoding does not appear here - expected if the")
        print("   compiler chose a different register or scheduled the compare apart.")
    print()

    # Collapse the wide hits by target address; one global is loaded many times.
    by_target = {}
    for site, imm, desc in wide:
        by_target.setdefault(imm, []).append((site, desc))

    near, window = args.near, args.window
    ranked = sorted(by_target.items(),
                    key=lambda kv: (abs(kv[0] - near) > window,      # adjacent first
                                    not (kv[0] < near),              # below first
                                    abs(kv[0] - near)))
    print("WIDENED invariant (absolute load + scale-4 indexed read), %d distinct target(s)."
          % len(by_target))
    print("Ranked by the published adjacency: GNames sits BELOW GObjects, under 0x50 away (n=2).")
    print()
    print("  %-12s %8s %6s  %s" % ("target", "delta", "sites", "note"))
    shown = 0
    for imm, sites in ranked:
        d = imm - near
        adjacent = abs(d) <= window
        if not adjacent and shown >= 12:
            continue
        w, sec = in_writable(secs, base, imm)
        note = sec or "?"
        if adjacent:
            note += "  <-- ADJACENT to GObjObjects"
        print("  0x%08X %+8d %6d  %s" % (imm, d, len(sites), note))
        shown += 1
    if len(ranked) > shown:
        print("  ... %d more, all outside the +-0x%X window" % (len(ranked) - shown, window))

    print()
    print("⚠️ THIS CANNOT CONFIRM ANY OF THEM. The validator is runtime-only: read")
    print("   Data[0], follow it, and require the name \"None\" - FNameEntry objects are")
    print("   heap-allocated at startup and are not in the exe on disk. What this")
    print("   produces is a ranked shortlist for ONE live check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
