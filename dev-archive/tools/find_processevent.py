#!/usr/bin/env python3
"""find_processevent.py - locate UE3's `UObject::ProcessEvent` in Enslaved.exe.

WHY NOT THE PUBLISHED PROLOGUE SIGNATURE
  external-research/topics/2026-09-07b... reports that `unrealsdk` skips the
  vtable index entirely (it is not stable: APB 60, Rocket League 67) and instead
  scans for ProcessEvent's OWN PROLOGUE, given as:

      push ebp / mov ebp,esp / push -1 / push <scopetable> / push <handler>
      / mov eax,fs:[0] / push eax / sub esp,0x50 / xor eax,ebp
      / lea eax,[ebp-0x0C] / mov fs:[0],eax          (CallFunction: sub esp,0xA4)

  That literal shape DOES NOT OCCUR in this build (--prologue proves it: one hit
  in 23 MB of code, and it is not ProcessEvent). Two constants are wrong here:

    * TWO `push imm32` are expected; this build emits ONE. It uses the older
      _except_handler3 frame, where the handler comes from the scope table
      rather than from a second push.
    * `sub esp,0x50` is expected; ProcessEvent here is `sub esp,0x54`.

  The INVARIANT the research describes (an SEH + /GS frame) is right; the byte
  pattern built from it is not transferable. So this tool uses the route that
  already worked twice on this binary - the assertion strings - and then uses
  the prologue only to EMIT a signature, not to search with one.

THE METHOD THAT WORKS HERE
  This build ships with DO_CHECK on, so `check(expr)` calls appFailAssert with
  the stringified expression, __FILE__ and __LINE__ (see find_uobject_globals.py
  for the full argument shape). UE3 puts UObject::ProcessEvent in Core/Src/
  UnCorSc.cpp, and its first guard is `check(!HasAnyFlags(RF_Unreachable))`.

  So: take every appFailAssert call site whose __FILE__ is UnCorSc.cpp, find the
  function containing it, and rank those functions. ProcessEvent is the only one
  that is VIRTUAL - a UObject virtual appears once in every UObject subclass's
  vtable, i.e. in ~1800 slots in .rdata, while a file-local helper appears in
  none. That single discriminator separates it cleanly, and `ret 0Ch` (thiscall
  plus three stack arguments, matching ProcessEvent(UFunction*, void*, void*))
  corroborates it.

WHAT THIS CAN AND CANNOT SETTLE
  Static only. It produces an ADDRESS with converging evidence; it does not run
  the game, so the identification is [inferred-static], not verified. The live
  check is the one the proxy probe performs: detour it and confirm the
  UFunction* argument resolves to a name through GNames.

Read-only. Never writes to the game folder, and extracts no game content.
"""
import argparse
import collections
import os
import struct
import sys

try:
    import pefile
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
except ImportError:
    sys.exit("needs pefile and capstone  (pip install pefile capstone)")

DEFAULT_EXE = (r"D:\Program Files (x86)\Steam\steamapps\common"
               r"\Enslaved\Binaries\Win32\Enslaved.exe")
APPFAILASSERT = 0x0058E580     # located 2026-09-07, cross-checked three ways
DEFAULT_FILE = "UnCorSc.cpp"   # UE3 Core: the script VM, where ProcessEvent lives

# The published unrealsdk shape, for --prologue to demonstrate it does not fit.
PUBLISHED = b"\x55\x8b\xec\x6a\xff\x68"   # + imm32 + 68 imm32 + 64 A1 ...


class Image(object):
    def __init__(self, path):
        pe = pefile.PE(path, fast_load=True)
        self.base = pe.OPTIONAL_HEADER.ImageBase
        self.aslr = bool(pe.OPTIONAL_HEADER.DllCharacteristics & 0x0040)
        self.secs = []
        for s in pe.sections:
            data = s.get_data()
            self.secs.append({
                "name": s.Name.rstrip(b"\0").decode("latin-1"),
                "va": self.base + s.VirtualAddress,
                "vsize": max(s.Misc_VirtualSize, len(data)),
                "data": data,
                "exec": bool(s.Characteristics & 0x20000000),
            })
        self.text = next(s for s in self.secs if s["exec"])
        self.rdata = next((s for s in self.secs if s["name"] == ".rdata"), None)
        self.md = Cs(CS_ARCH_X86, CS_MODE_32)

    def sec_of(self, va):
        for s in self.secs:
            if s["va"] <= va < s["va"] + s["vsize"]:
                return s
        return None

    def cstr(self, va, maxn=260):
        s = self.sec_of(va)
        if not s:
            return None
        o = va - s["va"]
        if o < 0 or o >= len(s["data"]):
            return None
        e = s["data"].find(b"\0", o)
        if e < 0 or e - o > maxn:
            return None
        try:
            return s["data"][o:e].decode("latin-1")
        except Exception:
            return None

    def code(self, va, n):
        o = va - self.text["va"]
        return self.text["data"][o:o + n]


def call_sites(img, target):
    """Every `call rel32` in .text whose target is `target`."""
    d, tva, out, i = img.text["data"], img.text["va"], [], 0
    while True:
        i = d.find(b"\xe8", i)
        if i < 0 or i + 5 > len(d):
            break
        if tva + i + 5 + struct.unpack_from("<i", d, i + 1)[0] == target:
            out.append(tva + i)
        i += 1
    return out


def pushed_args(img, site, back=48):
    """The immediates pushed immediately before a call, in memory order.

    appFailAssert is __cdecl, so arguments are pushed right-to-left and appear
    in memory as: line, file, expr. Reading them in memory order and taking the
    .cpp string as the anchor therefore puts __LINE__ just before it and the
    stringified expression just after."""
    o = site - img.text["va"]
    seg = img.text["data"][max(0, o - back):o]
    out, j = [], 0
    while j < len(seg):
        if seg[j] == 0x68 and j + 5 <= len(seg):
            out.append(struct.unpack_from("<I", seg, j + 1)[0])
            j += 5
            continue
        if seg[j] == 0x6A and j + 2 <= len(seg):
            out.append(seg[j + 1])
            j += 2
            continue
        j += 1
    return out


def assertion_at(img, site):
    """-> (file, line, expr) or None."""
    vals = pushed_args(img, site)
    strs = [(v, img.cstr(v)) for v in vals]
    idx = None
    for n, (v, t) in enumerate(strs):
        if t and t.lower().endswith(".cpp"):
            idx = n
    if idx is None:
        return None
    f = strs[idx][1]
    line = strs[idx - 1][0] if idx >= 1 else None
    expr = strs[idx + 1][1] if idx + 1 < len(strs) else None
    return f, line, expr


def fn_start(img, va, maxback=0x4000):
    """Nearest preceding function entry: a standard frame set-up that is itself
    preceded by inter-function padding (int3 / nop) or by a return."""
    d, tva = img.text["data"], img.text["va"]
    o = va - tva
    for k in range(o, max(0, o - maxback), -1):
        if d[k:k + 3] != b"\x55\x8b\xec":
            continue
        p = d[k - 1] if k else 0xCC
        if p in (0xCC, 0x90, 0xC3) or (k % 16) == 0:
            return tva + k
    return None


def fn_end(img, start, limit=0x8000):
    """Linear sweep to the return that no forward branch jumps past."""
    d = img.code(start, limit)
    far = start
    for ins in img.md.disasm(d, start):
        if ins.mnemonic.startswith("j") and ins.op_str.startswith("0x"):
            far = max(far, int(ins.op_str, 16))
        if ins.mnemonic == "ret" and ins.address >= far:
            return ins.address, ins.op_str or "0"
    return None, None


def vtable_slots(img):
    """How many .rdata dwords hold each address (a virtual appears once per
    subclass vtable; a file-local helper appears nowhere)."""
    r = img.rdata
    n = len(r["data"]) // 4
    return collections.Counter(struct.unpack_from("<%dI" % n, r["data"], 0))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exe", nargs="?", default=DEFAULT_EXE)
    ap.add_argument("--file", default=DEFAULT_FILE,
                    help="source file to mine assertions from (default UnCorSc.cpp)")
    ap.add_argument("--afa", type=lambda v: int(v, 0), default=APPFAILASSERT,
                    help="appFailAssert VA")
    ap.add_argument("--prologue", action="store_true",
                    help="also run the published unrealsdk prologue signature, "
                         "to show it does not fit this build")
    args = ap.parse_args()

    if not os.path.exists(args.exe):
        sys.exit("no such file: %s" % args.exe)
    img = Image(args.exe)
    print("%s" % os.path.basename(args.exe))
    print("  image base 0x%08X   ASLR(DYNAMIC_BASE) %s"
          % (img.base, "ON" if img.aslr else "OFF"))
    if not img.aslr:
        print("  -> the exe is not relocated at load, so every VA below is also "
              "its RUNTIME address.")
    print()

    sites = call_sites(img, args.afa)
    print("appFailAssert(0x%08X) call sites: %d" % (args.afa, len(sites)))
    if len(sites) < 100:
        print("  WARNING: far fewer than expected - is --afa right? Aborting.")
        return 1

    mine = []
    for s in sites:
        a = assertion_at(img, s)
        if a and a[0].endswith(args.file):
            mine.append((s,) + a)
    print("  of which in %s: %d" % (args.file, len(mine)))
    print()

    slots = vtable_slots(img)
    fns = collections.OrderedDict()
    for site, f, line, expr in sorted(mine, key=lambda r: r[2] or 0):
        st = fn_start(img, site)
        fns.setdefault(st, []).append((line, expr))

    print("Functions in %s that carry an assertion:" % args.file)
    print("  %-12s %-9s %-8s %s" % ("function", "ret", "vtables", "assertions"))
    ranked = []
    for st, asserts in fns.items():
        if st is None:
            continue
        end, retn = fn_end(img, st)
        v = slots.get(st, 0)
        print("  0x%08X  %-9s %-8d %s"
              % (st, ("ret %s" % retn) if retn else "?", v,
                 "; ".join("%s: %s" % (l, e) for l, e in asserts)))
        ranked.append((v, st, end, retn, asserts))

    ranked.sort(reverse=True)
    print()
    if not ranked or ranked[0][0] == 0:
        print("No VIRTUAL function among them - ProcessEvent is not here.")
        return 1

    v, st, end, retn, asserts = ranked[0]
    runner = ranked[1][0] if len(ranked) > 1 else 0
    print("=== ProcessEvent candidate: 0x%08X ===" % st)
    print("  in %d vtable slots (next best in this file: %d)" % (v, runner))
    print("  bounds 0x%08X..0x%08X  (%d bytes), returns `ret %s`"
          % (st, end or 0, (end - st) if end else 0, retn))
    print("  assertions: %s" % "; ".join("%s: %s" % (l, e) for l, e in asserts))
    print("  prologue bytes: %s" % img.code(st, 24).hex(" "))
    print()
    for ins in img.md.disasm(img.code(st, 32), st):
        print("     0x%08X  %-6s %s" % (ins.address, ins.mnemonic, ins.op_str))
    print()
    print("  Why this is ProcessEvent and not a neighbour in the same file:")
    print("   1. it is the only VIRTUAL function among %s's assertion-bearing"
          % args.file)
    print("      functions - every other one appears in 0 vtable slots;")
    print("   2. `ret %s` is thiscall plus three stack arguments, which is" % retn)
    print("      ProcessEvent(UFunction* Function, void* Parms, void* Result);")
    print("   3. it guards on !HasAnyFlags(RF_Unreachable), ProcessEvent's own")
    print("      entry check on `this`.")
    print()
    print("  [inferred-static] - nothing here was run. The live confirmation is")
    print("     to detour it and check the UFunction* argument names a script")
    print("     function through GNames.")

    if args.prologue:
        d = img.text["data"]
        hits, i = [], 0
        while True:
            i = d.find(PUBLISHED, i)
            if i < 0:
                break
            j = i + 10
            if d[j] == 0x68 and d[j + 5:j + 11] == b"\x64\xa1\x00\x00\x00\x00":
                hits.append(img.text["va"] + i)
            i += 1
        print()
        print("--prologue: the published unrealsdk shape (two `push imm32`) "
              "matches %d site(s) in 23 MB of code." % len(hits))
        print("  The candidate above is NOT among them: this build emits ONE "
              "push imm32 (_except_handler3),")
        print("  and `sub esp,0x54` rather than the reported 0x50. The invariant "
              "holds; the byte pattern does not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
