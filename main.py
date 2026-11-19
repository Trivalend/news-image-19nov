#!/usr/bin/env python3
"""news-image-20261119 -- The World in One Day.

A newspaper front page that sums up Thursday 19 November 2026 in one
1024x1024 PNG. Pure standard library, no network, deterministic output:
two runs produce byte-identical files.

Drawn entirely in code: a hand-written 5x7 bitmap font, flat vector
illustrations, a stylised world map. No external images, no copied code.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 239, 221)     # cream newsprint
PAPER2 = (255, 253, 246)    # card white
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (179, 39, 30)
BLUE = (46, 90, 136)
TEAL = (46, 125, 107)
GOLD = (201, 162, 39)
SKY = (191, 217, 232)
SEA = (207, 224, 234)
LAND = (217, 200, 154)
LINE = (180, 168, 140)
GREEN = (74, 140, 74)
ORANGE = (214, 110, 44)
PINK = (226, 143, 138)

# ---------------------------------------------------------------- 5x7 font
# Every glyph is 7 rows of 5 cells, '#' = ink. Written by hand here.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10010", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ',': ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u00b7': ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '\u2013': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u20ac': ("00111", "01000", "10000", "11110", "10000", "01000", "00111"),
    '\u00e1': ("00010", "00100", "01110", "00001", "01111", "10001", "01111"),
    '\u00e9': ("00010", "00100", "01110", "10001", "11111", "10000", "01110"),
    '\u00f1': ("01010", "10101", "11110", "10001", "10001", "10001", "10001"),
}
FONT = {k: tuple(r.replace('0', '.').replace('1', '#') for r in v)
        for k, v in FONT.items()}
FONT['?'] = ("01110", "10001", "00001", "00110", "00100", "00000", "00100")


def adv(size, bold=False):
    """Advance width of one character at the given cap-height size."""
    return size * 6.0 / 7.0 + (1.0 if bold else 0.0)


def text_width(s, size, bold=False):
    if not s:
        return 0.0
    return len(s) * adv(size, bold) - size / 7.0


def wrap_text(s, size, max_w, bold=False):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        t = w if not cur else cur + ' ' + w
        if text_width(t, size, bold) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg)) * (w * h)

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(col)

    def fill_rect(self, x, y, w, h, col):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, col):
        self.fill_rect(x, y, w, 1, col)

    def vline(self, x, y, h, col):
        self.fill_rect(x, y, 1, h, col)

    def rect(self, x, y, w, h, col, t=1):
        self.fill_rect(x, y, w, t, col)
        self.fill_rect(x, y + h - t, w, t, col)
        self.fill_rect(x, y, t, h, col)
        self.fill_rect(x + w - t, y, t, h, col)

    def line(self, x0, y0, x1, y1, col):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, col)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, col):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, col)

    def ring(self, cx, cy, r, col):
        for a in range(0, 360, 3):
            self.set(int(cx + r * math.cos(math.radians(a))),
                     int(cy + r * math.sin(math.radians(a))), col)

    def poly(self, pts, col):
        ys = [p[1] for p in pts]
        y0, y1 = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, yy0 = pts[i]
                x1, yy1 = pts[(i + 1) % n]
                if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                    t = (y - yy0) / (yy1 - yy0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                a, b = max(0, int(xs[i])), min(self.w - 1, int(xs[i + 1]))
                if b >= a:
                    self.hline(a, y, b - a + 1, col)


# --------------------------------------------------------------------- text
def draw_text(cv, x, y, s, size, col, bold=False, italic=False):
    """Draw s with its top at y. Returns the x just past the last glyph."""
    cx = float(x)
    gw = max(1, int(round(size * 5 / 7)))
    gh = max(1, int(round(size)))
    for ch in s:
        g = FONT.get(ch, FONT['?'])
        for ty in range(gh):
            sy = ty * 7 // gh
            row = g[sy]
            slant = (gh - 1 - ty) // 4 if italic else 0
            for tx in range(gw):
                if row[tx * 5 // gw] == '#':
                    px = int(cx) + tx + slant
                    py = int(y) + ty
                    cv.set(px, py, col)
                    if bold:
                        cv.set(px + 1, py, col)
        cx += adv(size, bold)
    return cx


def draw_lines(cv, x, y, lines, size, leading, col, bold=False, italic=False):
    for ln in lines:
        draw_text(cv, x, y, ln, size, col, bold=bold, italic=italic)
        y += leading
    return y


# ---------------------------------------------------------------------- PNG
def png_bytes(cv):
    """Encode the canvas as a PNG (filter 0 rows, zlib level 9)."""
    w, h = cv.w, cv.h
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += cv.px[y * w * 3:(y + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = tag + data
        return (struct.pack('>I', len(data)) + c +
                struct.pack('>I', zlib.crc32(c) & 0xffffffff))

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', comp) + chunk(b'IEND', b''))


# ------------------------------------------------------- hero illustrations
def hero_summit(cv, x, y, w, h):
    """Shenzhen summit: sky, skyline, three flags, three leaders at a table."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.disc(x + w - 26, y + 14, 9, GOLD)
    # skyline
    for bx, bh in ((0, 16), (16, 24), (34, 13), (52, 28), (72, 18), (92, 26),
                   (112, 15), (132, 30), (154, 20), (176, 26), (198, 14),
                   (218, 24), (240, 17), (262, 27), (284, 16), (302, 22)):
        cv.fill_rect(x + bx, y + h - 12 - bh, 16, bh, (70, 96, 122))
    cv.fill_rect(x, y + h - 12, w, 12, (52, 74, 96))
    # three flags on poles
    def flag(fx, cols):
        cv.vline(fx, y + 6, 26, INK)
        for i, c in enumerate(cols):
            cv.fill_rect(fx + 1, y + 6 + i * 5, 18, 5, c)
    flag(x + 40, (RED, PAPER2, RED))
    flag(x + 130, (RED, RED, RED))
    flag(x + 220, (PAPER2, BLUE, RED))
    # table + three suited figures
    cv.fill_rect(x + 90, y + h - 26, 140, 6, (122, 84, 52))
    for fx in (105, 150, 195):
        cv.fill_rect(x + fx, y + h - 40, 16, 16, (32, 32, 40))
        cv.disc(x + fx + 8, y + h - 46, 6, (232, 196, 160))
        cv.fill_rect(x + fx + 7, y + h - 40, 2, 14, PAPER2)


def hero_gta(cv, x, y, w, h):
    """GTA VI: Vice City sunset, palms, road, car."""
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(226 + (214 - 226) * t)
        g = int(143 + (110 - 143) * t)
        b = int(138 + (90 - 138) * t)
        cv.hline(x, y + i, w, (r, g, b))
    cv.disc(x + w // 2, y + h - 8, 16, (240, 180, 60))
    # buildings
    for bx, bh in ((8, 18), (30, 26), (54, 14), (250, 22), (272, 30), (296, 16)):
        cv.fill_rect(x + bx, y + h - 22 - bh, 20, bh, (96, 52, 96))
    # palms
    for px in (90, 220):
        cv.line(x + px, y + h - 22, x + px + 4, y + 8, (90, 60, 30))
        for dx, dy in ((-12, 0), (-6, -4), (0, -6), (8, -4), (14, 0)):
            cv.line(x + px + 4, y + 8, x + px + 4 + dx, y + 8 + dy, (46, 110, 60))
    # road + car
    cv.fill_rect(x, y + h - 16, w, 16, (40, 40, 44))
    for dx in range(6, w, 24):
        cv.fill_rect(x + dx, y + h - 8, 12, 2, (240, 220, 120))
    cv.fill_rect(x + 130, y + h - 30, 60, 10, (24, 24, 28))
    cv.fill_rect(x + 142, y + h - 38, 34, 9, (24, 24, 28))
    cv.disc(x + 142, y + h - 18, 5, INK)
    cv.disc(x + 178, y + h - 18, 5, INK)
    cv.disc(x + 142, y + h - 18, 2, (180, 180, 180))
    cv.disc(x + 178, y + h - 18, 2, (180, 180, 180))


def hero_ipo(cv, x, y, w, h):
    """Anthropic IPO: candlestick chart, rising arrow, exchange building."""
    cv.fill_rect(x, y, w, h, (220, 234, 217))
    base = y + h - 10
    # candlesticks
    bars = [(12, 16, GREEN), (30, 24, GREEN), (48, 12, RED), (66, 28, GREEN),
            (84, 20, GREEN), (102, 34, GREEN), (120, 18, RED), (138, 30, GREEN)]
    for bx, bh, c in bars:
        cv.fill_rect(x + bx, base - bh, 12, bh, c)
        cv.vline(x + bx + 6, base - bh - 4, bh + 8, c)
    # rising arrow
    cv.line(x + 160, base - 6, x + 300, y + 8, RED)
    cv.line(x + 300, y + 8, x + 282, y + 8, RED)
    cv.line(x + 300, y + 8, x + 300, y + 24, RED)
    cv.line(x + 160, base - 6, x + 176, base - 6, RED)
    cv.line(x + 160, base - 6, x + 160, base - 20, RED)
    # exchange building
    bx, by = 168, y + 10
    cv.fill_rect(x + bx, y + 26, 120, h - 36, (232, 226, 208))
    cv.poly([(x + bx - 6, y + 26), (x + bx + 60, y + 8),
             (x + bx + 126, y + 26)], (120, 100, 70))
    for cx in range(bx + 12, bx + 112, 24):
        cv.fill_rect(x + cx, y + 34, 8, h - 44, (120, 100, 70))
    draw_text(cv, x + bx + 44, y + 12, "$", 14, (20, 90, 60), bold=True)


# --------------------------------------------------------- mini illustrations
MINI_TINTS = [(226, 232, 238), (238, 226, 210), (232, 226, 220), (226, 236, 226),
              (238, 224, 224), (228, 232, 226), (236, 232, 220), (226, 228, 236),
              (232, 236, 230), (238, 230, 226)]


def draw_mini(cv, x, y, w, h, kind, tint):
    cv.fill_rect(x, y, w, h, tint)
    cx, cy = x + w // 2, y + h // 2
    if kind == 'gavel':      # law
        cv.line(cx - 7, cy + 5, cx + 7, cy - 5, (90, 60, 30))
        cv.fill_rect(cx - 9, cy - 7, 10, 4, (90, 60, 30))
        cv.fill_rect(cx + 3, cy + 1, 8, 3, (90, 60, 30))
    elif kind == 'sun':      # climate
        cv.disc(cx, cy, 5, GOLD)
        for a in range(0, 360, 45):
            cv.line(cx, cy, cx + int(9 * math.cos(math.radians(a))),
                    cy + int(9 * math.sin(math.radians(a))), GOLD)
    elif kind == 'storm':    # cyclone
        cv.ring(cx, cy, 8, TEAL)
        cv.ring(cx, cy, 5, TEAL)
        cv.disc(cx, cy, 2, TEAL)
    elif kind == 'bridge':   # kerch bridge
        cv.line(x + 4, cy + 6, x + w - 4, cy + 6, INK)
        cv.line(x + 6, cy + 6, x + w // 2, cy - 6, INK)
        cv.line(x + w - 6, cy + 6, x + w // 2, cy - 6, INK)
        cv.vline(x + w // 2, cy - 6, 12, INK)
    elif kind == 'flag':     # ukraine
        cv.vline(cx - 4, cy - 8, 16, INK)
        cv.fill_rect(cx - 3, cy - 8, 14, 5, BLUE)
        cv.fill_rect(cx - 3, cy - 3, 14, 5, GOLD)
    elif kind == 'rain':     # florida floods
        cv.disc(cx - 4, cy - 2, 4, (120, 130, 140))
        cv.disc(cx + 4, cy - 2, 4, (120, 130, 140))
        for dx in (-6, 0, 6):
            cv.line(cx + dx, cy + 4, cx + dx - 2, cy + 8, BLUE)
    elif kind == 'strata':   # geology
        cv.poly([(x + 4, cy + 7), (cx, cy - 7), (x + w - 4, cy + 7)], (120, 100, 70))
        cv.fill_rect(x + 4, cy + 4, w - 8, 2, (90, 80, 60))
        cv.fill_rect(x + 4, cy + 7, w - 8, 2, (70, 90, 110))
    elif kind == 'ballot':   # politics
        cv.fill_rect(cx - 8, cy - 3, 16, 11, (160, 140, 100))
        cv.fill_rect(cx - 5, cy - 1, 10, 2, INK)
        cv.fill_rect(cx - 4, cy - 9, 8, 6, PAPER2)
        cv.vline(cx, cy - 9, 6, RED)
    elif kind == 'shield':   # gulf all-clear
        cv.poly([(cx - 7, cy - 8), (cx + 7, cy - 8), (cx + 7, cy + 1),
                 (cx, cy + 9), (cx - 7, cy + 1)], TEAL)
        cv.line(cx - 4, cy, cx - 1, cy + 3, PAPER2)
        cv.line(cx - 1, cy + 3, cx + 5, cy - 4, PAPER2)
    elif kind == 'pills':    # drug seizure
        cv.fill_rect(cx - 9, cy - 3, 12, 5, RED)
        cv.fill_rect(cx + 3, cy - 3, 12, 5, BLUE)
        cv.disc(cx - 9, cy, 2, PAPER2)
        cv.disc(cx + 15, cy, 2, PAPER2)


# ------------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-55, 52), (-60, 46), (-75, 35), (-80, 25),
     (-90, 21), (-97, 16), (-105, 20), (-117, 33), (-125, 40), (-124, 48),
     (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-70, -18),
     (-70, -30), (-65, -40), (-68, -52), (-65, -55), (-60, -45), (-55, -35),
     (-48, -28), (-40, -22), (-35, -8), (-50, -2), (-60, 0), (-70, 8)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 2), (40, -5), (40, -15), (35, -25), (28, -33),
     (18, -35), (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5), (-13, 8),
     (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70),
     (20, 70), (12, 66), (5, 60), (5, 58), (-2, 57), (-5, 50), (-8, 43),
     (-9, 37)],
    [(30, 70), (40, 68), (60, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (162, 56), (158, 52),
     (142, 50), (140, 40), (130, 35), (127, 30), (122, 32), (120, 25),
     (110, 20), (105, 10), (100, 8), (98, 15), (95, 16), (90, 22), (85, 20),
     (80, 10), (77, 8), (75, 15), (70, 22), (60, 25), (55, 26), (50, 29),
     (48, 30), (43, 28), (40, 32), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (135, -35),
     (140, -38), (146, -39), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (136, -12), (132, -12), (126, -14), (122, -17),
     (118, -20)],
]

# (number, lon, lat, display dx, display dy)
PINS = [
    (1, 114.1, 22.5, 0, 0), (2, -74.0, 40.7, -4, -8), (3, -74.0, 40.7, 10, 6),
    (4, 4.3, 52.1, -12, -6), (5, 30.7, 36.9, 4, 8), (6, 85.8, 19.8, 0, 0),
    (7, 36.4, 45.3, 8, -8), (8, 30.5, 50.4, -10, -8), (9, -81.5, 27.5, 0, 6),
    (10, -0.1, 51.5, 2, 8), (11, 2.35, 48.85, 12, -2), (12, 42.6, 16.9, 8, 2),
    (13, 20.1, 32.1, -12, 6),
]


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SEA)
    cv.rect(x, y, w, h, LINE, 1)

    def px(lon):
        return int(x + (lon + 170) / 360.0 * w)

    def py(lat):
        return int(y + (75 - lat) / 130.0 * h)

    for cont in CONTINENTS:
        pts = [(px(lon), py(lat)) for lon, lat in cont]
        cv.poly(pts, LAND)
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            cv.line(x0, y0, x1, y1, (150, 135, 100))
    for num, lon, lat, dx, dy in PINS:
        tx, ty = px(lon), py(lat)
        cx, cy = tx + dx, ty + dy
        if dx or dy:
            cv.line(tx, ty, cx, cy, RED)
        cv.disc(cx, cy, 8, RED)
        cv.ring(cx, cy, 8, PAPER2)
        s = str(num)
        tw = text_width(s, 8, bold=True)
        draw_text(cv, cx - tw / 2, cy - 4, s, 8, PAPER2, bold=True)


# ------------------------------------------------------------------- content
NUMBERS = [
    ("$81.3bn", "RAISED BY ANTHROPIC \u2014 LARGEST IPO EVER"),
    ("15.9m", "GTA VI PRE-ORDERS BEFORE LAUNCH"),
    ("200,000", "EVACUATED AHEAD OF CYCLONE AKVAN"),
    ("$120bn", "ADAPTATION FINANCE UNRESOLVED AT COP31"),
    ("730,000", "ROHINGYA WHO FLED IN 2017 \u2014 THE ICJ CASE"),
    ("$190.4m", "RECORD VAN GOGH SALE"),
]

HEROES = [
    ("1 \u00b7 SHENZHEN \u00b7 SUMMIT",
     "Trump, Xi and Putin hold first three-way summit",
     "The three nuclear powers meet at APEC in Shenzhen; arms control "
     "and the Iran war top the agenda.", hero_summit),
    ("2 \u00b7 NEW YORK \u00b7 GAMES",
     "GTA VI arrives after a 13-year wait",
     "Unlocks at midnight, New Zealand first. 15.9m pre-orders banked. "
     "$79.99 on PS5 and Xbox, no PC yet.",
     hero_gta),
    ("3 \u00b7 NASDAQ \u00b7 MARKETS",
     "Anthropic debuts in the biggest IPO on record",
     "Priced at $83, the Claude maker raised $81.3bn, valued near "
     "$1.5tn. First trades set the real price.",
     hero_ipo),
]

CARDS = [
    (4, "THE HAGUE", "LAW", "World Court rules on Myanmar's Rohingya case",
     "The ICJ reads its judgment in The Gambia's case over the 2017 campaign.",
     'gavel'),
    (5, "ANTALYA", "CLIMATE", "COP31 enters its final 48 hours",
     "Ministers take over the text in Antalya; \"phase out\" and the $120bn "
     "adaptation fund are still open.", 'sun'),
    (6, "ODISHA", "STORM", "Akvan bears down as 200,000 flee the coast",
     "Red alerts in 11 districts, schools shut. Landfall near Puri due Friday.",
     'storm'),
    (7, "KERCH STRAIT", "WAR", "Crimean bridge hit again",
     "Traffic halts after a fresh attack, a Russian official says.", 'bridge'),
    (8, "KYIV", "WAR", "Left off the agenda, Ukraine watches Shenzhen",
     "The war is off the summit agenda, the White House says. Kyiv fears "
     "being carved up.", 'flag'),
    (9, "FLORIDA", "WEATHER", "Flooded Florida braces for still more rain",
     "A foot of rain in hours; 300 rescue calls in a night. Schools shut "
     "Thursday.", 'rain'),
    (10, "SCIENCE", "GEOLOGY", "Earth's missing billion years are explained",
     "A Nature study blames mantle currents and ancient ice sheets for "
     "the erasure.", 'strata'),
    (11, "PARIS", "POLITICS", "M\u00e9lenchon could win, says France's justice minister",
     "The hard-left leader is a plausible president, the minister concedes.",
     'ballot'),
    (12, "JAZAN", "GULF", "Saudi Arabia says danger has passed in three cities",
     "The all-clear follows southern alerts after a Houthi missile was downed.",
     'shield'),
    (13, "BENGHAZI", "CRIME", "Cocaine and millions of pills seized in eastern Libya",
     "Officials display one of the country's biggest drug hauls.",
     'pills'),
]

BRIEFS = [
    "14 GAZA \u2014 Israeli tanks cross the Yellow Line; Hamas calls it a truce breach.",
    "15 SHENZHEN \u2014 APEC leaders adopt the Shenzhen Declaration; 21 economies back digital trade.",
    "16 CARACAS \u2014 Hegseth signs a US\u2013Venezuela military deal.",
    "17 WASHINGTON \u2014 Vance: no \"forever war\" in the Gulf.",
    "18 NEW DELHI \u2014 Modi meets the Prince and Princess of Wales.",
    "19 TOKYO \u2014 India and Japan review defence ties at their 2+2.",
    "20 SEOUL \u2014 North Korea expands uranium enrichment, the IAEA says.",
    "21 CANBERRA \u2014 Australia sanctions West Bank settlers.",
    "22 MANAMA \u2014 Bapco refinery back on its feet after the attacks.",
    "23 RIYADH \u2014 Gulf leaders urge Trump not to strike Iran.",
    "24 WASHINGTON \u2014 White House pursues a $2bn-plus loan package for the Philippines.",
    "25 JERUSALEM \u2014 Knesset elects Matan Kahana speaker with 66 votes.",
    "26 BENGALURU \u2014 Amazon pledges $7bn for renewables in India by 2030.",
    "27 SYDNEY \u2014 Duckett's 133 puts England on top in the ODI.",
    "28 AUCKLAND \u2014 New Zealand plays first as GTA VI unlocks at local midnight.",
    "29 PANAMA \u2014 Second arrest over the attack on a journalist's home.",
    "30 SANTA FE \u2014 Residents flee as the Paran\u00e1 River rises.",
    "31 DHAKA \u2014 Garment workers protest for a third week; dozens of factories shut.",
    "32 ADDIS ABABA \u2014 Ethiopia and Eritrea mass forces on their border; clashes reported near Badme.",
    "33 PORT-AU-PRINCE \u2014 El Salvador hails its helicopter raid on a Haiti gang leader's villa.",
    "34 FRANKFURT \u2014 Deutsche Bank handled $582m in Epstein-linked deals, the FT reports.",
    "35 LA PAZ \u2014 Bolivia declares an El Ni\u00f1o emergency; 78,000 families hit.",
    "36 DELHI \u2014 Schools reopen as Delhi lifts its Stage-III pollution curbs.",
]

DATECHECK = ("DATE CHECK \u2014 FIRST REPORTED WEDNESDAY 18 NOV, SO NOT ON "
             "THIS PAGE AS NEWS: the Iranian drone interceptions \u00b7 the EU's "
             "proposed \u20ac45bn loan for Ukraine \u00b7 the House Democrats' "
             "251\u201311 vote nominating Hakeem Jeffries \u00b7 Voyager 1 crossing "
             "one light-day, at 10:16 GMT Wednesday \u00b7 Peltola's Alaska win "
             "\u00b7 Pew's projection that Islam becomes the largest religion by "
             "2035 \u00b7 the first COP31 draft (Monday).")

FOOTER = ("Every story here happened, or was first reported, on Thursday "
          "19 November 2026. Disputed claims are attributed, not stated as "
          "fact. Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, NASA, ICJ, "
          "Pew. Original drawings. The World in One Day \u2014 19 November 2026.")


# -------------------------------------------------------------------- layout
def draw_brief(cv, x, y, text, size, max_w, leading):
    """One numbered brief; the '14 GAZA' head is bold red, body is ink."""
    lines = wrap_text(text, size, max_w - 10)
    for i, ln in enumerate(lines):
        if i == 0:
            idx = ln.find(' \u2014 ')
            if idx >= 0:
                head, rest = ln[:idx], ln[idx:]
                draw_text(cv, x, y, head, size, RED, bold=True)
                draw_text(cv, x + text_width(head, size, bold=True), y,
                          rest, size, INK)
            else:
                draw_text(cv, x, y, ln, size, INK)
        else:
            draw_text(cv, x, y, ln, size, INK)
        y += leading
    return y


def build():
    cv = Canvas(W, H, PAPER)
    x0, x1 = 24, 1000
    cw = x1 - x0
    y = 10

    # masthead
    draw_text(cv, x0, y, "THE WORLD IN ONE DAY", 20, INK, bold=True)
    s = "THURSDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES"
    draw_text(cv, x1 - text_width(s, 11, bold=True), y + 6, s, 11, GREY,
              bold=True)
    y += 24
    cv.fill_rect(x0, y, cw, 2, INK)
    cv.fill_rect(x0, y + 4, cw, 1, INK)
    y += 8

    # giant date headline
    draw_text(cv, x0, y, "Thursday 19 November 2026", 38, INK, bold=True)
    y += 40
    # red italic subhead
    sub = ("Three leaders meet in Shenzhen \u00b7 GTA VI arrives at last "
           "\u00b7 The biggest IPO ever debuts")
    draw_text(cv, x0, y, sub, 13, RED, italic=True)
    y += 14
    cv.fill_rect(x0, y, cw, 1, INK)
    y += 4

    # number strip
    colw = (cw - 5 * 8) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = x0 + i * (colw + 8)
        if i:
            cv.vline(cx - 4, y + 2, 44, LINE)
        draw_text(cv, cx, y, num, 21, RED, bold=True)
        draw_lines(cv, cx, y + 25, wrap_text(cap, 8, colw), 8, 9.5, INK)
    y += 46
    cv.fill_rect(x0, y, cw, 1, INK)
    y += 4

    # three hero cards
    hw = (cw - 2 * 8) // 3
    hh = 130
    for i, (kick, head, deck, ill) in enumerate(HEROES):
        hx = x0 + i * (hw + 8)
        cv.fill_rect(hx, y, hw, hh, PAPER2)
        cv.rect(hx, y, hw, hh, LINE, 1)
        ill(cv, hx + 1, y + 1, hw - 2, 34)
        draw_text(cv, hx + 8, y + 39, kick, 9, RED, bold=True)
        head_lines = wrap_text(head, 13, hw - 16, bold=True)
        draw_lines(cv, hx + 8, y + 52, head_lines, 13, 15, INK, bold=True)
        draw_lines(cv, hx + 8, y + 52 + len(head_lines) * 15 + 2,
                   wrap_text(deck, 9.5, hw - 16), 9.5, 11, INK)
    y += hh + 3

    # ten numbered cards, 5 x 2
    cw5 = (cw - 4 * 8) // 5
    chh = 120
    for row in range(2):
        for col in range(5):
            num, place, beat, head, deck, kind = CARDS[row * 5 + col]
            cx = x0 + col * (cw5 + 8)
            cy = y + row * (chh + 4)
            cv.fill_rect(cx, cy, cw5, chh, PAPER2)
            cv.rect(cx, cy, cw5, chh, LINE, 1)
            draw_mini(cv, cx + 1, cy + 1, cw5 - 2, 20, kind,
                      MINI_TINTS[row * 5 + col])
            draw_text(cv, cx + 6, cy + 23,
                      "%d \u00b7 %s \u00b7 %s" % (num, place, beat),
                      7.5, RED, bold=True)
            draw_lines(cv, cx + 6, cy + 35,
                       wrap_text(head, 10, cw5 - 12, bold=True),
                       10, 11.5, INK, bold=True)
            nlines = len(wrap_text(head, 10, cw5 - 12, bold=True))
            draw_lines(cv, cx + 6, cy + 35 + nlines * 11.5,
                       wrap_text(deck, 9, cw5 - 12), 9, 9.5, GREY)
    y += 2 * chh + 3 + 3

    # world map panel
    draw_text(cv, x0, y, "WHERE IT HAPPENED", 11, INK, bold=True)
    draw_text(cv, x1 - text_width("13 STORIES PINNED", 9), y + 1,
              "13 STORIES PINNED", 9, GREY)
    y += 12
    draw_map(cv, x0, y, cw, 48)
    y += 48 + 5

    # briefs
    draw_text(cv, x0, y,
              "ALSO ON THURSDAY 19 NOVEMBER \u2014 23 MORE STORIES",
              13, RED, bold=True)
    y += 15
    for b in BRIEFS:
        y = draw_brief(cv, x0, y, b, 11, cw, 13.5)
    y = int(y + 0.5) + 3

    # date check box (the "DATE CHECK" head is bold red, rest is ink)
    dc_lines = wrap_text(DATECHECK, 10, cw - 16)
    box_h = int(8 + len(dc_lines) * 12 + 6 + 0.5)
    cv.fill_rect(x0, y, cw, box_h, (253, 246, 232))
    cv.rect(x0, y, cw, box_h, RED, 2)
    yy = y + 6
    for i, ln in enumerate(dc_lines):
        if i == 0:
            idx = ln.find(' \u2014 ')
            head, rest = ln[:idx], ln[idx:]
            draw_text(cv, x0 + 8, yy, head, 10, RED, bold=True)
            draw_text(cv, x0 + 8 + text_width(head, 10, bold=True), yy,
                      rest, 10, INK)
        else:
            draw_text(cv, x0 + 8, yy, ln, 10, INK)
        yy += 12
    y += box_h + 3

    # footer
    for ln in wrap_text(FOOTER, 9, cw):
        tw = text_width(ln, 9)
        draw_text(cv, x0 + (cw - tw) / 2, y, ln, 9, GREY)
        y += 10.5
    assert y <= H, "layout overflow: final y=%d" % y
    return cv


def main():
    # safety: every character used must exist in the font
    all_text = ([s for pair in NUMBERS for s in pair] +
                [s for h in HEROES for s in h[:3]] +
                [s for c in CARDS for s in
                 ("%d \u00b7 %s \u00b7 %s" % (c[0], c[1], c[2]), c[3], c[4])] +
                BRIEFS + [DATECHECK, FOOTER,
                          "THE WORLD IN ONE DAY",
                          "THURSDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES",
                          "Thursday 19 November 2026",
                          "Three leaders meet in Shenzhen \u00b7 GTA VI arrives "
                          "at last \u00b7 The biggest IPO ever debuts",
                          "WHERE IT HAPPENED", "13 STORIES PINNED",
                          "ALSO ON THURSDAY 19 NOVEMBER \u2014 23 MORE STORIES"])
    missing = sorted({ch for s in all_text for ch in s if ch not in FONT})
    assert not missing, "missing glyphs: %r" % missing

    cv = build()
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'entry.png'), 'wb') as f:
        f.write(png_bytes(cv))


if __name__ == '__main__':
    main()
