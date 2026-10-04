import sys, struct
sys.path.insert(0, r"D:\claude video game stuff\github-backups\staging\enslaved-vr\reader-tools")
from ue3_props import World
COOK = r"D:\Program Files (x86)\Steam\steamapps\common\Enslaved\MonkeyGame\CookedPC"
w = World(COOK)
want = set(a.lower() for a in sys.argv[1:])
for pk in w.pkgs:
    for i, e in enumerate(pk.exports, 1):
        if not e["cls"] or pk.ref_name(e["cls"]) != "Function":
            continue
        outer = pk.ref_name(e["outer"]) or ""
        if outer.lower() not in want:
            continue
        end = e["off"] + e["size"]
        flags = struct.unpack_from("<I", pk.data, end - 12)[0]
        nat = struct.unpack_from("<H", pk.data, end - 15)[0]
        if flags & 0x40:  # FUNC_Net -> RepOffset u16 before FriendlyName
            flags = struct.unpack_from("<I", pk.data, end - 14)[0]
            nat = struct.unpack_from("<H", pk.data, end - 17)[0]
        tags = []
        if flags & 0x400: tags.append("NATIVE")
        if flags & 0x800: tags.append("event")
        if flags & 0x2000: tags.append("static")
        print(f"{pk.name:16} {outer:32} {e['name']:36} flags={flags:08x} iNative={nat} {' '.join(tags)}")
