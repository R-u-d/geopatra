"""Ping-pong iteration, kept separate from the animation code on purpose.

`avatar.py` needs Tkinter, OpenCV and Pillow. This class needs none of them,
and it is the piece with an off-by-one worth testing — so it lives where the
test suite can reach it on a machine with no display.
"""

from __future__ import annotations


class BounceCycle:
    """Ping-pong iterator that counts completed round trips.

    One cycle = first frame -> last frame -> first frame. The count is what the
    animator uses to find a safe moment to switch clips: swapping at a boundary
    looks intentional, swapping mid-motion looks like a dropped frame.
    """

    def __init__(self, items) -> None:
        self.items = list(items)
        if len(self.items) < 2:
            raise ValueError("BounceCycle needs at least two frames")
        self.index = 0
        self.step = 1
        self.cycles = 0

    def __iter__(self):
        return self

    def __next__(self):
        value = self.items[self.index]
        if self.index == 0:
            self.step = 1
        elif self.index == len(self.items) - 1:
            self.step = -1
        self.index += self.step
        if self.index == 0 and self.step == -1:
            self.cycles += 1
        return value

    def restart(self) -> None:
        self.index, self.step, self.cycles = 0, 1, 0
