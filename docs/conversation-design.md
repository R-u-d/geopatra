# Conversation design

How to change what the bot says without touching application code.

Everything the bot knows lives in [`src/geopatra/data.py`](../src/geopatra/data.py):
195 countries, 25 patterns, 40 response templates, 3 fallbacks. No logic.

---

## The three tables

**`COUNTRIES`** — one entry per country, three facts each. Multiple languages
are joined with `_` and rendered as a list at output time, so
`"Afrikaans_English_Zulu"` is read aloud as "Afrikaans, English and Zulu".

```python
"Peru": {"capital": "Lima", "currency": "Nuevo Sol", "language": "Spanish"},
```

**`PATTERNS`** — a regex mapped to a list of possible answers. One is picked at
random, so the same question twice does not give the same answer twice.

```python
r'\b(?:hello|hi|hey)\b': [
    "Hello there {user}! I am Geopatra. How can I help you today?",
],
```

**`DEFAULT_RESPONSES`** — used when nothing matched. There is always an answer.

---

## Writing a pattern

**Anchor bare keywords.** A pattern like `hello|hi|hey` matches `hi` inside
*somet**hi**ng*, and `war` inside *soft**war**e*. Every keyword pattern is
wrapped:

```python
r'\b(?:hello|hi|hey)\b'
```

This was a real bug: "what is software" returned an opinion about war.

**Order matters.** First match wins, top to bottom. Specific patterns go above
general ones. A test fails if a keyword pattern is completely shadowed by an
earlier one, but it cannot catch partial overlap, so read the neighbours before
inserting.

**Capture what you need.** The match object reaches the callback, so a pattern
can hand a value to a feature:

```python
r'(?:weather in|temperature in|climate in)\s+(.+?)(?:\s+(?:and|then|but)\b|[.?!]|$)': [
    '{meteo}'
],
```

Group 1 is the place name. The trailing alternation stops the capture at a
conjunction or punctuation so "weather in Lisbon and then a joke" does not send
*Lisbon and then a joke* to the geocoder.

**Matching runs against the raw input**, not a lowercased or stripped copy —
that is why patterns can contain apostrophes, and why "my nickname is Rud" is
answered with *Rud* and not *rud*.

---

## Placeholders

A response is a template. Anything in braces is a name looked up in a callback
map when the response is rendered.

| Placeholder | Does |
|:--|:--|
| `{user}` | the nickname, or how the bot was told to address you |
| `{nick}` | sets the nickname from capture group 1 |
| `{date}` `{day}` `{month}` `{year}` `{time}` | the clock |
| `{x}` | evaluates every arithmetic expression in the sentence |
| `{meteo}` | weather for capture group 1 |
| `{repos}` | public repositories of capture group 1 |
| `{repcon}` | top-level contents of repository in capture group 1 |
| `{clear}` | clears the transcript, returns nothing |
| `{quit}` | closes the application, returns nothing |
| `{joke}` `{joke1}` `{rap}` | switches the avatar to that mood clip |

A placeholder can be the whole response (`'{meteo}'`), or sit inside a sentence
(`"It's {time} o'clock"`), or be used purely for its effect
(`'{clear} Chat cleared.'`).

An unknown name renders as `<name?>` in the chat window instead of crashing the
app. A test fails if any template names a callback that does not exist.

Adding a new placeholder means one method on `Actions` and one line in
`Actions.callbacks()` — [`actions.py`](../src/geopatra/actions.py).

---

## Tone

The bot is written as a slightly smug machine that is nonetheless kind to the
person typing. That applies to the pattern responses and to the prompt sent to
the language model, which is in [`llm.py`](../src/geopatra/llm.py). Two
constraints on anything written for it:

- **No emoji, no markdown, no bullet lists.** Every response is read aloud by a
  speech engine, which pronounces them.
- **Short by default.** Everything is read aloud, so a long paragraph is a long
  wait.

---

## Origin

The original keyword and question list from the assignment is kept verbatim in
[`keywords-original.txt`](keywords-original.txt), as written on day one. It is
not loaded by the application — the tables above superseded it — but it is what
the conversation was designed from.
