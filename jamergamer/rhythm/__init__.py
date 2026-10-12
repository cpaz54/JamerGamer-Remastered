"""Chapter III: Turn and Cough - a five-fret rhythm game.

Strum mode (default, like the original): hold Z X C V B and strum with SPACE.
Tap mode (TAB on the intro screen): just press the fret keys on the beat.
"""
import math
import os
import random
import time

import pygame

from .. import ui
from ..config import BLACK, WHITE, NEON
from ..scene import Scene
from . import charts

LANES = 5
FRET_KEYS = [pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b]
STRUM_KEYS = (pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP, pygame.K_DOWN)
COLORS = [(40, 200, 60), (220, 40, 40), (240, 210, 40), (40, 110, 240), (245, 140, 30)]
LABELS = ["Z", "X", "C", "V", "B"]

LOOKAHEAD = 1.6         # seconds of highway visible
CHORD_EPS = 0.045       # notes this close together form one chord
WINDOWS = [(0.045, "PERFECT", 100), (0.085, "GREAT", 75), (0.125, "GOOD", 50)]
MISS_AFTER = 0.13
PASS_ACCURACY = 0.60
# headless test runs use a dummy audio driver whose clock isn't meaningful
SYNC_TO_AUDIO = os.environ.get("SDL_AUDIODRIVER") != "dummy"

W, H = 960, 540
STRIKE_Y = 470
VANISH_Y = 70
CX = W // 2
LANE_GAP = 92           # lane spacing at the strike line
DEPTH = 3.2


def project(z):
    """z: 0 at strike line .. 1 at far end -> (scale, y)."""
    s = 1.0 / (1.0 + z * DEPTH)
    y = VANISH_Y + (STRIKE_Y - VANISH_Y) * s
    return s, y


def lane_x(lane, s):
    return CX + (lane - 2) * LANE_GAP * s


class Note:
    __slots__ = ("t", "lane", "hit", "missed", "group")

    def __init__(self, t, lane):
        self.t, self.lane = t, lane
        self.hit = False
        self.missed = False
        self.group = None


class RhythmScene(Scene):
    size = (W, H)
    title = "TURN AND COUGH"

    def __init__(self, app):
        super().__init__(app)
        song = charts.load()
        self.song = song
        self.tap_mode = bool(app.save["rhythm_tap_mode"])
        self.offset = app.save["rhythm_offset_ms"] / 1000.0
        self.lights = [random.random() * math.tau for _ in range(4)]
        self.crowd = [random.random() for _ in range(48)]
        self.reset()

    def reset(self):
        self.notes = [Note(t, lane) for t, lane in self.song["notes"]]
        groups = []
        for n in self.notes:
            if groups and abs(groups[-1][0].t - n.t) <= CHORD_EPS:
                groups[-1].append(n)
            else:
                groups.append([n])
            n.group = groups[-1]
        self.groups = groups
        self.next_idx = 0           # first group not yet resolved
        self.state = "intro"        # intro -> count -> play -> results
        self.count_t = 0.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.judged = 0
        self.rock = 0.5
        self.feedback = []          # (text, color, life)
        self.sparks = []
        self.lane_flash = [0.0] * LANES
        self.song_time = -3.0
        self.last_wall = time.perf_counter()
        self.end_time = (self.notes[-1].t + 3.0) if self.notes else 5.0
        self.results_t = 0.0
        self.passed = False
        self.overstrums = 0

    def enter(self):
        self.audio.stop_music(400)

    def exit(self):
        if self.audio.enabled:
            pygame.mixer.music.stop()
        self.audio.current = None

    # ------------------------------------------------------------- timing
    # The song clock advances with the game's fixed timestep (so pausing simply
    # stops it) and is gently pulled toward the music's real playback position.
    def _begin_song(self):
        self.state = "play"
        self.song_time = 0.0
        self.last_wall = time.perf_counter()
        if self.song["audio"] and self.audio.enabled:
            try:
                pygame.mixer.music.load(self.song["audio"])
                pygame.mixer.music.set_volume(self.app.save["music_volume"])
                pygame.mixer.music.play()
                self.audio.current = self.song["audio"]
            except pygame.error as e:
                print("[rhythm] could not play song:", e)

    def _advance_clock(self, dt):
        self.song_time += dt
        self.last_wall = time.perf_counter()
        if SYNC_TO_AUDIO and self.audio.enabled and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000.0
            diff = pos - self.song_time
            if pos > 0 and 0.02 < abs(diff) < 1.0:
                self.song_time += diff * 0.1

    def _input_time(self):
        """Song time at the moment of a key press (between fixed updates)."""
        extra = min(0.02, time.perf_counter() - self.last_wall) if SYNC_TO_AUDIO else 0.0
        return self.song_time + extra - self.offset

    # ------------------------------------------------------------- input
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        k = event.key
        if self.state == "intro":
            if k == pygame.K_TAB:
                self.tap_mode = not self.tap_mode
                self.app.save["rhythm_tap_mode"] = self.tap_mode
                self.audio.blip("move")
            elif k in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                self._nudge_offset(k)
            elif k in (pygame.K_RETURN, pygame.K_SPACE):
                if not self.song["notes"]:
                    return
                self.state = "count"
                self.count_t = 0.0
                self.audio.blip("select")
            return
        if self.state == "results":
            if k in (pygame.K_RETURN, pygame.K_SPACE) and self.results_t > 1.0:
                if self.passed:
                    self.app.story.complete()
                else:
                    self.reset()
                    self.state = "count"
            return
        if self.state != "play":
            return
        if k in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
            self._nudge_offset(k)
            return
        now = self._input_time()
        if self.tap_mode:
            if k in FRET_KEYS:
                self._tap(FRET_KEYS.index(k), now)
        elif k in STRUM_KEYS:
            self._strum(now)

    def _nudge_offset(self, k):
        delta = -0.01 if k == pygame.K_LEFTBRACKET else 0.01
        self.offset = round(self.offset + delta, 3)
        self.app.save["rhythm_offset_ms"] = int(round(self.offset * 1000))
        self.feedback.append((f"OFFSET {int(round(self.offset * 1000)):+d}MS", WHITE, 1.0))

    def _held(self):
        keys = pygame.key.get_pressed()
        return {i for i, k in enumerate(FRET_KEYS) if keys[k]}

    def _strum(self, now):
        held = self._held()
        for g in self.groups[self.next_idx:self.next_idx + 6]:
            if all(n.hit or n.missed for n in g):
                continue
            dt = g[0].t - now
            if dt > WINDOWS[-1][0]:
                break
            if abs(dt) <= WINDOWS[-1][0]:
                lanes = {n.lane for n in g}
                # guitar rules: chord frets held, and nothing held above the top note
                # (lower frets may stay anchored)
                if lanes <= held and max(held) == max(lanes):
                    self._judge_hit(g, abs(dt))
                    return
        self._overstrum()

    def _tap(self, lane, now):
        best = None
        for g in self.groups[self.next_idx:self.next_idx + 8]:
            dt = g[0].t - now
            if dt > WINDOWS[-1][0]:
                break
            for n in g:
                if n.lane == lane and not n.hit and not n.missed and abs(dt) <= WINDOWS[-1][0]:
                    best = n
                    break
            if best:
                break
        if best is None:
            self.lane_flash[lane] = 0.08
            return
        self._judge_hit([best], abs(best.t - now))

    def _judge_hit(self, notes, err):
        label, color, points = "GOOD", (160, 200, 255), 50
        for window, name, pts in WINDOWS:
            if err <= window:
                label, points = name, pts
                color = {"PERFECT": (255, 230, 90), "GREAT": (120, 255, 140)}.get(name, (160, 200, 255))
                break
        for n in notes:
            n.hit = True
            self.hits += 1
            self.judged += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += points * self.multiplier
            self.lane_flash[n.lane] = 0.18
            self._spark(n.lane)
            self.rock = min(1.0, self.rock + 0.018)
        self.feedback.append((label, color, 0.5))

    def _overstrum(self):
        if self.combo >= 5:
            self.feedback.append(("OVERSTRUM", (255, 90, 90), 0.5))
        self.combo = 0
        self.overstrums += 1
        self.rock = max(0.0, self.rock - 0.02)
        self.audio.play(self.audio.synth("overstrum", freq=110, dur=0.12, wave="saw", vol=0.25, noise=0.5))

    def _miss(self, n):
        n.missed = True
        self.judged += 1
        if self.combo >= 10:
            self.feedback.append(("COMBO BROKEN", (255, 90, 90), 0.6))
        self.combo = 0
        self.rock = max(0.0, self.rock - 0.045)

    @property
    def multiplier(self):
        return min(4, 1 + self.combo // 10)

    def _spark(self, lane):
        x = lane_x(lane, 1.0)
        for _ in range(10):
            a = random.uniform(math.pi * 1.1, math.pi * 1.9)
            v = random.uniform(120, 360)
            self.sparks.append([x, STRIKE_Y, math.cos(a) * v, math.sin(a) * v, 0.45, COLORS[lane]])

    # ------------------------------------------------------------- update
    def update(self, dt):
        super().update(dt)
        self.lane_flash = [max(0.0, f - dt) for f in self.lane_flash]
        self.feedback = [(t, c, life - dt) for t, c, life in self.feedback if life - dt > 0][-4:]
        for s in self.sparks:
            s[0] += s[2] * dt
            s[1] += s[3] * dt
            s[3] += 900 * dt
            s[4] -= dt
        self.sparks = [s for s in self.sparks if s[4] > 0]

        if self.state == "count":
            self.count_t += dt
            if self.count_t >= 3.0:
                self._begin_song()
            self.song_time = self.count_t - 3.0
            return
        if self.state == "results":
            self.results_t += dt
            return
        if self.state != "play":
            return

        self._advance_clock(dt)
        now = self.song_time - self.offset
        while self.next_idx < len(self.groups):
            g = self.groups[self.next_idx]
            if all(n.hit or n.missed for n in g):
                self.next_idx += 1
                continue
            if now - g[0].t > MISS_AFTER:
                for n in g:
                    if not n.hit:
                        self._miss(n)
                self.next_idx += 1
                continue
            break
        if now > self.end_time or (self.next_idx >= len(self.groups) and self.audio.enabled
                                    and self.song["audio"] and not pygame.mixer.music.get_busy() and now > 1):
            self._finish()

    def _finish(self):
        self.state = "results"
        self.results_t = 0.0
        total = max(1, len(self.notes))
        self.accuracy = self.hits / total
        self.passed = self.accuracy >= PASS_ACCURACY
        self.audio.blip("win" if self.passed else "die")
        if self.audio.enabled:
            pygame.mixer.music.fadeout(1500)

    def skip(self):
        if self.audio.enabled:
            pygame.mixer.music.stop()
        self.app.story.complete()

    # ------------------------------------------------------------- draw
    def draw(self, surf):
        self._draw_stage(surf)
        self._draw_highway(surf)
        self._draw_hud(surf)
        if self.state == "intro":
            self._draw_intro(surf)
        elif self.state == "count":
            n = 3 - int(self.count_t)
            if n > 0:
                ui.draw_text(surf, str(n), 64, (W // 2, 190), WHITE, "midtop", shadow=BLACK)
        elif self.state == "results":
            self._draw_results(surf)

    def _draw_stage(self, surf):
        surf.fill((8, 4, 14))
        # gradient backdrop
        for i in range(0, H, 6):
            k = i / H
            pygame.draw.rect(surf, (int(20 + 30 * k), int(6 + 8 * k), int(36 + 20 * (1 - k))), (0, i, W, 6))
        # sweeping spotlights
        beam = pygame.Surface((W, H), pygame.SRCALPHA)
        energy = 0.4 + 0.6 * self.rock
        for i, ph in enumerate(self.lights):
            ang = math.sin(self.t * (0.6 + i * 0.13) + ph) * 0.5
            base = (120 + i * 240, -10)
            tip_x = base[0] + math.sin(ang) * 600
            col = [(255, 80, 200), (80, 200, 255), (255, 220, 80), (140, 255, 120)][i]
            pygame.draw.polygon(beam, (*col, int(26 * energy)), [base, (tip_x - 90, H), (tip_x + 90, H)])
        surf.blit(beam, (0, 0))
        # crowd silhouettes bopping with the combo
        bounce = min(1.0, self.combo / 20)
        for i, r in enumerate(self.crowd):
            x = i * (W / len(self.crowd)) + 10
            hop = abs(math.sin(self.t * 6 + r * 6)) * 10 * bounce
            y = H - 30 - r * 18 - hop
            pygame.draw.circle(surf, (14, 8, 22), (int(x), int(y)), 11)
            pygame.draw.rect(surf, (14, 8, 22), (int(x - 13), int(y + 8), 26, 40))

    def _draw_highway(self, surf):
        far_s, far_y = project(1.0)
        half = LANE_GAP * 2.5
        poly = [(CX - half, STRIKE_Y + 40), (CX + half, STRIKE_Y + 40),
                (CX + half * far_s, far_y), (CX - half * far_s, far_y)]
        hw = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(hw, (10, 10, 16, 215), poly)
        # beat lines scrolling
        if self.song["notes"]:
            spb = 60 / self.song.get("bpm", 140)
            origin = self.song.get("first_beat", 0.0)
            now = self.song_time - self.offset - origin
            first = math.floor(now / spb)
            for b in range(first, first + int(LOOKAHEAD / spb) + 2):
                z = (b * spb - now) / LOOKAHEAD
                if 0 <= z <= 1:
                    s, y = project(z)
                    pygame.draw.line(hw, (60, 60, 80, 160), (CX - half * s, y), (CX + half * s, y), 1)
        for i in range(LANES + 1):
            x0 = CX + (i - 2.5) * LANE_GAP
            x1 = CX + (i - 2.5) * LANE_GAP * far_s
            pygame.draw.line(hw, (70, 70, 95, 200), (x0, STRIKE_Y + 40), (x1, far_y), 2)
        surf.blit(hw, (0, 0))
        pygame.draw.polygon(surf, (120, 110, 150), poly, 2)

        # fret buttons
        held = self._held() if self.state in ("play", "count", "intro") else set()
        for i in range(LANES):
            x = lane_x(i, 1.0)
            col = COLORS[i]
            pressed = i in held
            ring = tuple(min(255, c + 80) for c in col) if pressed else tuple(c // 2 for c in col)
            pygame.draw.circle(surf, (20, 20, 26), (int(x), STRIKE_Y), 30)
            pygame.draw.circle(surf, ring, (int(x), STRIKE_Y), 30, 5)
            if pressed:
                pygame.draw.circle(surf, col, (int(x), STRIKE_Y), 18)
            if self.lane_flash[i] > 0:
                glow = pygame.Surface((100, 100), pygame.SRCALPHA)
                a = int(255 * self.lane_flash[i] / 0.18)
                pygame.draw.circle(glow, (*col, min(160, a)), (50, 50), 42)
                surf.blit(glow, (x - 50, STRIKE_Y - 50), special_flags=pygame.BLEND_RGBA_ADD)
            ui.draw_text(surf, LABELS[i], 10, (int(x), STRIKE_Y + 38), (180, 180, 200), "midtop")

        # notes (far first)
        now = self.song_time - self.offset
        visible = []
        for g in self.groups[max(0, self.next_idx - 2):]:
            dt = g[0].t - now
            if dt > LOOKAHEAD:
                break
            for n in g:
                if not n.hit and dt > -0.2:
                    visible.append((dt, n))
        for dt, n in sorted(visible, key=lambda v: -v[0]):
            z = max(-0.1, dt / LOOKAHEAD)
            s, y = project(max(0.0, z))
            if z < 0:
                y = STRIKE_Y - z * 300
            x = lane_x(n.lane, s)
            r = max(4, int(24 * s))
            col = COLORS[n.lane] if not n.missed else (70, 70, 70)
            pygame.draw.ellipse(surf, (0, 0, 0), (x - r, y - r * 0.6 + 4, r * 2, r * 1.3))
            pygame.draw.ellipse(surf, col, (x - r, y - r * 0.6, r * 2, r * 1.2))
            pygame.draw.ellipse(surf, (255, 255, 255), (x - r * 0.55, y - r * 0.45, r * 1.1, r * 0.5), max(1, r // 8))
        for x, y, _vx, _vy, life, col in self.sparks:
            pygame.draw.rect(surf, col, (int(x), int(y), 4, 4))

    def _draw_hud(self, surf):
        ui.draw_text(surf, f"{self.score:,}", 20, (W - 20, 18), WHITE, "topright", shadow=BLACK)
        mult = self.multiplier
        ui.draw_text(surf, f"x{mult}", 16, (W - 20, 48), [WHITE, (120, 255, 140), (255, 230, 90), (255, 120, 255)][mult - 1], "topright", shadow=BLACK)
        if self.combo >= 5:
            ui.draw_text(surf, f"{self.combo} COMBO", 10, (W - 20, 74), (220, 220, 240), "topright", shadow=BLACK)
        # rock meter
        x, y, w, h = 20, 20, 24, 200
        pygame.draw.rect(surf, (20, 20, 30), (x, y, w, h))
        fill = int(h * self.rock)
        col = (220, 50, 50) if self.rock < 0.3 else (240, 210, 50) if self.rock < 0.6 else (60, 220, 80)
        pygame.draw.rect(surf, col, (x + 3, y + h - fill + 3, w - 6, max(0, fill - 6)))
        pygame.draw.rect(surf, (200, 200, 220), (x, y, w, h), 2)
        ui.draw_text(surf, "ROCK", 8, (x + w // 2, y + h + 6), (200, 200, 220), "midtop")
        # song progress
        if self.notes:
            prog = max(0.0, min(1.0, (self.song_time - self.offset) / self.end_time))
            pygame.draw.rect(surf, (40, 40, 60), (CX - 200, 12, 400, 6))
            pygame.draw.rect(surf, NEON, (CX - 200, 12, int(400 * prog), 6))
        ui.draw_text(surf, f"{self.song['title']}", 8, (CX, 24), (200, 200, 220), "midtop", shadow=BLACK)
        # judgement popups
        for i, (text, col, life) in enumerate(reversed(self.feedback)):
            a = int(255 * min(1.0, life * 4))
            ui.draw_text(surf, text, 14 if i == 0 else 10, (CX, STRIKE_Y - 110 - i * 22), col, "midtop", shadow=BLACK, alpha=a)

    def _draw_intro(self, surf):
        ui.panel(surf, (W // 2 - 300, 110, 600, 300), fill=(8, 6, 14), border=(160, 120, 255))
        ui.draw_text(surf, "TURN AND COUGH", 24, (W // 2, 132), (255, 230, 120), "midtop", shadow=BLACK)
        ui.draw_text(surf, f"{self.song['title']} - {self.song['artist']}", 10, (W // 2, 172), WHITE, "midtop")
        if not self.song["notes"]:
            ui.draw_text(surf, "NO SONG FOUND IN assets/rhythm/", 10, (W // 2, 220), (255, 120, 120), "midtop")
            return
        mode = "TAP: PRESS Z X C V B ON THE BEAT" if self.tap_mode else "STRUM: HOLD Z X C V B, STRUM WITH SPACE"
        ui.draw_text(surf, mode, 10, (W // 2, 210), (180, 255, 180), "midtop")
        ui.draw_text(surf, f"HIT {int(PASS_ACCURACY * 100)}% OF THE NOTES TO MOVE ON", 10, (W // 2, 240), WHITE, "midtop")
        ui.draw_text(surf, f"{len(self.notes)} NOTES", 8, (W // 2, 264), (180, 180, 200), "midtop")
        ui.draw_text(surf, "TAB  SWITCH STRUM / TAP MODE", 8, (W // 2, 304), (180, 180, 200), "midtop")
        ui.draw_text(surf, f"[ ]  AUDIO OFFSET ({int(round(self.offset * 1000)):+d}MS)", 8, (W // 2, 322), (180, 180, 200), "midtop")
        if ui.blink(self.t):
            ui.draw_text(surf, "PRESS ENTER TO ROCK", 12, (W // 2, 362), (255, 230, 120), "midtop")

    def _draw_results(self, surf):
        ui.panel(surf, (W // 2 - 300, 100, 600, 320), fill=(8, 6, 14), border=(160, 120, 255))
        acc = self.accuracy
        grade = "S" if acc >= 0.95 else "A" if acc >= 0.85 else "B" if acc >= 0.75 else "C" if acc >= PASS_ACCURACY else "F"
        ui.draw_text(surf, grade, 56, (W // 2 + 200, 130), (255, 230, 120) if grade != "F" else (255, 80, 80), "midtop", shadow=BLACK)
        ui.draw_text(surf, f"SCORE     {self.score:,}", 12, (W // 2 - 260, 140), WHITE)
        ui.draw_text(surf, f"ACCURACY  {acc * 100:.1f}%", 12, (W // 2 - 260, 168), WHITE)
        ui.draw_text(surf, f"NOTES     {self.hits}/{len(self.notes)}", 12, (W // 2 - 260, 196), WHITE)
        ui.draw_text(surf, f"MAX COMBO {self.max_combo}", 12, (W // 2 - 260, 224), WHITE)
        if self.passed:
            ui.draw_text(surf, "WELL DONE! YOU ARE A", 16, (W // 2, 284), (255, 80, 80), "midtop", shadow=BLACK)
            ui.draw_text(surf, "TRUE TURN AND COUGHER", 16, (W // 2, 310), (255, 80, 80), "midtop", shadow=BLACK)
            prompt = "PRESS ENTER TO CONTINUE"
        else:
            ui.draw_text(surf, f"NICE TRY. HIT {int(PASS_ACCURACY * 100)}% TO MOVE ON", 14, (W // 2, 290), (255, 220, 80), "midtop", shadow=BLACK)
            prompt = "PRESS ENTER TO TRY AGAIN"
        if self.results_t > 1.0 and ui.blink(self.t):
            ui.draw_text(surf, prompt, 10, (W // 2, 380), WHITE, "midtop")
