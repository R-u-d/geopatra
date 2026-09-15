"""The original acceptance list, run against the finished bot.

`docs/keywords-original.txt` was written on day two of the project: 26 example
questions the bot was supposed to handle, in the phrasings a person would
actually use. It is the closest thing the assignment had to a specification, so
it is worth keeping executable rather than letting it rot in a text file.

Three of the 26 — the "which country speaks X" shape — were never answered by
the original. They are answered now.
"""

from pathlib import Path

import pytest

from geopatra.bot import Bot

SPEC = Path(__file__).resolve().parents[1] / "docs" / "keywords-original.txt"


def acceptance_questions() -> list[str]:
    """The two question blocks at the top of the spec, before the notes."""
    lines = SPEC.read_text(encoding="utf-8").splitlines()[:36]
    return [
        line.strip()
        for line in lines
        if line.strip().endswith(("?", ".")) and not line.startswith("#")
    ]


def test_the_spec_file_is_still_there_and_still_has_26_questions():
    assert len(acceptance_questions()) == 26


@pytest.mark.parametrize("question", acceptance_questions())
def test_every_acceptance_question_reaches_the_country_layer(question):
    bot = Bot()
    reply, meta = bot.responder.dispatch(question)
    assert meta["route"] == "country", f"{question!r} fell through to {meta['route']}"
    assert reply
