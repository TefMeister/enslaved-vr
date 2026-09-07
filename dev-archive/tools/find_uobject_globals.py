#!/usr/bin/env python3
"""find_uobject_globals.py - locate GObjObjects / GNames / ProcessEvent in a 32-bit UE3 binary
by exploiting the fact that this build shipped with DO_CHECK enabled.

Written 2026-09-07 for enslaved-vr, route (B). Method comes from the /gr drop
`engine-research/inbox/2026-09-05-gr-gobjobjects-is-an-assertion-string-and-do-check-is-on.md`:

  UE3's check() macro is
      #define check(expr) { if(!(expr)) appFailAssert( #expr, __FILE__, __LINE__ ); ... }
  so `#expr` stringifies the asserted expression. A retail build with DO_CHECK on
  therefore contains literal strings naming the globals it guards, e.g.
      check( GObjObjects.Num() == 0 )
  Crucially the call to appFailAssert sits INSIDE the function that tests the
  global, so a few instructions earlier the global appears as a DIRECT MEMORY
  OPERAND. That is the address itself, not a hint toward it.

  appFailAssert(expr, file, line) is __cdecl, so the call site pushes in reverse:
      push <line>            ; imm32, a plausible source line number
      push offset <__FILE__> ; a path ending .cpp  <-- free confirmation
      push offset <#expr>    ; the string naming the global
      call appFailAssert

The __FILE__ neighbour both distinguishes a real hit from a coincidence and tells
you which assertion you are standing in.

This script reads ONLY the executable's own code and strings and emits addresses.
It extracts no game content.

Usage:  python find_uobject_globals.py <path to exe> [symbol ...]
"""
import sys
import collections

try:
    import pefile
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
except ImportError:
    sys.exit("needs pefile and capstone")

DEFAULT_SYMBOLS = ["GObjObjects", "GObjLoaded", "GObjRoot", "GNames", "ProcessEvent"]


def load(path):
    pe = pefile.PE(path, fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase
    secs = []
    for s in pe.sections:
        name = s.Name.rstrip(b"\x00").decode("latin1")
        data = s.get_data()
        secs.append({
            "name": name,
            "va": base + s.VirtualAddress,
            "vsize": max(s.Misc_VirtualSize, len(data)),
            "data": data,
            "exec": bool(s.Characteristics & 0x20000000),
            "write": bool(s.Characteristics & 0x80000000),
        })
    return pe, base, secs


def sec_of(secs, va):
    for s in secs:
        if s["va"] <= va < s["va"] + s["vsize"]:
            return s
    return None


def read_cstr(secs, va, limit=260):
    s = sec_of(secs, va)
    if not s:
        return None
    off = va - s["va"]
    end = s["data"].find(b"\x00", off, off + limit)
    if end < 0:
        return None
    raw = s["data"][off:end]
    try:
        t = raw.decode("ascii")
    except UnicodeDecodeError:
        return None
    return t if all(32 <= ord(c) < 127 for c in t) else None


def find_strings(secs, needle):
    """Every ASCII occurrence of `needle`, reported at the START of its C string."""
    hits = []
    nb = needle.encode("ascii")
    for s in secs:
        d = s["data"]
        i = d.find(nb)
        while i >= 0:
            start = d.rfind(b"\x00", 0, i)
            start = 0 if start < 0 else start + 1
            text = read_cstr(secs, s["va"] + start)
            if text and needle in text:
                hits.append((s["va"] + start, s["name"], text))
            i = d.find(nb, i + 1)
    # de-duplicate by address, keep order
    seen, out = set(), []
    for h in hits:
        if h[0] not in seen:
            seen.add(h[0]); out.append(h)
    return out


def find_push_refs(secs, target_va):
    """Sites doing `push imm32` with imm32 == target_va (opcode 0x68)."""
    pat = b"\x68" + target_va.to_bytes(4, "little")
    out = []
    for s in secs:
        if not s["exec"]:
            continue
        d = s["data"]
        i = d.find(pat)
        while i >= 0:
            out.append(s["va"] + i)
            i = d.find(pat, i + 1)
    return out


def disasm_window(md, secs, va, back=140, fwd=32):
    s = sec_of(secs, va)
    if not s:
        return []
    start = max(s["va"], va - back)
    off = start - s["va"]
    n = (va - start) + fwd
    return list(md.disasm(s["data"][off:off + n], start))


def globals_near(md, secs, call_va, back=160):
    """Data addresses used as direct memory operands shortly BEFORE call_va.
    These are the candidates for the global the assertion guards."""
    cands = []
    for ins in disasm_window(md, secs, call_va, back=back, fwd=0):
        if ins.address >= call_va:
            break
        op = ins.op_str
        if "[" not in op:
            continue
        # direct absolute operand: [0xXXXXXXXX] with no register inside
        j = op.find("[")
        k = op.find("]", j)
        if k < 0:
            continue
        inner = op[j + 1:k]
        if not inner.startswith("0x"):
            continue
        if any(r in inner for r in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp")):
            continue
        try:
            addr = int(inner, 16)
        except ValueError:
            continue
        sd = sec_of(secs, addr)
        if sd and sd["write"] and not sd["exec"]:
            cands.append((addr, sd["name"], ins.mnemonic, ins.op_str, ins.address))
    return cands


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    symbols = sys.argv[2:] or DEFAULT_SYMBOLS
    pe, base, secs = load(path)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = False

    print("image base 0x%08X" % base)
    print("%-10s %-12s %-10s %s" % ("section", "va", "size", "flags"))
    for s in secs:
        print("%-10s 0x%08X   %-10d %s%s" % (s["name"], s["va"], s["vsize"],
                                             "X" if s["exec"] else " ",
                                             "W" if s["write"] else " "))

    for sym in symbols:
        print("\n" + "=" * 78)
        print("SYMBOL: %s" % sym)
        print("=" * 78)
        strs = find_strings(secs, sym)
        if not strs:
            print("  no ASCII occurrence")
            continue
        print("  %d string occurrence(s):" % len(strs))
        for va, sname, text in strs:
            print("    0x%08X  %-8s  %r" % (va, sname, text[:88]))

        tally = collections.Counter()
        detail = collections.defaultdict(list)
        for va, sname, text in strs:
            refs = find_push_refs(secs, va)
            if not refs:
                continue
            for r in refs:
                # the __FILE__ push is normally the very next push after this one
                nxt = None
                for ins in disasm_window(md, secs, r + 64, back=64, fwd=0):
                    if ins.address > r and ins.mnemonic == "push" and ins.op_str.startswith("0x"):
                        t = read_cstr(secs, int(ins.op_str, 16))
                        if t and (".cpp" in t.lower() or ".h" in t.lower()):
                            nxt = t
                            break
                print("    ref at 0x%08X   __FILE__=%s" % (r, nxt or "(none seen)"))
                for addr, dsec, mn, ops, at in globals_near(md, secs, r):
                    tally[addr] += 1
                    detail[addr].append((r, mn, ops, at))

        if tally:
            print("\n  data globals touched near those assertion sites"
                  " (higher count = referenced from more sites):")
            for addr, n in tally.most_common(12):
                mn, ops = detail[addr][0][1], detail[addr][0][2]
                print("    0x%08X  x%-3d  e.g. %s %s" % (addr, n, mn, ops))


if __name__ == "__main__":
    main()
