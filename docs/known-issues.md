# Known issues

Things that are wrong or limited and were left that way on purpose.

---

## A country name anywhere in a sentence wins

"do you like China" is answered with the capital, currency and language of
China. The country layer looks for an entity, not an intent, so any sentence
containing a country name that no pattern claimed first gets a country answer.

Explicit intents are safe — "weather in Lisbon", "what time is it in Berlin" and
"repos of torvalds" are claimed by the pattern table, which runs first, and two
tests keep it that way. The gap is sentences with no recognised intent at all.

**Fix would be:** classify intent before extracting entities, i.e. a real NLU
layer. Out of proportion for a bot this size.

---

## The pattern table is ordered by hand

First regex that matches wins, and the order in `data.PATTERNS` is the order
they are tried. Adding a broad pattern near the top silently disables
everything specific below it.

A test catches the total case — a keyword pattern that an earlier pattern
already matches — but it cannot catch partial overlap, and it skips patterns
built around capture groups because there is no single literal to probe them
with.

**Fix would be:** score all matches and take the most specific, instead of
taking the first. Would also make the order stop mattering.

---

## Eleven clips live in RAM as decoded frames

Every frame of every loaded clip is held as a `Tk` image. That is tens of
megabytes and several seconds of startup. Startup is hidden — the first clip
plays while the rest decode on a worker thread — but the memory is real.

Clip count is the knob: `CLIPS` in `app.py`. Fourteen more clips sit unused in
`assets/geopatra/`.

**Fix would be:** stream frames instead of pre-decoding, or drop to a lower
render size. Never measured against an alternative; see the last section of
`decisions.md`.

---

## The window is sized for one aspect ratio

`RENDER_SIZE` is `1234x768`; the source clips are `1096x768`. The avatar is
stretched horizontally by about 12%, which was how the original had it and is
how it was demonstrated. Resizing the window does not rescale the avatar — the
background image keeps its decoded size and is repositioned, not redrawn.

**Fix would be:** re-decode or re-scale on `<Configure>`. Rescaling every frame
of every clip while the window is being dragged would stutter, so it was left
alone.

---

## `--unsafe-code` is genuinely unsafe

With the flag on, the `:` and `!` routes run whatever is typed, in the
application's process, with full builtins. That is what the flag is for, and it
is off by default. Do not enable it on a machine you care about or with input
you did not type yourself.

The arithmetic route is a different thing and is always on: expressions are
extracted character by character, can only contain digits, operators and
brackets, and are evaluated with empty globals. A test asserts the extractor
cannot emit a name, an attribute or a call.

---

## Speech is output only

There is no voice input. The original imported `speech_recognition` and never
called it; the dependency is gone. Input is typed.

---

## No Linux verification

Tested on macOS. `pyttsx3` on Linux needs `espeak`/`espeak-ng` installed, and
the voice will sound different. Nobody has run it there.

