"""Music + sound effects with global volume control, plus a tiny synth for UI blips."""
import array
import math
import os
import random

import pygame

from .config import asset


class Audio:
    def __init__(self, save):
        self.save = save
        self.current = None
        self.enabled = pygame.mixer.get_init() is not None
        self._cache = {}
        self._synth_cache = {}
        if self.enabled:
            pygame.mixer.set_num_channels(24)

    # ---------------------------------------------------------------- music
    def music(self, path, loop=True, fade_ms=600, start=0.0, restart=False):
        """Play a music file (path relative to assets/). No-op if already playing."""
        if not self.enabled:
            return
        if path == self.current and not restart and pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(asset(path) if not os.path.isabs(path) else path)
            pygame.mixer.music.set_volume(self.save["music_volume"])
            pygame.mixer.music.play(-1 if loop else 0, start=start, fade_ms=fade_ms)
            self.current = path
        except pygame.error as e:
            print(f"[audio] could not play {path}: {e}")
            self.current = None

    def stop_music(self, fade_ms=500):
        if not self.enabled:
            return
        if fade_ms:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self.current = None

    def apply_volume(self):
        if self.enabled:
            pygame.mixer.music.set_volume(self.save["music_volume"])

    # ---------------------------------------------------------------- sfx
    def load(self, path):
        if not self.enabled:
            return None
        snd = self._cache.get(path)
        if snd is None:
            try:
                snd = pygame.mixer.Sound(asset(path))
            except (pygame.error, FileNotFoundError) as e:
                print(f"[audio] could not load {path}: {e}")
                snd = False
            self._cache[path] = snd
        return snd or None

    def sfx(self, path, volume=1.0):
        snd = self.load(path)
        if snd:
            snd.set_volume(volume * self.save["sfx_volume"])
            snd.play()

    def play(self, sound, volume=1.0):
        """Play an already-built Sound (e.g. from synth())."""
        if sound:
            sound.set_volume(volume * self.save["sfx_volume"])
            sound.play()

    def stop_all(self):
        if self.enabled:
            pygame.mixer.stop()

    # ---------------------------------------------------------------- synth
    def synth(self, key, freq=440.0, dur=0.08, wave="square", vol=0.4,
              slide=0.0, attack=0.004, decay=None, noise=0.0):
        """Generate (and cache) a short procedural sound."""
        if not self.enabled:
            return None
        if key in self._synth_cache:
            return self._synth_cache[key]
        rate, _fmt, channels = pygame.mixer.get_init()
        n = int(rate * dur)
        decay = dur if decay is None else decay
        buf = array.array("h")
        phase = 0.0
        rng = random.Random(hash(key) & 0xFFFF)
        for i in range(n):
            t = i / rate
            f = freq + slide * t / dur
            phase += f / rate
            p = phase % 1.0
            if wave == "square":
                s = 1.0 if p < 0.5 else -1.0
            elif wave == "tri":
                s = 4 * abs(p - 0.5) - 1
            elif wave == "saw":
                s = 2 * p - 1
            else:
                s = math.sin(2 * math.pi * p)
            if noise:
                s = s * (1 - noise) + (rng.random() * 2 - 1) * noise
            env = min(1.0, t / attack) if attack else 1.0
            env *= max(0.0, 1.0 - t / decay)
            v = int(max(-1.0, min(1.0, s * env * vol)) * 32767)
            for _ in range(channels):
                buf.append(v)
        snd = pygame.mixer.Sound(buffer=buf.tobytes())
        self._synth_cache[key] = snd
        return snd

    def blip(self, kind="type"):
        presets = {
            "type": dict(freq=880, dur=0.03, wave="square", vol=0.12),
            "select": dict(freq=660, dur=0.07, wave="square", vol=0.25, slide=440),
            "move": dict(freq=440, dur=0.04, wave="tri", vol=0.25),
            "back": dict(freq=520, dur=0.08, wave="square", vol=0.2, slide=-260),
            "eat": dict(freq=520, dur=0.09, wave="square", vol=0.3, slide=520),
            "die": dict(freq=300, dur=0.5, wave="saw", vol=0.3, slide=-250),
            "win": dict(freq=520, dur=0.4, wave="square", vol=0.25, slide=780),
            "hit": dict(freq=160, dur=0.12, wave="square", vol=0.35, slide=-80, noise=0.5),
            "hurt": dict(freq=240, dur=0.25, wave="saw", vol=0.35, slide=-160, noise=0.2),
            "jump": dict(freq=300, dur=0.12, wave="square", vol=0.18, slide=300),
            "swing": dict(freq=900, dur=0.09, wave="sine", vol=0.25, slide=-600, noise=0.6),
            "coin": dict(freq=988, dur=0.12, wave="square", vol=0.2, slide=330),
            "heal": dict(freq=600, dur=0.3, wave="tri", vol=0.3, slide=600),
            "boom": dict(freq=90, dur=0.5, wave="sine", vol=0.6, slide=-60, noise=0.7),
            "checkpoint": dict(freq=700, dur=0.25, wave="tri", vol=0.3, slide=700),
            "drone": dict(freq=55, dur=1.6, wave="saw", vol=0.12, attack=0.4, noise=0.15),
        }
        self.play(self.synth("blip:" + kind, **presets[kind]))
