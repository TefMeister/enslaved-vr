"""find code that references given VAs (imm32 operands / displacements), print function context."""
import sys, struct, pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
EXE = r"D:\Program Files (x86)\Steam\steamapps\common\Enslaved\Binaries\Win32\Enslaved.exe"
d = open(EXE, 'rb').read()
pe = pefile.PE(data=d, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
text = [s for s in pe.sections if s.Characteristics & 0x20000000]

def va2off(va):
    for s in pe.sections:
        if s.VirtualAddress <= va - IB < s.VirtualAddress + s.Misc_VirtualSize:
            return va - IB - s.VirtualAddress + s.PointerToRawData

def raw_hits(target):
    pat = struct.pack('<I', target)
    out = []
    for s in text:
        a, b = s.PointerToRawData, s.PointerToRawData + s.SizeOfRawData
        i = d.find(pat, a, b)
        while i != -1:
            out.append(IB + s.VirtualAddress + i - a)
            i = d.find(pat, i + 1, b)
    return out

md = Cs(CS_ARCH_X86, CS_MODE_32)
def dis(va, n=40, back=0):
    o = va2off(va - back)
    for ins in md.disasm(d[o:o + n * 8], va - back):
        print(f"  {ins.address:08x}  {ins.mnemonic:6} {ins.op_str}")
        n -= 1
        if n <= 0: break

if __name__ == '__main__':
    for t in sys.argv[1:]:
        t = int(t, 16)
        hs = raw_hits(t)
        print(f"== {t:08x}: {len(hs)} hits", ' '.join(f'{h:08x}' for h in hs[:30]))
