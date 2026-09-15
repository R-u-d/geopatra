"""The animated avatar.

The avatar is not a sprite sheet — it is a folder of short MP4 clips. Each clip
is decoded once at startup into a list of Tk images, and playback is a `after()`
loop on the Tk canvas at 30 fps.

Two things make it read as lip-sync without any lip-sync:

1. Clips are played *ping-pong* (`BounceCycle`), so a two-second clip loops
   forever without a visible cut back to frame one.
2. The clip set is swapped on the speaking/silent edge, and the swap only
   happens at a cycle boundary, so it never cuts mid-motion. The edge comes
   from the TTS engine, not from a timer — see `tts.py`.

A mood queue sits on top: a response template containing `{joke}` pushes a
mood key, and the next boundary plays that clip instead of a random one.
"""

from __future__ import annotations

import random
import tkinter as tk
from collections import deque
from pathlib import Path

import cv2
from PIL import Image, ImageTk

from .cycle import BounceCycle

# Tk virtual events. The TTS thread generates them; the animator listens.
EVENT_SPEAKING = "<<speaking>>"
EVENT_SILENT = "<<silent>>"
EVENT_BUSY = "<<busy>>"
EVENT_IDLE = "<<idle>>"
EVENT_QUIT = "<<quit>>"

FPS = 30


def load_frames(path: Path, size: tuple[int, int], crop: tuple[float, float, float, float]):
    """Decode an MP4 into PIL images.

    OpenCV hands back frames in BGR order; feeding those straight to PIL swaps
    red and blue. This footage is nearly monochrome, so the earlier version got
    away with it — the mean channel difference is about eight levels — but it
    was wrong and would be obvious on any colourful clip.

    `crop` is relative (0..1) so the same numbers work at any render size. The
    default trims the bottom tenth, which is where the generator watermark sits.
    """
    capture = cv2.VideoCapture(str(path))
    frames: list[Image.Image] = []
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if all(size):
                image = image.resize(size)
            if any(crop):
                width, height = image.size
                box = tuple(
                    int(dim * factor)
                    for dim, factor in zip((width, height, width, height), crop, strict=True)
                )
                image = image.crop(box)
            frames.append(image)
    finally:
        capture.release()
    return frames


class Clip:
    """One decoded animation, ready for the canvas."""

    def __init__(self, name: str, images: list[Image.Image]) -> None:
        self.name = name
        self.images = images
        self.photos = [ImageTk.PhotoImage(image) for image in images]
        self.frames = BounceCycle(self.photos)

    def restart(self) -> None:
        self.frames.restart()


class Animator:
    """Drives the canvas image. Owns which clip is on screen and when it changes."""

    # a clip is held for this many cycles before a new one is picked
    IDLE_CYCLES = 1
    SPEAK_CYCLES = 3

    def __init__(self, root: tk.Tk, canvas: tk.Canvas, image_id: int) -> None:
        self.root = root
        self.canvas = canvas
        self.image_id = image_id
        self.interval_ms = int(1000 / FPS)

        self.clips: dict[str, Clip] = {}
        self.idle_keys: set[str] = set()
        self.speak_keys: set[str] = set()
        self.idle: Clip | None = None
        self.speaking: Clip | None = None

        self.speaking_now = False
        self.ready = False
        self.moods: deque[str] = deque()
        self._after_id: str | None = None

        self.root.bind(EVENT_SPEAKING, self._on_speaking)
        self.root.bind(EVENT_SILENT, self._on_silent)

    # -- events ------------------------------------------------------------
    def _on_speaking(self, event=None) -> None:
        self.root.event_generate(EVENT_BUSY)
        if not self.speaking_now:
            self._pick_idle()  # choose what to return to once the voice stops
            self.speaking_now = True

    def _on_silent(self, event=None) -> None:
        self.root.event_generate(EVENT_IDLE)
        if self.speaking_now:
            self._pick_speaking()  # choose what to use for the next utterance
            self.speaking_now = False

    # -- clip management ---------------------------------------------------
    def add(self, name: str, clip: Clip) -> None:
        self.clips[name] = clip
        if self.speaking is None:
            self.speaking = clip

    def classify(
        self,
        idle_marker: str = "idle",
        speak_markers: tuple[str, ...] = ("neutral", "funny", "rap"),
    ) -> None:
        """Sort loaded clips into the idle pool and the speaking pool."""
        self.idle_keys = {name for name in self.clips if idle_marker in name}
        self.speak_keys = {
            name for name in self.clips if any(m in name for m in speak_markers)
        }

    def select(self, key: str) -> Clip | None:
        if key in self.clips:
            return self.clips[key]
        for name, clip in self.clips.items():
            if key and key in name:
                return clip
        return None

    def _pick_idle(self) -> None:
        if self.idle:
            self.idle.restart()
        pool = self.idle_keys or set(self.clips)
        if pool:
            self.idle = self.clips[random.choice(sorted(pool))]

    def _pick_speaking(self) -> None:
        if self.speaking:
            self.speaking.restart()
        pool = self.speak_keys or set(self.clips)
        if pool:
            self.speaking = self.clips[random.choice(sorted(pool))]

    def queue_mood(self, key: str) -> None:
        """Ask for a specific clip on the next utterance, e.g. the joke clip."""
        self.moods.append(key)

    def _take_mood(self) -> bool:
        while self.moods:
            clip = self.select(self.moods.popleft())
            if clip:
                self.speaking = clip
                return True
        return False

    # -- the loop ----------------------------------------------------------
    def start(self) -> None:
        self._tick()

    def stop(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _tick(self) -> None:
        if self.ready:
            if self.idle is None:
                self._pick_idle()
            if self.speaking is None:
                self._pick_speaking()

            if self.idle and self.idle.frames.cycles >= self.IDLE_CYCLES:
                self._pick_idle()
            if not self._take_mood() and self.speaking and (
                self.speaking.frames.cycles >= self.SPEAK_CYCLES
            ):
                self._pick_speaking()

            current = self.speaking if self.speaking_now else self.idle
            if current:
                self.canvas.itemconfig(self.image_id, image=next(current.frames))

        self._after_id = self.root.after(self.interval_ms, self._tick)
