"""The fixed sequence of cutscenes and games, plus progress tracking."""

# Each step: (id, kind, payload). Cutscene payload is a list of pages; the
# optional "controls" entry is shown as a card under the final page.
STEPS = [
    ("intro", "cutscene", {
        "pages": [
            "Jameson.",
            "Let's play a game. A test of your skills, a test of your luck, a test of your patience.",
            "Let's start with something simple...",
        ],
        "controls": ["ARROWS - STEER", "EAT 20 APPLES"],
    }),
    ("snake", "snake", {}),
    ("pre_platformer", "cutscene", {
        "pages": [
            "Very good. You pick up fast.",
            "Now, let's try something a little more challenging...",
            "Use WASD and the space bar to move. Press J to attack.",
            "These will be your only instructions.",
        ],
        "controls": ["A/D - MOVE", "W/SPACE - JUMP", "J - ATTACK"],
    }),
    ("platformer", "platformer", {}),
    ("pre_rhythm", "cutscene", {
        "pages": [
            "It seems you've bested us all in battle.",
            "But some challenges still await. This one is a bit more... musical.",
            "Press Z X C V B to select notes, press SPACE to play them.",
        ],
        "controls": ["HOLD Z X C V B - FRET", "SPACE - STRUM"],
    }),
    ("rhythm", "rhythm", {}),
    ("pre_adventure", "cutscene", {
        "pages": [
            "Your rhythm, your sense of showmanship... remarkable.",
            "Now for something more old school...",
            "Use the arrow keys to move and E to interact.",
        ],
        "controls": ["ARROWS - MOVE", "E - INTERACT"],
    }),
    ("adventure", "adventure", {}),
    ("pre_doom", "cutscene", {
        "pages": [
            "Well, well, well. You've made it this far.",
            "It seems nothing can stop you now.",
            "I hope you have a mouse nearby...",
        ],
        "controls": ["WASD - MOVE", "MOUSE - AIM", "CLICK - SHOOT"],
    }),
    ("doom", "doom", {}),
    ("finale", "cutscene", {
        "pages": [
            "Very good, Jameson, very good!",
            "It seems you've mastered all our tests... for now.",
            "Be a good boy and go out back behind the house...",
            "...the door is unlocked.",
        ],
        "final": True,
    }),
    ("end", "end", {}),
]

INDEX = {sid: i for i, (sid, _k, _p) in enumerate(STEPS)}

# What the chapter-select screen offers: (label, step id it starts from)
CHAPTERS = [
    ("I.   SNAKE", "intro"),
    ("II.  THE GAUNTLET", "pre_platformer"),
    ("III. TURN AND COUGH", "pre_rhythm"),
    ("IV.  JAMER QUEST", "pre_adventure"),
    ("V.   HELL ARENA", "pre_doom"),
    ("VI.  THE DOOR", "finale"),
]


class Story:
    def __init__(self, app):
        self.app = app
        self.current = None

    def build(self, index):
        sid, kind, payload = STEPS[index]
        app = self.app
        if kind == "cutscene":
            from .scenes.cutscene import CutsceneScene
            return CutsceneScene(app, sid, **payload)
        if kind == "snake":
            from .scenes.snake import SnakeScene
            return SnakeScene(app)
        if kind == "platformer":
            from .platformer import PlatformerScene
            return PlatformerScene(app)
        if kind == "rhythm":
            from .rhythm import RhythmScene
            return RhythmScene(app)
        if kind == "adventure":
            from .adventure import AdventureScene
            return AdventureScene(app)
        if kind == "doom":
            from .raycaster import DoomScene
            return DoomScene(app)
        if kind == "end":
            from .scenes.ending import EndScene
            return EndScene(app)
        raise ValueError(kind)

    def goto(self, index, fade=True):
        if isinstance(index, str):
            index = INDEX[index]
        self.current = index
        if index > self.app.save["reached"]:
            self.app.save["reached"] = index
        self.app.switch(lambda: self.build(index), fade=fade)

    def complete(self):
        """Current step finished: move to the next one."""
        if self.current is None:
            return
        nxt = self.current + 1
        if nxt >= len(STEPS):
            self.to_title()
            return
        self.goto(nxt)

    def restart(self):
        if self.current is not None:
            self.app.audio.stop_all()
            self.goto(self.current)

    def to_title(self):
        from .scenes.title import TitleScene
        self.current = None
        self.app.switch(lambda: TitleScene(self.app))

    def new_run(self, sid="intro"):
        """Start from a chapter fresh (drops mid-chapter checkpoints)."""
        self.app.save["checkpoints"] = {}
        self.goto(sid)

    def checkpoint(self, name, value=None, clear=False):
        cps = dict(self.app.save.data.get("checkpoints", {}))
        if clear:
            cps.pop(name, None)
            self.app.save["checkpoints"] = cps
            return None
        if value is None:
            return cps.get(name)
        cps[name] = value
        self.app.save["checkpoints"] = cps
        return value

    def continue_index(self):
        """Where 'Continue' should start: games resume at their intro cutscene."""
        reached = min(self.app.save["reached"], len(STEPS) - 1)
        if STEPS[reached][1] not in ("cutscene", "end") and reached > 0:
            return reached - 1
        if STEPS[reached][1] == "end":
            return INDEX["finale"]
        return reached

    def unlocked(self, sid):
        return INDEX[sid] <= self.app.save["reached"]
