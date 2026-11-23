import os
from PIL import Image, ImageDraw, ImageFont

PAPER = (248, 240, 232)
INK = (16, 29, 58)
RED = (168, 24, 24)
OCHRE = (176, 112, 24)
DOTS = (110, 145, 190)
CHAR = (30, 30, 35)
W = H = 1024
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
MAP = []
for r in range(26):
    row = ["."] * 50
    for lo, hi, top, bot in AREAS:
        if top <= r <= bot:
            for c in range(lo, hi + 1):
                row[c] = "#"
    MAP.append("".join(row))

img = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(img)
_cache = {}


def F(n):
    if n not in _cache:
        _cache[n] = ImageFont.load_default(size=n)
    return _cache[n]


def fit(s, f, maxw):
    if draw.textlength(s, font=f) > maxw:
        raise SystemExit("overflow: " + s)


def txt(s, x, y, n, c):
    f = F(n)
    fit(s, f, W - x)
    draw.text((x, y), s, font=f, fill=c)


def ctr(s, y, n, c):
    f = F(n)
    fit(s, f, W)
    draw.text(((W - draw.textlength(s, font=f)) / 2, y), s, font=f, fill=c)


def bold(s, x, y, n, c):
    f = F(n)
    fit(s, f, W - x - 1)
    draw.text((x + 1, y), s, font=f, fill=c)
    draw.text((x, y), s, font=f, fill=c)


def wrap(s, f, maxw):
    out, cur = [], ""
    for word in s.split():
        t = word if not cur else cur + " " + word
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        elif not cur:
            raise SystemExit("unbreakable: " + word)
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def flow(items, x0, y0, ncols, colw, step, bottom):
    f = F(15)
    for j, s in enumerate(items):
        x = x0 + (j % ncols) * colw
        y = y0 + (j // ncols) * step
        lines = wrap(f"{j + 4:02d} {s[0]} - {s[1]} [{s[2]}]: {s[3]}" + (" ONGOING" if s[5] == "1" else ""), f, colw - 10)
        if y + 15 * len(lines) > bottom:
            raise SystemExit("flow overflow: " + s[0])
        for k, line in enumerate(lines):
            draw.text((x, y + 15 * k), line, font=f, fill=INK)


draw.rectangle((0, 0, W, 24), fill=INK)
draw.rectangle((0, 1006, W, H), fill=INK)
ctr("THE WORLD IN ONE DAY | MONDAY 23 NOVEMBER 2026", 5, 13, PAPER)
ctr("MONDAY 23 NOVEMBER 2026 | ONE PAGE", 1011, 13, PAPER)

ctrb = "Monday 23 November 2026"
fw = draw.textlength(ctrb, font=F(48))
bold(ctrb, (W - fw) / 2 - 1, 30, 48, INK)
draw.rectangle((40, 88, 984, 90), fill=RED)
ctr("reported Monday 23 November 2026", 96, 17, RED)
ctr("COP31 ends without a pact | US-China gap at 5.3 | 24 bags recovered in Java", 120, 15, INK)

draw.rectangle((0, 140, W, 188), fill=CHAR)
stats = [(STORIES[i][2], lab) for i, lab in [(0, "COP31"), (2, "Asia power"), (3, "Java fire"),
                                             (8, "Yemen strikes"), (4, "Poland"), (5, "Israel bloc")]]
draw.rectangle((0, 190, W, 228), fill=INK)
for i, (value, label) in enumerate(stats):
    x = 40 + i * 158
    bold(value, x, 146, 22, OCHRE)
    fit(label, F(13), 150)
    txt(label, x, 172, 13, PAPER)
    if i:
        draw.rectangle((x - 12, 146, x - 11, 184), fill=PAPER)
rx = 40
for i, r in enumerate(REGIONS):
    cnt = sum(1 for s in STORIES if s[4] == r)
    label = f"{r} {cnt}"
    cw = draw.textlength(label, font=F(15))
    col = RED if i < 4 else OCHRE
    draw.rectangle((rx, 192, rx + cw + 12, 218), outline=col, width=1)
    txt(label, rx + 6, 198, 15, PAPER)
    rx += cw + 18
total = f"{len(STORIES)} stories | {sum(1 for s in STORIES if s[5] == '1')} ONGOING"
fit(total, F(15), 240)
txt(total, 984 - draw.textlength(total, font=F(15)), 198, 15, PAPER)
draw.rectangle((0, 226, W, 228), fill=OCHRE)

draw.rectangle((40, 236, 380, 470), fill=CHAR)
for ri, row in enumerate(MAP):
    for ci, ch in enumerate(row):
        if ch == "#":
            px, py = 44 + ci * 6.5, 240 + ri * 8.8
            draw.rectangle((px, py, px + 3, py + 3), fill=DOTS)
for i, cx, cy in PINS:
    px, py = 44 + cx * 6.5 + 1, 240 + cy * 8.8 + 1
    draw.ellipse((px - 9, py - 9, px + 9, py + 9), fill=RED)
    t = str(i + 1)
    draw.text((px - draw.textlength(t, font=F(13)) / 2, py - 9), t, font=F(13), fill=PAPER)

for i in range(3):
    s = STORIES[i]
    x, y = 392, 236 + i * 78
    draw.rectangle((x, y, 984, y + 74), fill=INK, outline=INK, width=2)
    draw.rectangle((x, y, 984, y + 2), fill=RED)
    txt(s[0], x + 8, y + 6, 15, RED)
    bold(s[1], x + 8, y + 22, 17, PAPER)
    txt(s[2], x + 8, y + 46, 20, OCHRE)
    txt(s[3], x + 8 + draw.textlength(s[2], font=F(20)) + 12, y + 50, 15, PAPER)

flow(STORIES[3:], 40, 478, 3, 308, 46, 894)

draw.rectangle((40, 906, 984, 950), outline=RED, width=1)
bold("DATE CHECK", 48, 912, 15, RED)
for k, line in enumerate(wrap("Stories are what was reported Monday 23 November 2026. Some events occurred Sunday; they appear only where Monday's reporting advanced them.", F(13), 920)[:2]):
    txt(line, 48, 930 + k * 14, 13, INK)
txt("Sources: Reuters, AP, BBC, Xinhua, Al Jazeera, AFP, Lowy Institute, UNFCCC, national wires.", 40, 956, 13, INK)
txt("CERTAINTY  REPORTED = carried by wires   CLAIM = one side's account   FORECAST = scheduled / unresolved", 40, 976, 13, INK)
out = os.environ.get("OUTPUT_DIR", "/output")
os.makedirs(out, exist_ok=True)
img.save(os.path.join(out, "entry.png"))
print("wrote", os.path.join(out, "entry.png"), len(STORIES), "stories")
