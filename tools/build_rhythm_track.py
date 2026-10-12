"""Compose the bundled rhythm-chapter track ("Cough Syrup") and its note chart.

Everything is synthesised here from scratch (no samples), so the track is
original and the chart lines up with the melody exactly: lanes 0-4 are the
A-minor pentatonic notes A C D E G, so the frets you press are the notes you hear.

    python tools/build_rhythm_track.py      (needs ffmpeg on PATH for the .ogg)

Writes assets/rhythm/cough_syrup.ogg and assets/rhythm/cough_syrup.json.
"""
import array
import json
import math
import os
import random
import shutil
import subprocess
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "rhythm")
RATE = 22050
BPM = 140
BEAT = 60 / BPM
BAR = BEAT * 4
EIGHTH = BEAT / 2
LEAD_IN = 1.0

LANE_FREQ = [440.0, 523.25, 587.33, 659.25, 783.99]      # A4 C5 D5 E5 G5
CHORD_ROOT = {"Am": 110.0, "F": 87.31, "C": 130.81, "G": 98.0}
CHORD_PAD = {"Am": [220.0, 261.63, 329.63], "F": [174.61, 220.0, 261.63],
             "C": [261.63, 329.63, 392.0], "G": [196.0, 246.94, 293.66]}
PROG = ["Am", "F", "C", "G"]

rng = random.Random(1977)


class Mix:
    def __init__(self, seconds):
        self.buf = [0.0] * int(seconds * RATE)

    def add(self, start, samples):
        i0 = int(start * RATE)
        buf = self.buf
        n = min(len(samples), len(buf) - i0)
        for i in range(max(0, n)):
            buf[i0 + i] += samples[i]


def env(i, n, attack=0.005, release=0.3):
    t = i / RATE
    a = min(1.0, t / attack) if attack else 1.0
    return a * (1 - i / n) ** (1 / max(0.05, release))


def kick(vol=0.9):
    n = int(0.22 * RATE)
    out, ph = [], 0.0
    for i in range(n):
        f = 45 + 95 * math.exp(-i / (RATE * 0.03))
        ph += f / RATE
        out.append(math.sin(2 * math.pi * ph) * vol * (1 - i / n) ** 2)
    return out


def snare(vol=0.5):
    n = int(0.16 * RATE)
    out, ph = [], 0.0
    for i in range(n):
        ph += 185 / RATE
        e = (1 - i / n) ** 3
        out.append((rng.uniform(-1, 1) * 0.8 + math.sin(2 * math.pi * ph) * 0.4) * vol * e)
    return out


def hat(vol=0.07, length=0.03):
    n = int(length * RATE)
    prev = 0.0
    out = []
    for i in range(n):
        x = rng.uniform(-1, 1)
        out.append((x - prev) * vol * (1 - i / n) ** 2)   # crude high-pass
        prev = x
    return out


def tone(freq, dur, vol, wave_="square", vibrato=0.0, release=0.6, duty=0.5, cutoff=2500.0):
    n = int(dur * RATE)
    out, ph, y = [], 0.0, 0.0
    a = 1 - math.exp(-2 * math.pi * cutoff / RATE)   # one-pole low-pass
    for i in range(n):
        f = freq * (1 + vibrato * math.sin(2 * math.pi * 5.5 * i / RATE) * min(1, i / (RATE * 0.12)))
        ph += f / RATE
        p = ph % 1.0
        if wave_ == "square":
            s = 1.0 if p < duty else -1.0
        elif wave_ == "saw":
            s = 2 * p - 1
        elif wave_ == "tri":
            s = 4 * abs(p - 0.5) - 1
        else:
            s = math.sin(2 * math.pi * p)
        y += a * (s - y)
        out.append(y * vol * env(i, n, release=release))
    return out


def chord_tone(freqs, dur, vol):
    parts = [tone(f, dur, vol / len(freqs), "saw", release=1.5, cutoff=1200) for f in freqs]
    return [sum(p[i] for p in parts) for i in range(len(parts[0]))]


# ------------------------------------------------------------------ song
VERSE = [
    [0, None, 2, 3, 2, None, 0, 1],
    [1, None, 2, 1, 0, None, 1, 2],
    [2, 3, 4, 3, 2, None, 3, 2],
    [4, None, 3, 2, 1, 2, 3, None],
]
VERSE_END = [4, 3, 2, 1, 0, None, None, None]
CHORUS = {  # quarter-note dyads per chord
    "Am": [(0, 2), (0, 2), (1, 3), (0, 2)],
    "F": [(1, 3), (1, 3), (2, 4), (1, 3)],
    "C": [(2, 4), (2, 4), (1, 3), (2, 4)],
    "G": [(2, 4), (1, 3), (0, 2), (1, 3)],
}
BRIDGE = {
    "Am": [0, 1, 2, 3, 4, 3, 2, 1],
    "F": [1, 2, 3, 4, 3, 2, 1, 0],
    "C": [2, 3, 4, 3, 2, 1, 2, 3],
    "G": [4, 3, 2, 1, 0, 1, 2, 3],
}


def build():
    sections = (["intro"] * 4 + ["verse"] * 8 + ["chorus"] * 8 + ["verse"] * 8 +
                ["bridge"] * 4 + ["chorus"] * 8 + ["outro"] * 4)
    total = LEAD_IN + len(sections) * BAR + 3.0
    mix = Mix(total)
    notes = []
    k, s = kick(), snare()
    h, h_open = hat(), hat(0.1, 0.12)

    for bar_i, sec in enumerate(sections):
        t0 = LEAD_IN + bar_i * BAR
        chord = PROG[bar_i % 4]
        in_sec = sum(1 for x in sections[:bar_i] if x == sec)
        last_of_sec = bar_i + 1 >= len(sections) or sections[bar_i + 1] != sec

        # drums
        if sec != "outro" or in_sec < 3:
            for beat in range(4):
                bt = t0 + beat * BEAT
                if beat in (0, 2) or (sec in ("chorus", "bridge") and beat == 3 and in_sec % 2):
                    mix.add(bt, k)
                if beat in (1, 3) and not (sec == "intro" and bar_i < 2):
                    mix.add(bt, s)
                for e in range(2):
                    mix.add(bt + e * EIGHTH, h_open if (sec == "chorus" and e == 1) else h)
            if last_of_sec and sec != "outro":
                for e in range(4):   # snare fill into the next section
                    mix.add(t0 + 3 * BEAT + e * BEAT / 4, snare(0.35))
        else:
            mix.add(t0, k)

        # bass: driving eighths on the root
        root = CHORD_ROOT[chord]
        if sec == "outro" and in_sec == 3:
            mix.add(t0, tone(root, BAR, 0.4, "square", duty=0.3, release=2.0, cutoff=700))
        else:
            for e in range(8):
                f = root * (2 if e % 4 == 3 else 1)
                mix.add(t0 + e * EIGHTH, tone(f, EIGHTH * 0.92, 0.38, "square", duty=0.3, release=0.8, cutoff=700))

        # pads in the big sections
        if sec in ("chorus", "outro", "bridge"):
            mix.add(t0, chord_tone(CHORD_PAD[chord], BAR, 0.28))

        # lead + chart
        def lead(t, lanes, dur, vol=0.22):
            for ln in lanes:
                mix.add(t, tone(LANE_FREQ[ln], dur, vol / len(lanes) ** 0.5, "square", vibrato=0.006, duty=0.25, cutoff=3200))
                notes.append([round(t, 4), ln])

        if sec == "intro":
            if bar_i >= 2:
                for beat in range(4):
                    lead(t0 + beat * BEAT, [0 if chord == "Am" else 1], BEAT * 0.9, 0.18)
        elif sec == "verse":
            pat = VERSE[bar_i % 4]
            if last_of_sec:
                pat = VERSE_END
            for e, ln in enumerate(pat):
                if ln is not None:
                    lead(t0 + e * EIGHTH, [ln], EIGHTH * 0.95)
        elif sec == "chorus":
            for beat, dy in enumerate(CHORUS[chord]):
                lead(t0 + beat * BEAT, list(dy), BEAT * 0.95, 0.26)
        elif sec == "bridge":
            for e, ln in enumerate(BRIDGE[chord]):
                lead(t0 + e * EIGHTH, [ln], EIGHTH * 0.9)
        elif sec == "outro":
            if in_sec < 2:
                for beat, dy in enumerate(CHORUS[chord]):
                    lead(t0 + beat * BEAT, list(dy), BEAT * 0.95, 0.26)
            elif in_sec == 2:
                for e, ln in enumerate([4, 3, 2, 1, 0, 1, 2, 3]):
                    lead(t0 + e * EIGHTH, [ln], EIGHTH * 0.9)
            else:
                lead(t0, [0, 2, 4], BAR * 1.5, 0.3)

    # normalise + soft clip
    peak = max(abs(x) for x in mix.buf) or 1.0
    gain = 0.95 / peak
    pcm = array.array("h", (int(math.tanh(x * gain) * 30000) for x in mix.buf))
    return pcm, sorted(notes), total


def main():
    os.makedirs(OUT, exist_ok=True)
    pcm, notes, total = build()
    wav_path = os.path.join(OUT, "cough_syrup.wav")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    with open(os.path.join(OUT, "cough_syrup.json"), "w") as f:
        json.dump({"title": "Cough Syrup", "bpm": BPM, "length": round(total, 2), "notes": notes}, f)
    ogg = os.path.join(OUT, "cough_syrup.ogg")
    encoders = [["-c:a", "libvorbis", "-q:a", "5"],
                ["-c:a", "vorbis", "-strict", "-2", "-ac", "2", "-q:a", "5"]]   # ffmpeg's built-in encoder
    done = False
    if shutil.which("ffmpeg"):
        for args in encoders:
            res = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav_path] + args + [ogg], stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                done = True
                break
    if done:
        os.remove(wav_path)
        print("wrote", ogg)
    else:
        print("no ogg encoder found; kept", wav_path, "- convert it to cough_syrup.ogg")
    print(len(notes), "notes,", round(total, 1), "seconds")


if __name__ == "__main__":
    main()
