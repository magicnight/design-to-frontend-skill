# -*- coding: utf-8 -*-
"""Verify a PNG really has a usable alpha channel (not a baked-in background).

Decodes IDAT with stdlib zlib, unfilters scanlines, then reports corner/edge alpha and overall
fully_transparent / semi / opaque percentages. For a clean cut-out the corners should read alpha 0.
If they don't, strengthen the transparency style block in the prompt and regenerate.

Usage:  python check_alpha.py out/foo.png out/bar.png
"""
import struct, sys, zlib


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def decode_png(path):
    with open(path, "rb") as f:
        raw = f.read()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, meta = 8, [], None
    while pos < len(raw):
        (length,) = struct.unpack(">I", raw[pos:pos + 4])
        ctype = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            w, h, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", data)
            meta = (w, h, depth, color, interlace)
        elif ctype == b"IDAT":
            idat.append(data)
        elif ctype == b"IEND":
            break
        pos += 12 + length
    w, h, depth, color, interlace = meta
    assert depth == 8 and color == 6 and interlace == 0, f"unsupported: depth={depth} color={color} interlace={interlace}"
    decomp = zlib.decompress(b"".join(idat))
    stride, bpp = w * 4, 4
    out = bytearray(w * h * 4)
    prev = bytearray(stride)
    pos = 0
    for y in range(h):
        f = decomp[pos]
        line = bytearray(decomp[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                c = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + paeth(a, prev[i], c)) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, out


def main():
    for path in sys.argv[1:]:
        w, h, px = decode_png(path)

        def alpha(x, y):
            return px[(y * w + x) * 4 + 3]

        corners = [alpha(0, 0), alpha(w - 1, 0), alpha(0, h - 1), alpha(w - 1, h - 1)]
        edges = [alpha(w // 2, 0), alpha(w // 2, h - 1), alpha(0, h // 2), alpha(w - 1, h // 2)]
        total = w * h
        transparent = sum(1 for i in range(3, len(px), 4) if px[i] == 0)
        semi = sum(1 for i in range(3, len(px), 4) if 0 < px[i] < 255)
        print(f"{path}")
        print(f"  {w}x{h}  corners_alpha={corners}  edge_mid_alpha={edges}")
        print(f"  fully_transparent={transparent/total:.1%}  semi={semi/total:.1%}  opaque={(total-transparent-semi)/total:.1%}")


if __name__ == "__main__":
    main()
