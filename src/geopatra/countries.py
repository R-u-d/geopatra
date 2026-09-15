"""Country lookups: the one topic the bot actually knows something about.

Four questions are answered, in this order of specificity:

1. country + aspect   "whats the currency of Peru"   -> one fact
2. capital -> country "which country has Lima"       -> the country
3. currency -> list   "who uses the Euro"            -> every country with it
4. language -> list   "where do they speak Arabic"   -> every country with it
5. country alone      "tell me about Peru"           -> every known fact

Shapes 1, 2 and 5 come from the original assignment spec in
docs/keywords-original.txt; 3 and 4 were in it too and 4 was never built. All
26 acceptance questions in that file are answered here.

Everything here is pure: dicts in, string out. That is deliberate — it is
the part of the bot worth testing, so it must not need a window or a network.
"""

from __future__ import annotations

from .text import fuzzy_contains, normalize

# aspect -> (data key, sentence template)
ASPECTS: dict[str, tuple[str, str]] = {
    "capital": ("capital", "The capital of {country} is {value}."),
    "currency": ("currency", "The currency of {country} is {value}."),
    "language": ("language", "The language spoken in {country} is {value}."),
}

Countries = dict[str, dict[str, str]]

# a spoken list longer than this is unbearable to listen to
MAX_LISTED = 12


def _readable(raw: str) -> str:
    """The data file joins multiple values with '_'. Make that speakable.

    Applies to languages ("Afrikaans_English_Zulu") and to the handful of
    countries with more than one currency ("Euro_CFP Franc").
    """
    parts = [p.strip() for p in raw.split("_") if p.strip()]
    if len(parts) <= 1:
        return raw
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def _mentions(needle: str, text: str) -> bool:
    """Whole-token containment of a possibly multi-word name."""
    needle = normalize(needle)
    return bool(needle) and f" {needle} " in f" {text} "


def find_country(text: str, countries: Countries) -> tuple[str, dict[str, str]] | None:
    """Match a country by its own name or by its capital.

    Returns the *longest* match, so "South Africa" is not answered as
    "Africa" and "Niger" does not swallow "Nigeria".
    """
    norm = normalize(text)
    best: tuple[str, dict[str, str]] | None = None
    best_len = 0

    for name, facts in countries.items():
        for candidate in (name, facts.get("capital", "")):
            if _mentions(candidate, norm) and len(candidate) > best_len:
                best, best_len = (name, facts), len(candidate)

    return best


def _aspect_in(text: str) -> str | None:
    """Which aspect the user asked about, tolerating typos."""
    for aspect in ASPECTS:
        if fuzzy_contains(aspect, text):
            return aspect
    return None


def all_facts(country: str, facts: dict[str, str]) -> str:
    return (
        f"{country}: the capital is {_readable(facts['capital'])}, "
        f"they pay in {_readable(facts['currency'])} "
        f"and they speak {_readable(facts['language'])}."
    )


def _holders_of(field: str, norm: str, countries: Countries) -> list[str]:
    """Countries whose `field` is named in the text.

    A field may hold several values joined with '_', so each is checked on its
    own — that is what makes "where do they speak Arabic" work for a country
    listed as "Arabic_Tamazight_French".
    """
    return [
        name
        for name, facts in countries.items()
        if any(_mentions(part, norm) for part in facts.get(field, "").split("_"))
    ]


def _value_of(field: str, country: str, norm: str, countries: Countries) -> str:
    """The specific value that was mentioned, not the whole joined field."""
    for part in countries[country].get(field, "").split("_"):
        if _mentions(part, norm):
            return part.strip()
    return countries[country].get(field, "")


def answer(text: str, countries: Countries) -> str | None:
    """Answer a country question, or None if this is not one."""
    norm = normalize(text)

    match = find_country(norm, countries)
    if match:
        country, facts = match
        aspect = _aspect_in(norm)
        if aspect:
            key, template = ASPECTS[aspect]
            value = _readable(facts[key])
            return template.format(country=country, value=value)
        return all_facts(country, facts)

    # No country named. Maybe a currency or a language was — "who uses the
    # Euro", "where do they speak Arabic".
    for field, one, many in (("currency", "pays in", "pay in"), ("language", "speaks", "speak")):
        holders = _holders_of(field, norm, countries)
        if not holders:
            continue
        value = _value_of(field, holders[0], norm, countries)
        if len(holders) == 1:
            return f"{holders[0]} is the only country I know that {one} {value}."
        shown = ", ".join(holders[:MAX_LISTED])
        more = f" and {len(holders) - MAX_LISTED} more" if len(holders) > MAX_LISTED else ""
        return f"{len(holders)} countries {many} {value}: {shown}{more}."

    return None
