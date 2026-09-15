from geopatra import countries
from geopatra.data import COUNTRIES

SAMPLE = {
    "Peru": {"capital": "Lima", "currency": "Nuevo Sol", "language": "Spanish"},
    "Niger": {"capital": "Niamey", "currency": "CFA Franc", "language": "French"},
    "Nigeria": {"capital": "Abuja", "currency": "Naira", "language": "English"},
    "South Africa": {
        "capital": "Pretoria",
        "currency": "Rand",
        "language": "Afrikaans_English_Zulu",
    },
}


def test_focused_answer_per_aspect():
    assert countries.answer("whats the capital of Peru", SAMPLE) == "The capital of Peru is Lima."
    assert countries.answer("currency of Peru?", SAMPLE) == "The currency of Peru is Nuevo Sol."
    assert countries.answer("language in Peru", SAMPLE) == "The language spoken in Peru is Spanish."


def test_typo_in_aspect_still_resolves():
    # the whole point of the fuzzy matcher
    assert countries.answer("whats the langiuage of Peru", SAMPLE) == (
        "The language spoken in Peru is Spanish."
    )


def test_longest_country_name_wins():
    # "Niger" is a substring of "Nigeria"; the longer name must win
    assert "Abuja" in countries.answer("capital of Nigeria", SAMPLE)
    assert "Niamey" in countries.answer("capital of Niger", SAMPLE)
    # and a two-word country is not answered as one of its words
    assert "Pretoria" in countries.answer("capital of South Africa", SAMPLE)


def test_capital_resolves_back_to_country():
    reply = countries.answer("which country has Lima", SAMPLE)
    assert reply is not None and reply.startswith("Peru:")


def test_country_alone_returns_every_fact():
    reply = countries.answer("tell me about Peru", SAMPLE)
    assert "Lima" in reply and "Nuevo Sol" in reply and "Spanish" in reply


def test_multiple_languages_are_read_as_a_list():
    reply = countries.answer("language of South Africa", SAMPLE)
    assert reply == "The language spoken in South Africa is Afrikaans, English and Zulu."


def test_currency_maps_back_to_its_countries():
    reply = countries.answer("who pays in Rand", SAMPLE)
    assert reply is not None and "South Africa" in reply


def test_unrelated_input_is_not_answered_here():
    assert countries.answer("tell me a joke", SAMPLE) is None
    assert countries.answer("", SAMPLE) is None


def test_substring_of_a_word_is_not_a_country():
    # "Chad" must not be found inside "Chadwick"
    data = {"Chad": {"capital": "N'Djamena", "currency": "CFA Franc", "language": "French"}}
    assert countries.answer("who is Chadwick", data) is None


def test_real_dataset_is_complete():
    assert len(COUNTRIES) == 195
    for name, facts in COUNTRIES.items():
        assert facts.get("capital"), name
        assert facts.get("currency"), name
        assert facts.get("language"), name
