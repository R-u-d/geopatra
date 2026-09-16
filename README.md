# Geopatra

A desktop chatbot that speaks its answers and animates an avatar in time with
its own voice. Python, Tkinter, no game engine and no web stack.

Started as **Speak2Me**, a one-week group project at WBS Coding School — the
brief was "a chatbot in Python, at least ten keywords and two extra features".
Geopatra is the name it got once it had a face and a voice. This repository is
where it ended up two and a half weeks later, cleaned up and tested; the
original, with the full commit history and every pull request, is
[`jobben-2025/Speak2Me`](https://github.com/jobben-2025/Speak2Me).

![Geopatra answering two questions, avatar animating in time with the voice](docs/media/demo.gif)

*Unedited 15-second screen recording of the running program, produced by [`tools/record_demo.py`](tools/record_demo.py).*

---

## The problem

A keyword chatbot is a solved exercise. Ours had to hold a room for five
minutes, which turned the assignment into three problems:

**1. It had to talk, and look like it was talking.**
Text-to-speech is easy. Making an avatar move *with* the voice is not, because
the length of an utterance is not known in advance — it depends on the text,
the voice, and the platform. Any timer-based approach drifts within one
sentence.

**2. It could not depend on a language model.**
A live demo that calls a hosted model over venue wifi fails in front of an
audience. The bot had to give good answers with the network unplugged, and use a
model only as a bonus route.

**3. Every answer had to be able to *do* something.**
"What time is it" cannot be answered from a fixed string. Neither can "weather
in Lisbon" or "clear the chat". The answer layer needed to reach the clock, the
network and the window without the data file knowing any of that exists.

## The decisions

**Sync the avatar to the voice, not to a clock.**
The TTS engine runs in non-blocking mode and is polled from the Tk main loop
every 50 ms. The *edge* of `engine.isBusy()` — not its value — is turned into a
Tk virtual event (`<<speaking>>` / `<<silent>>`). The animator listens for those
events. Nothing estimates how long a sentence takes; the avatar reacts to the
voice actually starting and stopping.
→ [`tts.py`](src/geopatra/tts.py), [`avatar.py`](src/geopatra/avatar.py)

**Play clips ping-pong and only swap at a boundary.**
The avatar is 25 short MP4 clips, decoded once into Tk images. Each clip plays
forwards then backwards (`BounceCycle`), so a two-second clip loops forever with
no visible cut. A clip is only exchanged when the bounce returns to frame one,
so switching moods never looks like a dropped frame.
→ [`avatar.py`](src/geopatra/avatar.py), tested in
[`test_bounce_cycle.py`](tests/test_bounce_cycle.py)

**Make responses templates with callbacks, not strings.**
A response in the data file is `"It's {time} o'clock"` or `"{meteo}"`. The
placeholder name is looked up in a callback map and resolved on first use, with
the regex match handed to the callback — which is how "weather in Lisbon" gets
*Lisbon* to the weather call without parsing the sentence twice. That is also
how a response can clear the transcript or close the window.
→ [`text.render`](src/geopatra/text.py), [`actions.py`](src/geopatra/actions.py)

**One rule for the dispatcher: `None` means "not mine".**
Routes are tried from most specific to least. A route that has nothing to say
returns `None` and the chain continues. An empty string is a *valid* answer and
stops the chain — that is how `{clear}` acts and deliberately prints nothing.
Order: forced prefix → country → pattern table → bare arithmetic → default.
→ [`responder.py`](src/geopatra/responder.py)

**Keep the language model optional and off the critical path.**
The LLM answers only when the user prefixes a line with `?`, and only if
`HF_TOKEN` is set. Everything else works with no token and no network. A model
reply is rendered through the same placeholder mechanism, but with only the two
avatar-mood placeholders offered — a model must not be able to reach `{quit}`.
→ [`llm.py`](src/geopatra/llm.py)

**Split the logic away from the window.**
`text`, `countries`, `responder`, `actions`, `weather`, `llm` and `github`
import no Tkinter, no OpenCV and no audio. The GUI passes itself in as a host
object, which is what lets the response layer be tested without opening a
window.
→ [`bot.py`](src/geopatra/bot.py)

### Documentation

| | |
|:--|:--|
| [`docs/decisions.md`](docs/decisions.md) | the six decisions in full, with what was rejected and what each cost |
| [`docs/architecture.md`](docs/architecture.md) | module graph, one turn traced end to end, the dispatcher, the avatar |
| [`docs/conversation-design.md`](docs/conversation-design.md) | how to change what the bot says without touching code |
| [`docs/known-issues.md`](docs/known-issues.md) | what is wrong on purpose, and what fixing it would take |
| [`docs/cleanup.md`](docs/cleanup.md) | every change against the original, diffable |

## Status

Working and demonstrated. Not maintained as a product.

| | |
|:--|:--|
| Application code | 13 modules |
| Conversation data | 195 countries, 25 patterns, 40 response templates |
| Avatar | 25 clips, 11 loaded at startup |
| Tests | 84, no display and no network |
| Lint | `ruff` clean |
| Platform | Only ever run on macOS; Linux and Windows untried |

What this repository is **not**: it is not the original history. See
[Provenance](#provenance).

## Run it

```bash
git clone https://github.com/R-u-d/geopatra && cd geopatra
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                       # or: pip install -r requirements.txt

geopatra                               # the window, with voice and avatar
geopatra --terminal                    # response layer only, no audio, no window
geopatra --help
```

Run it from a clone — the avatar clips live in the repository, not in the
installed package.

The window takes a few seconds to reach full speed — the remaining clips decode
on a background thread while the first one is already on screen.

Optional language model:

```bash
export HF_TOKEN=hf_...                 # Hugging Face inference token
geopatra
```

Then prefix a line with `?` to route it to the model.

### Things to type

| | |
|:--|:--|
| `capital of Peru` | one fact |
| `whats the langiuage of brazil` | the typo is deliberate — fuzzy keyword match |
| `which country has Lima` | capital resolved back to its country |
| `who pays in Euro` | currency resolved back to 23 countries |
| `where do they speak Arabic` | same for languages, 25 countries |
| `tell me about Japan` | everything known |
| `calculate 3*7 and 8-1` | several expressions in one sentence |
| `weather in Lisbon` | Open-Meteo, no API key |
| `repos of torvalds` | GitHub API, unauthenticated |
| `my nickname is Rud` | remembered for the session |
| `clear` | the answer clears the transcript |
| `?explain recursion` | routed to a language model, if configured |

### Development

```bash
pip install -e ".[dev]"     # or: pip install -r requirements-dev.txt for pinned versions
pytest                      # 84 tests, no network, no window, under a second
ruff check .
```

CI runs both on every push, on Linux with no display.

The demo GIF at the top is a recording of the real application, produced by
[`tools/record_demo.py`](tools/record_demo.py): it opens the window at a fixed
position, waits for the clips to decode, types a scripted conversation into the
actual entry widget and records the window rectangle. Regenerate it after a UI
change. Needs `ffmpeg` and, on macOS, Screen
Recording permission for the terminal.

```bash
python tools/record_demo.py
```

## Provenance

This is a clean import, not a rewritten history. The code here is the final
state of the project plus the cleanup described below; the commit history of
how it was built lives in the original repository and is not reproduced here.

Written by [**@jobben-2025**](https://github.com/jobben-2025) (Benjamin Becht)
and [**@R-u-d**](https://github.com/R-u-d) (R. Hildermann). The original was a
group project with a third participant; the layer he contributed — country
lookups and fuzzy keyword matching — was rewritten from scratch for this
repository, so everything here belongs to the two authors above. His work is
still visible in the upstream pull requests.

**AI disclosure.** Parts of the application code were written with AI
assistance. The avatar clips in `assets/geopatra/` are AI-generated video
(MiniMax / Hailuo). The conversation data, the dispatcher design, the
placeholder-callback mechanism and the voice-synchronised animation were our
decisions, and are written up in `docs/decisions.md`.

**What changed against the original**, all of it verifiable by diffing against
upstream — see [`docs/cleanup.md`](docs/cleanup.md):
a hardcoded API token removed, a vendored copy of Pillow and 21 abandoned
iteration files deleted, the response logic separated from the GUI, eight
correctness bugs fixed, code execution turned off by default, and 84 tests
added where there were none.

## Licence

Code: MIT, see [LICENSE](LICENSE).
The avatar clips and background art in `assets/` are **not** covered by it —
they are machine-generated media kept for the demo. Do not reuse them.
