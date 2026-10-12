"""Jamer Quest world data. Every room is 17 x 11 tiles.

Rooms in an area grid ("over" / "cave") connect through edge openings.
Objects in a map (S, C, N, D, $ ...) take their details, in reading order
(left-to-right, top-to-bottom), from the room's matching list.

Outside:  T tree  . grass  f flowers  p bush  b cuttable shrub  w water
          W waterfall  = bridge  R rock  M cave mouth  F fence  G grave
          r roof  h house wall  D door  S sign  C chest  N npc
          E spider  e hunter spider  H heart  g gem
Inside:   # wall  _ floor  u rug  Z/z bed  d drawer  c candles  O exit  $ shop item
Cave:     % wall  , floor  R rock  1 red barrier  2 blue barrier  t target
          P push block  ~ gate (opens when enemies are cleared)  L locked door
          U stairs (appear after boss)  X boss
"""

SIGN_WELCOME = ["Welcome to a Zelda-like game. Maybe you will find it enjoyable.",
                "Do not fail, Jameson. We are watching. :)"]
SIGN_DIRECTIONS = ["North: Fan Residence\nWest: DiPalma Shores"]

T_SWORD = ["You got a sword. Press the A key to use. This item can be used to",
           "harm enemies and cut down bushes."]
T_BOW = ["You got the bow and arrow. Press the Q key to use. Arrows are unlimited, but",
         "only a certain amount of arrows can be shot at a time."]
T_GEM1 = ["1 measely gem? That's not very exciting."]
T_GEM10 = ["You got 10 gems. Don't spend it all in one place."]
T_GEM100 = ["You got 100 gems. You're delighted!"]
T_KEY = ["You got a key. Use it to open a locked door."]
T_BOSS_KEY = ["You got the Boss Key! It opens the big door deep in the dungeon."]
T_CONTAINER = ["You got a Heart Container! Your health went up by one heart."]

NPC_BROTHER_VILLAGE = ["Hey Mister! My brother needs your help to clear out an old family sex dungeon.",
                       "Our house is to the north. ...now where did I put the key...",
                       "I think I dropped it by the graves to the east. You'll need something sharp to get through the brambles."]
NPC_BROTHER_HOUSE = ["You talked to my brother? Please clear out our sex dungeon! Ghosts have",
                     "been terrorizing that place for way too long. Take my bow and arrow",
                     "with you and be careful!"]
NPC_BROTHER_HOUSE_AFTER = ["The dungeon is in Mt. Rock, south of the village. Good luck!"]
NPC_THANKS_1 = ["Thank you for clearing out our family sex dungeon! Here is some money to reward you.",
                "It may not look like a lot, but it is all my brother and I had saved up."]
NPC_THANKS_2 = ["Wow thanks man. Now our ancestors can rest in peace."]
NPC_SHOP = ["Welcome, welcome! Gems for goods. Stand by an item and press E to buy it."]

ROOMS = {
    # ===================================================================== overworld
    ("over", 1, 1): {
        "name": "VILLAGE", "kind": "outside", "music": "village",
        "map": [
            "TTTTTTT...TTTTTTT",
            "T.f............fT",
            "T.rrrr......ww..T",
            "T.hDhh..f...ww..T",
            "..........S......",
            ".....N...........",
            "..............S..",
            "T.f..........f..T",
            "T..TT......TT...T",
            "T...............T",
            "TTTTTTT...TTTTTTT",
        ],
        "S": [SIGN_WELCOME, SIGN_DIRECTIONS],
        "N": [{"id": "brother_village", "look": "red", "text": NPC_BROTHER_VILLAGE, "hide_if": "boss_dead"}],
        "D": [{"to": ("house", "shop"), "spawn": (8, 9)}],
    },
    ("over", 1, 0): {
        "name": "FAN RESIDENCE", "kind": "outside", "music": "village",
        "map": [
            "TTTTTTTTTTTTTTTTT",
            "T.f....TTT....f.T",
            "T....rrrrrrr....T",
            "T....rrrrrrr....T",
            "T....hhhDhhh..S.T",
            "T...............T",
            "TT..f.......f..TT",
            "T...FF.....FF...T",
            "T...............T",
            "T...............T",
            "TTTTTTT...TTTTTTT",
        ],
        "S": [["THE FAN RESIDENCE. Please wipe your feet."]],
        "D": [{"to": ("house", "fan"), "spawn": (8, 9)}],
    },
    ("over", 0, 1): {
        "name": "DIPALMA SHORES", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTT...TTTTTTT",
            "TWW....bbb......T",
            "Twwwwww.........T",
            "Twwwwwwwwwwww...T",
            "TwwC.=======..S..",
            "Twwwwwwwwwwww....",
            "Twwwwwwwwwww.....",
            "Twwwwwwww.......T",
            "Twwwww......f...T",
            "T.ww............T",
            "TTTTTTTTTTTTTTTTT",
        ],
        "S": [["DIPALMA SHORES. No swimming. No fishing. No fun."]],
        "C": [{"id": "sword", "item": "sword", "text": T_SWORD}],
    },
    ("over", 0, 0): {
        "name": "WHISPERING WOODS", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTTTTTTTTTTTT",
            "T.C...T.....T..CT",
            "T.TT..T.TT.T.TT.T",
            "T..T....T....T..T",
            "TT.TTTT.T.TTTT.TT",
            "T......E....E...T",
            "T.TTTTT.T.TTTTT.T",
            "T...f...T...f...T",
            "TTTT..TTTTT..TTTT",
            "T......H........T",
            "TTTTTTT...TTTTTTT",
        ],
        "C": [{"id": "woods_100", "item": "gems", "amount": 100, "text": T_GEM100},
              {"id": "woods_1", "item": "gems", "amount": 1, "text": T_GEM1}],
    },
    ("over", 2, 1): {
        "name": "EAST ROAD", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTT...TTTTTTT",
            "T...f.........f.T",
            "T..TT.......TT..T",
            "T......S........T",
            "........E.......T",
            ".............E..T",
            "...........f....T",
            "T..TT.......TT..T",
            "T......bbb......T",
            "T..f...bbb...f..T",
            "TTTTTTT...TTTTTTT",
        ],
        "S": [["North: The Old Graveyard. Mind the spiders.", "South: ...something rustles behind those bushes."]],
    },
    ("over", 2, 0): {
        "name": "OLD GRAVEYARD", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTTTTTTTTTTTT",
            "T.G..G..G..G..G.T",
            "T...............T",
            "T.G..G.FFF.G..G.T",
            "T......FCF......T",
            "T......FbF......T",
            "T.G..G..e..G..G.T",
            "T...............T",
            "T.G..G.....G..G.T",
            "T...e...........T",
            "TTTTTTT...TTTTTTT",
        ],
        "C": [{"id": "grave_key", "item": "key", "text": T_KEY}],
    },
    ("over", 1, 2): {
        "name": "MT. ROCK", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTT...TTTTTTT",
            "T.f.............T",
            "T...p.......p...T",
            "T.......S.......T",
            "T...E.......E...T",
            "T...............T",
            "RRRRRRRRMRRRRRRRR",
            "RRRRRRRRRRRRRRRRR",
            "RRRRRRRRRRRRRRRRR",
            "RRRRRRRRRRRRRRRRR",
            "RRRRRRRRRRRRRRRRR",
        ],
        "S": [["MT. ROCK. The old family dungeon lies within. KEEP OUT."]],
        "M": [{"to": ("cave", 1, 2), "spawn": (8, 9), "lock": "mountain_door"}],
    },
    ("over", 2, 2): {
        "name": "SECRET GROVE", "kind": "outside", "music": "overworld",
        "map": [
            "TTTTTTT...TTTTTTT",
            "T...f.......f...T",
            "T.TTT.......TTT.T",
            "T.T...f...f...T.T",
            "T.T..f.....f..T.T",
            "T.....f.C.f.....T",
            "T.T..f.....f..T.T",
            "T.T...f...f...T.T",
            "T.TTT.......TTT.T",
            "T...f.......f...T",
            "TTTTTTTTTTTTTTTTT",
        ],
        "C": [{"id": "grove_container", "item": "container", "text": T_CONTAINER}],
    },

    # ===================================================================== interiors
    ("house", "shop"): {
        "name": "SHOP", "kind": "house", "music": "shop",
        "map": [
            "#################",
            "#c_____________c#",
            "#_______N_______#",
            "#_____ddddd_____#",
            "#_______________#",
            "#_____$___$_____#",
            "#_______________#",
            "#______uuu______#",
            "#______uuu______#",
            "#_______________#",
            "########O########",
        ],
        "N": [{"id": "shopkeeper", "look": "green", "text": NPC_SHOP}],
        "$": [{"id": "refill", "name": "HEART REFILL", "price": 10},
              {"id": "container", "name": "HEART CONTAINER", "price": 80, "once": True}],
        "O": [{"to": ("over", 1, 1), "spawn": (3, 4)}],
    },
    ("house", "fan"): {
        "name": "FAN RESIDENCE", "kind": "house", "music": "village",
        "map": [
            "#################",
            "#Z__d_____c___dZ#",
            "#z_____________z#",
            "#_______________#",
            "#______uuu______#",
            "#______uNu______#",
            "#______uuu______#",
            "#c_____________c#",
            "#_______________#",
            "#_______________#",
            "########O########",
        ],
        "N": [{"id": "brother_house", "look": "green", "text": NPC_BROTHER_HOUSE, "gives": "bow",
               "after_text": NPC_BROTHER_HOUSE_AFTER, "hide_if": "boss_dead"}],
        "O": [{"to": ("over", 1, 0), "spawn": (8, 5)}],
    },

    # ===================================================================== dungeon
    # Same four rooms as the original Mt. Rock dungeon: entry, west switch room,
    # east block room (holds the key), and the ghost's lair north of the entry.
    ("cave", 1, 2): {
        "name": "DUNGEON - ENTRY", "kind": "cave", "music": "dungeon",
        "map": [
            "%%%%%%%%L%%%%%%%%",
            "%,,,,,,,,,,,,,,,%",
            "%,,,,E,,,,,%%,,,%",
            "%,,,,,,,,,,%%,,,%",
            ",,,,,,,,,,,,,,,,,",
            "%,,,%%,,,,,,,,,,%",
            "%,,,%%,,,,,,,,,,%",
            "%,,,,,,,,,,,,E,,%",
            "%,,,,,,,,,,,,,,,%",
            "%%%%%%%%,%%%%%%%%",
            "%%%%%%%%O%%%%%%%%",
        ],
        "L": [{"lock": "boss_door", "needs": "boss_key"}],
        "O": [{"to": ("over", 1, 2), "spawn": (8, 5)}],
    },
    ("cave", 0, 2): {
        "name": "DUNGEON - WEST WING", "kind": "cave", "music": "dungeon",
        "map": [
            "%%%%%%%%%%%%%%%%%",
            "%f2C2t%%%%%%%%,,%",
            "%,222,%%%%%%%%,,%",
            "%,,,,,1,,,E,2,,,%",
            "%,,E,,1,,,,,2,,,,",
            "%f,,,E1,,,,,2,,,%",
            "%wwwE,1,,E,,2,,,%",
            "%www,,1E,,,,2,,t%",
            "%wwwE,1,,,,,2,,,%",
            "%wwwf,1,,,,,2,,,%",
            "%%%%%%%%%%%%%%%%%",
        ],
        "C": [{"id": "west_100", "item": "gems", "amount": 100, "text": T_GEM100}],
    },
    ("cave", 2, 2): {
        "name": "DUNGEON - EAST WING", "kind": "cave", "music": "dungeon",
        "map": [
            "%%%%%%%%%%%%%%%%%",
            "%%%%%%%,,,,,,,,,%",
            "%%%%%%%,%%%%%,,,%",
            "%,,%%%%,%%%%%,E,%",
            ",,,%%%%,%%%%%,,,%",
            "%,,,P,,,,%%%%,,,%",
            "%%%%%%%%%%%%%PPP%",
            "%%%%%%%%%%%%%,,,%",
            "%fCfE,,,%%%%%%,%%",
            "%,,,,E,,,,,,,,,,%",
            "%%%%%%%%%%%%%%%%%",
        ],
        "C": [{"id": "boss_key", "item": "boss_key", "text": T_BOSS_KEY}],
    },
    ("cave", 1, 1): {
        "name": "DUNGEON - THE GHOST'S LAIR", "kind": "cave", "music": "dungeon",
        "map": [
            "%%%%%%%%O%%%%%%%%",
            "%,,,,,,,X,,,,,,,%",
            "%,,,,,,,,,,,,,,,%",
            "wwwwwwww~wwwwwwww",
            "wwwwwwww~wwwwwwww",
            "%,,,,,,,,,,,,,,,%",
            "%,,,,,,,,,,,,,,,%",
            "%,,,,,,,,,,,,,,,%",
            "%,,,,,,,,,,,,,,,%",
            "%,,,,,,,,,,,,,,,%",
            "%%%%%%%%,%%%%%%%%",
        ],
        "O": [{"to": ("house", "fan"), "spawn": (8, 9)}],
    },
}

START_ROOM = ("over", 1, 1)
START_POS = (8, 6)
ENTRY_ROOM = ("cave", 1, 2)

for _key, _room in ROOMS.items():
    assert len(_room["map"]) == 11, _key
    for _row in _room["map"]:
        assert len(_row) == 17, (_key, _row)
