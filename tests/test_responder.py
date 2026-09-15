"""The dispatcher is the part most likely to break when data is edited.

These tests assert on the *route* that answered, not on the exact sentence —
the sentences are random choices from the data file and are allowed to change.
"""

import re

import pytest

from speak2me.bot import Bot
from speak2me.data import PATTERNS


@pytest.fixture
def bot():
    return Bot(user="tester")


def route(bot, question):
    _reply, meta = bot.responder.dispatch(question)
    return meta["route"]


def test_country_question_beats_the_pattern_table(bot):
    assert route(bot, "capital of Peru") == "country"


def test_greeting_hits_the_pattern_table(bot):
    assert route(bot, "hello") == "pattern"


def test_bare_arithmetic_is_answered_without_a_pattern(bot):
    reply, meta = bot.responder.dispatch("12*12")
    assert meta["route"] == "arithmetic"
    assert "144" in reply


def test_nonsense_falls_through_to_a_default(bot):
    assert route(bot, "qwertyuiop zxcvbn") == "default"


def test_empty_input_produces_no_reply(bot):
    reply, meta = bot.responder.dispatch("   ")
    assert reply is None
    assert meta["route"] == "empty"


def test_nickname_keeps_the_users_capitalisation(bot):
    reply, _ = bot.responder.dispatch("my nickname is Rud")
    assert "Rud" in reply
    assert bot.nickname == "Rud"
    assert bot.name == "Rud"


def test_placeholder_that_calculates_is_resolved(bot):
    reply, meta = bot.responder.dispatch("calculate 3*7 and 8-1")
    assert meta["route"] == "pattern"
    assert "21" in reply and "7" in reply


def test_no_unresolved_placeholder_leaks_into_a_reply(bot):
    """Every {name} in the data file must have a callback behind it."""
    unmapped = []
    for pattern, responses in PATTERNS.items():
        for template in responses:
            for name in re.findall(r"\{(\w+)\}", template):
                if name not in bot.callbacks:
                    unmapped.append((pattern, name))
    assert unmapped == []


def test_code_execution_is_off_by_default(bot):
    reply, meta = bot.responder.dispatch(":1+1")
    assert meta["blocked"] is True
    assert "2" not in reply


def test_code_execution_runs_when_explicitly_enabled():
    bot = Bot(user="tester", allow_code_execution=True)
    reply, meta = bot.responder.dispatch(":1+1")
    assert meta["route"] == "eval"
    assert reply == "2"


def test_exec_route_reports_errors_as_speech():
    bot = Bot(user="tester", allow_code_execution=True)
    reply, meta = bot.responder.dispatch("!nope")
    assert meta["route"] == "exec"
    assert "nope" in reply


def test_llm_route_says_so_when_no_token_is_configured(bot, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    reply, meta = bot.responder.dispatch("?what is recursion")
    assert meta["configured"] is False
    assert "HF_TOKEN" in reply


def test_every_pattern_is_reachable():
    """A pattern listed after a greedier one can never fire. Catch that."""
    bot = Bot(user="tester")
    shadowed = []
    patterns = list(bot.patterns)
    for index, pattern in enumerate(patterns):
        # a literal sample that this pattern is meant to match
        sample = pattern.split("|")[0]
        sample = re.sub(r"\\b|\(\?:|\)|\\|\$", "", sample).strip()
        if not sample or "(" in sample or "?" in sample:
            continue
        for earlier in patterns[:index]:
            if re.search(earlier, sample, re.IGNORECASE):
                shadowed.append((pattern, earlier))
                break
    assert shadowed == []


def test_an_explicit_intent_beats_a_place_name(bot):
    """Regression: "weather in Lisbon" must not be answered with facts about
    Portugal just because Lisbon is a capital. Patterns carry intent and are
    tried before the country layer."""
    # stub the two callbacks that would otherwise reach the network, and
    # record what the pattern captured out of the sentence
    captured = {}
    bot.callbacks["meteo"] = lambda ctx: captured.setdefault("place", ctx[2].group(1))
    bot.callbacks["repos"] = lambda ctx: captured.setdefault("owner", ctx[2].group(1))

    assert route(bot, "weather in Lisbon") == "pattern"
    assert route(bot, "what time is it in Berlin") == "pattern"
    assert route(bot, "repos of torvalds") == "pattern"
    assert captured == {"place": "Lisbon", "owner": "torvalds"}


def test_a_bare_place_name_still_reaches_the_country_layer(bot):
    assert route(bot, "tell me about Japan") == "country"
    assert route(bot, "capital of Peru") == "country"
