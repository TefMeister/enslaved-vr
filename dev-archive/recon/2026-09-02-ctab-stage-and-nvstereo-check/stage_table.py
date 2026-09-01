import struct, sys, collections
data = open(sys.argv[1],'rb').read()
names = set(sys.argv[2].split(','))
cnt = collections.Counter(); stages = collections.Counter()
i = 0
while True:
    ct = data.find(b'CTAB', i)
    if ct < 0: break
    i = ct + 4
    base = ct + 4
    try: size, creator, version, nconst, cinfo, flags, target = struct.unpack_from('<7I', data, base)
    except struct.error: continue
    if not (0 < nconst < 512) or base + cinfo + nconst*20 > len(data): continue
    ver = struct.unpack_from('<I', data, ct-8)[0]
    stage = {0xFFFE: 'VS', 0xFFFF: 'PS'}.get(ver >> 16, 'unk%08x' % ver)
    stages[stage] += 1
    for k in range(nconst):
        o = base + cinfo + k*20
        name_off, regset, regidx, regcount, _r, _ti, _dv = struct.unpack_from('<IHHHHII', data, o)
        name = data[base+name_off:data.find(b'\0', base+name_off)].decode('latin-1')
        if name in names: cnt[(name, stage, 'c%d' % regidx, 'x%d' % regcount)] += 1
print('tables by stage:', dict(stages))
for k, v in sorted(cnt.items()): print(v, k)
