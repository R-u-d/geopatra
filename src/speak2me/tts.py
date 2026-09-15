"""Text-to-speech, and the speaking/silent signal the avatar animates to.

The naive way to animate a talking avatar is a timer: guess how long the
sentence takes, animate for that long. It desynchronises immediately, because
the engine's rate depends on the text, the voice and the platform.

Instead the engine is driven in non-blocking mode (`startLoop(False)` plus a
manual `iterate()`), polled from the Tk main loop, and the *edge* of
`engine.isBusy()` is turned into a Tk virtual event. The avatar then reacts to
the voice actually starting and stopping. Nothing is estimated.

Polling at 50 ms is well under a syllable, so the switch is not perceptible.
"""

from __future__ import annotations

import contextlib
import tkinter as tk

import pyttsx3

from .avatar import EVENT_SILENT, EVENT_SPEAKING

POLL_MS = 50


class Speaker:
    def __init__(self, root: tk.Tk, rate: int = 180, volume: float = 0.6) -> None:
        self.root = root
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self._speaking = False
        self._stopped = False

        # non-blocking: we own the iteration, so Tk keeps repainting while
        # the voice runs
        self.engine.startLoop(False)
        self._poll()

    def _poll(self) -> None:
        if self._stopped:
            return
        busy = self.engine.isBusy()
        if busy and not self._speaking:
            self._speaking = True
            self.root.event_generate(EVENT_SPEAKING)
        elif not busy and self._speaking:
            self._speaking = False
            self.root.event_generate(EVENT_SILENT)

        # the engine can be torn down while a poll is in flight
        with contextlib.suppress(RuntimeError):
            self.engine.iterate()

        self.root.after(POLL_MS, self._poll)

    def say(self, text: str, interrupt: bool = True) -> None:
        if not text.strip():
            return
        if interrupt:
            self.engine.stop()
        self.engine.say(text)

    def shutdown(self) -> None:
        self._stopped = True
        with contextlib.suppress(RuntimeError):
            self.engine.stop()
            self.engine.endLoop()
