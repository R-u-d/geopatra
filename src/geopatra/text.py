"""Pure string helpers. No I/O, no GUI, no network — safe to import anywhere."""

from __future__ import annotations

import difflib
import string
from datetime import datetime

_PUNCTUATION = str.maketrans("", "", string.punctuation)


def normalize(text: str) -> str:
    """Lowercase, strip surrounding whitespace, drop punctuation."""
    return text.strip().lower().translate(_PUNCTUATION)


def fuzzy_contains(word: str, text: str, cutoff: float = 0.8) -> bool:
    """True if any token in `text` is close enough to `word`.

    Lets "whats the langiuage of Peru" still hit the `language` keyword.
    The cutoff is difflib's similarity ratio; 0.8 tolerates roughly one
    typo in a five-letter word and two in a ten-letter word.
    """
    return any(
        difflib.get_close_matches(token, [word], n=1, cutoff=cutoff)
        for token in text.split()
    )


def date_and_time(fmt: str = "%a %d %b %Y, %H:%M") -> str:
    return datetime.now().strftime(fmt)


def extract_expressions(user_input: str) -> list[str]:
    """Pull arithmetic expressions out of free text.

    "whats 2+2 and also 10 * 5?" -> ["2+2", "10 * 5"]

    Scans for a run of digits, operators and brackets. Anything else ends
    the current run. Only these characters are ever collected, which is what
    keeps `evaluate_expressions` from seeing arbitrary Python.
    """
    starters = set("(-+.")
    body = set("-+/*% ()")
    expressions: list[str] = []
    start: int | None = None

    for i, char in enumerate(user_input):
        is_math = char.isdigit() or char in body
        if start is None:
            if char.isdigit() or char in starters:
                start = i
            continue
        if not is_math:
            expressions.append(user_input[start:i])
            start = None
        elif i == len(user_input) - 1:
            expressions.append(user_input[start:])
            start = None

    return [e.strip() for e in expressions if any(c.isdigit() for c in e)]


class LazyFormat(dict):
    """Resolve {placeholders} through a callback map, on first use only.

    A response template like "It is {time}" does not carry a value, it carries
    a *name*. The name is looked up in `callbacks` and the callback is invoked
    with the match context. That is what lets a template do something —
    `{quit}` closes the app, `{meteo}` hits the weather API — instead of only
    substituting text.

    Unknown names render as "<name?>" rather than raising, so a typo in the
    data file shows up in the chat window instead of crashing the bot.
    """

    def __init__(self, context, callbacks):
        super().__init__()
        self._context = context
        self._callbacks = callbacks

    def __missing__(self, key):
        if key not in self._callbacks:
            return f"<{key}?>"
        value = self._callbacks[key](self._context)
        self[key] = value
        return value


def render(template: str, context, callbacks: dict) -> str:
    """Fill {placeholders} in `template` using `callbacks`."""
    return template.format_map(LazyFormat(context, callbacks))
