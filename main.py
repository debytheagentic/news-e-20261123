import os
import struct
import zlib

W = H = 1024
PAPER = (248, 240, 232)
INK = (16, 29, 58)
RED = (168, 24, 24)
OCHRE = (176, 112, 24)
DOTS = (110, 145, 190)
CHAR = (30, 30, 35)
REGIONS = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC", "AFRICA", "OCEANIA", "WORLD"]

RAW = """ANTALYA|COP31 ends with no climate pact|190 nations|First UN climate summit failure since 2009|WORLD|0
BENGHAZI|Russian corvette Merkury sinks|0 dead|Sea-drone claim unconfirmed; UN wants probe|AFRICA|0
SYDNEY|US lead over China in Asia shrinks|5.3 points|Lowy index 78.9 to 73.6; narrowest since 2018|ASIA-PACIFIC|0
JAKARTA|Candy factory fire death toll rises|24 bags|About 30 missing; 300 were inside|ASIA-PACIFIC|1
WARSAW|Poland calls missile incursion a provocation|2 missiles|One landed 20 miles from NATO drills|EUROPE|1
JERUSALEM|Coalition talks end without a deal|48 seats|Eisenkot has until 6 December to form government|MIDDLE EAST|1
SEOUL|Education minister resigns over exam chaos|550,000|CSAT rules changed late; president accepts quit|ASIA-PACIFIC|0
ATLANTA|Delta delays worsen after systems glitch|1,169 flights|FAA ground delay at Hartsfield-Jackson|AMERICAS|0
SANAA|Airstrikes and Houthi drone kill|5 dead|18 hurt; oil facility hit in capital|MIDDLE EAST|0
PORT VILA|M6.5 quake strikes Vanuatu|6.5 magnitude|02:40 UTC; Pacific tsunami advisory issued|OCEANIA|1
TUPANCIRENA|Storm devastates southern Brazil|5 dead|265 injured; thousands displaced|AMERICAS|0
LAGOS|Boat accident death toll rises|24 dead|River disaster on Nigerian waterway|AFRICA|0
KINSHASA|Ebola outbreak spreads at record pace|5,600+|WHO says emergency continues|AFRICA|1
RIYADH|Saudi Arabia intercepts Houthi missiles|3 missiles|Alerts sounded in the capital|MIDDLE EAST|0
TEHRAN|Iran holds new talks with Qatari mediators|2 sides|War with US; conditions still demanded|MIDDLE EAST|1
BRUSSELS|EU and Indonesia sign trade pact|98.5%|Tariffs cut; EUR600m a year saved|EUROPE|0
PARIS|Billionaire wealth-tax rally gathers|100+|2% minimum levy proposed|EUROPE|0
MADRID|Bank tax extension to fund housing|EUR1.4bn|One-year renewal for protected housing|EUROPE|0
BERLIN|Metal workers walk out over pay|23,000|IG Metall extends industrial action|EUROPE|0
COPENHAGEN|Denmark approves expanded US Greenland access|1 pact|Parliament ratifies Arctic defence deal|EUROPE|0
HANOI|Land reform passed to speed projects|1 law|Compensation rights strengthened|ASIA-PACIFIC|0
CANBERRA|China and Australia agree AI safety talks|2 nations|Dialogue launched after APEC meeting|OCEANIA|0
WELLINGTON|NZ counts nearly 400,000 special votes|400,000|Government formation delayed|OCEANIA|1
TOKYO|Rocket launches shift to Mitsubishi|1 flagship|JAXA hands over commercial operations|ASIA-PACIFIC|0
SANTIAGO|Auditor probes government OpenAI deal|10 days|Minister ordered to explain terms|AMERICAS|0
BUENOS AIRES|Sovereign risk climbs above 1,000 points|1,000|Debt financing for 2027 questioned|AMERICAS|0
OTTAWA|Canada seeks US military reassurance|1 memo|Pentagon restrictions on ties reported|AMERICAS|0
NEW YORK|Nvidia faces questions over China chip sales|1 firm|Bessent seeks compliance accountability|AMERICAS|1
ACCRA|Ghana wins amputee football world cup|1-0|Black Challenge beat Morocco in WAFF final|AFRICA|0
THE HAGUE|Myanmar rejects ICJ Rohingya ruling|2017|France urges UN action on genocide finding|ASIA-PACIFIC|1"""

STORIES = [ln.split("|") for ln in RAW.splitlines()]
PINS = [(0, 30, 10), (1, 26, 13), (2, 45, 21), (3, 40, 16), (4, 30, 7), (5, 29, 12),
        (7, 13, 11), (9, 46, 20), (11, 25, 14), (12, 26, 17), (18, 29, 7),
        (22, 48, 23), (25, 17, 21), (28, 25, 14)]
AREAS = [(6, 16, 3, 8), (11, 19, 12, 21), (20, 24, 1, 3), (22, 27, 4, 9),
         (22, 28, 10, 18), (27, 44, 2, 11), (33, 36, 10, 12), (40, 46, 18, 22),
         (46, 48, 21, 23)]

FONT = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/00010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11110/00001/00001/01110/00001/00001/11110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/11110/00001/00001/10001/01110",
    "6": "00110/01000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00001/01110",
    " ": "00000/00000/00000/00000/00000/00000/00000",
    ".": "00000/00000/00000/00000/00000/01100/01100",
    ",": "00000/00000/00000/00000/00110/00100/01000",
    ":": "00000/01100/01100/00000/01100/01100/00000",
    ";": "00000/01100/01100/00000/01100/01100/01000",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "|": "00100/00100/00100/00100/00100/00100/00100",
    "(": "00010/00100/01000/01000/01000/00100/00010",
    ")": "01000/00100/00010/00010/00010/00100/01000",
    "%": "11001/11010/00010/00100/01000/01011/10011",
    "+": "00000/00100/00100/11111/00100/00100/00000",
    "=": "00000/00000/11111/00000/11111/00000/00000",
    "?": "01110/10001/00001/00010/00100/00000/00100",
    "'": "00100/00100/01000/00000/00000/00000/00000",
    "/": "00001/00010/00010/00100/01000/01000/10000",
    "[": "01110/01000/01000/01000/01000/01000/01110",
    "]": "01110/00010/00010/00010/00010/00010/01110",
    "_": "00000/00000/00000/00000/00000/00000/11111",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    "<": "00010/00100/01000/10000/01000/00100/00010",
    ">": "01000/00100/00010/00001/00010/00100/01000",
    "&": "01100/10010/10100/01000/10101/10010/01101",
}
FONT = {k: v.split("/") for k, v in FONT.items()}

buf = bytearray(bytes(PAPER) * (W * H))


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x0, y0, x1, y1, c):
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(W - 1, x1); y1 = min(H - 1, y1)
    if x1 < x0 or y1 < y0:
        return
    row = bytes(c) * (x1 - x0 + 1)
    for y in range(y0, y1 + 1):
        i = (y * W + x0) * 3
        buf[i:i + len(row)] = row


def frame(x0, y0, x1, y1, c, t=1):
    rect(x0, y0, x1, y0 + t - 1, c)
    rect(x0, y1 - t + 1, x1, y1, c)
    rect(x0, y0, x0 + t - 1, y1, c)
    rect(x1 - t + 1, y0, x1, y1, c)


def disc(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(x, y, c)


def measure(s, sc):
    return len(s) * 6 * sc - sc


def text(s, x, y, sc, c):
    for ch in s.upper():
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for ry, row in enumerate(glyph):
            for rx, bit in enumerate(row):
                if bit == "1":
                    for dy in range(sc):
                        base = (y + ry * sc + dy) * W
                        for dx in range(sc):
                            i = (base + x + rx * sc + dx) * 3
                            if 0 <= i < len(buf) - 2 and 0 <= x + rx * sc + dx < W:
                                buf[i] = c[0]
                                buf[i + 1] = c[1]
                                buf[i + 2] = c[2]
        x += 6 * sc
    return x


def ctext(s, y, sc, c):
    text(s, (W - measure(s, sc)) // 2, y, sc, c)


def wrap(s, sc, maxw):
    out, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if measure(trial, sc) <= maxw:
            cur = trial
        elif not cur:
            raise SystemExit("overflow: " + word)
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def save(path):
    stride = W * 3
    scan = bytearray()
    for y in range(H):
        scan.append(0)
        scan += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", zlib.compress(bytes(scan), 6)) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


rect(0, 0, W, 24, INK)
rect(0, 1006, W, H, INK)
ctext("THE WORLD IN ONE DAY | MONDAY 23 NOVEMBER 2026", 8, 1, PAPER)
ctext("MONDAY 23 NOVEMBER 2026 | ONE PAGE", 1011, 1, PAPER)

mast = "Monday 23 November 2026"
text(mast, (W - measure(mast, 6)) // 2 + 1, 34, 6, INK)
text(mast, (W - measure(mast, 6)) // 2, 34, 6, INK)
rect(40, 86, 984, 88, RED)
ctext("reported Monday 23 November 2026", 96, 2, RED)
ctext("COP31 ends without a pact | US-China gap at 5.3 | 24 bags recovered in Java", 118, 2, INK)

rect(0, 140, W, 188, CHAR)
stats = [(STORIES[i][2], lab) for i, lab in [(0, "COP31"), (2, "Asia power"), (3, "Java fire"),
                                             (8, "Yemen strikes"), (4, "Poland"), (5, "Israel bloc")]]
for i, (value, label) in enumerate(stats):
    x = 40 + i * 158
    text(value, x, 146, 3, OCHRE)
    text(label, x, 172, 1, PAPER)
    if i:
        rect(x - 12, 146, x - 11, 184, PAPER)

rect(0, 190, W, 228, INK)
rx = 40
for i, r in enumerate(REGIONS):
    cnt = sum(1 for s in STORIES if s[4] == r)
    label = r + " " + str(cnt)
    cw = measure(label, 2)
    col = RED if i < 4 else OCHRE
    frame(rx, 192, rx + cw + 12, 218, col)
    text(label, rx + 6, 198, 2, PAPER)
    rx += cw + 18
total = str(len(STORIES)) + " stories | " + str(sum(1 for s in STORIES if s[5] == "1")) + " ONGOING"
text(total, 984 - measure(total, 2), 198, 2, PAPER)
rect(0, 226, W, 228, OCHRE)

rect(40, 236, 560, 420, CHAR)
for ri in range(26):
    for ci in range(50):
        top, bot = None, None
        for lo, hi, t, b in AREAS:
            if t <= ri <= b and lo <= ci <= hi:
                top, bot = lo, hi
                break
        if top is not None:
            px, py = 44 + ci * 6, 240 + ri * 7
            rect(px, py, px + 3, py + 3, DOTS)
for i, cx, cy in PINS:
    px, py = 44 + cx * 6, 240 + cy * 7
    disc(px, py, 9, RED)
    t = str(i + 1)
    text(t, px - measure(t, 1) // 2, py - 3, 1, PAPER)

for i in range(3):
    s = STORIES[i]
    x, y = 572, 236 + i * 62
    rect(x, y, 984, y + 58, INK)
    rect(x, y, 984, y + 2, RED)
    text(s[0], x + 8, y + 4, 2, RED)
    text(s[1], x + 8, y + 18, 1, PAPER)
    text(s[2], x + 8, y + 38, 3, OCHRE)
    text(s[3], x + 8 + measure(s[2], 3) + 8, y + 42, 2, PAPER)

rect(40, 430, 984, 520, (200, 200, 205))
for j, s in enumerate(STORIES[3:]):
    x = 40 + (j % 3) * 308
    y = 430 + (j // 3) * 51
    line = f"{j + 4:02d} {s[0]} - {s[1]} [{s[2]}]: {s[3]}" + (" ONGOING" if s[5] == "1" else "")
    lines = wrap(line, 1, 298)
    if y + 10 * len(lines) > 894:
        raise SystemExit("overflow: " + s[0])
    for k, part in enumerate(lines):
        text(part, x, y + 10 * k, 1, INK)

frame(40, 906, 984, 950, RED)
text("DATE CHECK", 48, 912, 2, RED)
for k, line in enumerate(wrap("Stories are what was reported Monday 23 November 2026. Some events occurred Sunday; they appear only where Monday reporting advanced them.", 2, 920)[:2]):
    text(line, 48, 932 + k * 11, 1, INK)
text("Sources: Reuters, AP, BBC, Xinhua, Al Jazeera, AFP, Lowy Institute, UNFCCC, national wires.", 40, 956, 1, INK)
text("CERTAINTY  REPORTED = carried by wires   CLAIM = one side's account   FORECAST = scheduled / unresolved", 40, 976, 1, INK)

out = os.environ.get("OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
save(os.path.join(out, "entry.png"))
print("wrote", os.path.join(out, "entry.png"), len(STORIES), "stories")
