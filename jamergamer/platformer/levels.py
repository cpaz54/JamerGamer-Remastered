"""Stage layouts. Each stage is a list of bottom-aligned sections stitched
left-to-right; every section's last line is the bottom row (row 14).

Reach guide: a jump clears ~3 tiles up and ~4 tiles across.
See level.py for the legend.
"""

ROWS = 15


def stitch(*sections):
    out = [""] * ROWS
    for sec in sections:
        width = max(len(r) for r in sec)
        for r in sec:
            assert len(r) == width, f"ragged section row: {r!r}"
        pad = [" " * width] * (ROWS - len(sec))
        for i, row in enumerate(pad + list(sec)):
            out[i] += row
    return out


FLOOR = lambda w: ["X" * w] * 3  # noqa: E731

# ----------------------------------------------------------------- stage 1
STAGE_1 = stitch(
    ["  P             "] + FLOOR(16),
    [
        "            XXXX      ",
        "        XX  XXXX      ",
        "    XX  XX  XXXX      ",
        "XXXXXX  XXXXXXXX   XXX",
        "XXXXXX  XXXXXXXX   XXX",
        "XXXXXX  XXXXXXXX   XXX",
    ],
    [
        "           h              ",
        "         -----            ",
        "                          ",
        "  E               E       ",
    ] + FLOOR(26),
    ["  C           b         "] + FLOOR(24),
    [
        "           ---            ",
        "     ---          ---     ",
        "                          ",
        "XXXX                  XXXX",
        "XXXX                  XXXX",
        "XXXX                  XXXX",
    ],
    [
        "         h          ",
        "      XXXXXXX       ",
        "      XXXXXXX       ",
        "   E  XXXXXXX   E   ",
    ] + FLOOR(20),
    [
        "                       G      ",
        "               XXXXXXXXXXXXXXX",
        "          XXX  XXXXXXXXXXXXXXX",
        "     XXX  XXX  XXXXXXXXXXXXXXX",
        "     XXX  XXX  XXXXXXXXXXXXXXX",
    ] + FLOOR(30),
)

# ----------------------------------------------------------------- stage 2
STAGE_2 = stitch(
    ["  P           "] + FLOOR(14),
    [
        "         F                    ",
        "  |H         ||        H |    ",
        "                              ",
        "XX                          XX",
        "XX                          XX",
        "XX                          XX",
    ],
    [
        "  h                   ",
        "    ~~~~~~~~~~~~~~    ",
        "XXXX              XXXX",
        "XXXXSSSSSSSSSSSSSSXXXX",
        "XXXXXXXXXXXXXXXXXXXXXX",
    ],
    [
        "          F       F     ",
        "                        ",
        "                        ",
        "  C           E         ",
    ] + FLOOR(24),
    [
        "                    ",
        "         |     XXXXX",
        "         V     XXXXX",
        "               XXXXX",
        "               XXXXX",
        "               XXXXX",
        "               XXXXX",
        "    h          XXXXX",
        "   ---         XXXXX",
        "         |     XXXXX",
    ] + FLOOR(20),
    [
        "     E             h      F     ",
        "XXXXXXXXX   XXXXXXX  ~  XXXXX   ",
    ] + ["XXXXXXXXX   XXXXXXX     XXXXX   "] * 11,
    [
        " C                            ",
        "XXXXX                         ",
        "XXXXX                         ",
        "XXXXX   ---                   ",
        "XXXXX                         ",
        "XXXXX         ---             ",
        "XXXXX                         ",
        "XXXXX               XXX       ",
        "XXXXX               XXX       ",
        "XXXXX       F       XXX    G  ",
    ] + FLOOR(30),
)

# ----------------------------------------------------------------- stage 3
STAGE_3 = stitch(
    ["  P           "] + FLOOR(14),
    [
        "    ---        ---           ",
        "                             ",
        " |   B        |  |    B     |",
    ] + FLOOR(29),
    [
        "        |     |     |     ",
        "                          ",
        "        Y     Y     Y     ",
        "                          ",
        "                          ",
        "                          ",
        "   ~~~~~ ~~~~~ ~~~~~ ~~   ",
        "XXX     |     |     |  XXX",
        "XXXSSSSSXSSSSSXSSSSSXSSXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
    [
        "        F     F     ",
        "                    ",
        "                    ",
        " C    E      E      ",
    ] + FLOOR(20),
    [
        "            b         b         ",
        "                                ",
        "        F                       ",
        " |H                         |   ",
        "                                ",
        "XX                            XX",
        "XX                            XX",
        "XX                            XX",
    ],
    [
        "                       F      ",
        "                          G   ",
        "              |       XXXXXXXX",
        "                      XXXXXXXX",
        "                ---   XXXXXXXX",
        "              Y       XXXXXXXX",
        "          ---         XXXXXXXX",
        "                      XXXXXXXX",
        "    ---               XXXXXXXX",
        "              |       XXXXXXXX",
        "  C       E           XXXXXXXX",
    ] + FLOOR(30),
)

# ----------------------------------------------------------------- boss arena
ARENA = [
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X                      X",
    "X  -----        -----  X",
    "X                      X",
    "X                      X",
    "XXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXX",
]

STAGES = [
    {"name": "THE APPROACH", "rows": STAGE_1, "bg": "terrain/bg_forest.png", "theme": "forest"},
    {"name": "THE RAMPARTS", "rows": STAGE_2, "bg": "terrain/bg_forest.png", "theme": "forest"},
    {"name": "THE GAUNTLET", "rows": STAGE_3, "bg": "terrain/throne_hall.png", "theme": "hall"},
]
