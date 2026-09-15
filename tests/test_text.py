import pytest

from speak2me import text


def test_normalize_strips_case_and_punctuation():
    assert text.normalize("  What's THIS?! ") == "whats this"


@pytest.mark.parametrize("typo", ["language", "langauge", "langiuage", "languag"])
def test_fuzzy_contains_tolerates_typos(typo):
    assert text.fuzzy_contains("language", f"whats the {typo} of peru")


def test_fuzzy_contains_rejects_a_different_word():
    assert not text.fuzzy_contains("language", "whats the capital of peru")


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        ("2+2", ["2+2"]),
        ("whats 2+2", ["2+2"]),
        ("calculate 3*7 and 8-1", ["3*7", "8-1"]),
        ("(2+3)*4 please", ["(2+3)*4"]),
        ("no numbers here", []),
    ],
)
def test_extract_expressions(sentence, expected):
    assert text.extract_expressions(sentence) == expected


def test_extract_expressions_never_yields_names_or_calls():
    # this is the safety property that makes eval on the result acceptable
    for sentence in ("__import__('os') + 1", "open('x').read() 2", "1 + abc"):
        for expression in text.extract_expressions(sentence):
            assert all(c.isdigit() or c in "+-*/%(). " for c in expression), expression


def test_render_resolves_placeholders_through_callbacks():
    calls = []

    def clock(context):
        calls.append(context)
        return "12:00"

    result = text.render("It is {time}", ("It is {time}", "p", None), {"time": clock})
    assert result == "It is 12:00"
    assert len(calls) == 1


def test_render_calls_each_callback_once():
    counter = iter(range(10))
    result = text.render("{n} and {n}", ("", "", None), {"n": lambda ctx: next(counter)})
    assert result == "0 and 0"


def test_render_marks_unknown_placeholders_instead_of_crashing():
    assert text.render("hi {nope}", ("", "", None), {}) == "hi <nope?>"
