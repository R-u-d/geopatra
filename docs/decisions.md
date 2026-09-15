# Decisions

Six that shaped the project, with what they cost and what was rejected.

**1–4 were taken during the project**, in September 2025, and are visible in the
original code. **5 and 6 were taken during this cleanup** and are marked as such;
they change behaviour the original had. Where something was never properly
weighed at all, the last section says so.

---

## 1. The avatar follows the voice, not a timer

**Problem.** The avatar has to move while the bot talks and stop when it stops.
The duration of an utterance is not known before it is spoken — it depends on
the text, the selected voice and the platform's speech engine.

**Rejected: estimate the duration.** Words times a rate constant, animate for
that long. Cheap, and wrong by a visible margin on the second sentence. The rate
constant would need retuning on every machine.

**Rejected: `runAndWait()` on a worker thread.** Blocks until the utterance ends,
which gives an exact end time — but then the animation has to be driven from
that thread, and Tk widgets may only be touched from the main thread. Both this
and the plain blocking call are still in the original source as commented-out
lines (`geopatra_exe.py:933`, `:935`, `:941`); they were tried and abandoned
before the polled approach at `:823`.

**Chosen.** Run the engine in non-blocking mode (`startLoop(False)`), call
`iterate()` from a 50 ms Tk `after()` poll, and watch `isBusy()` for an *edge*.
A rising edge emits the Tk virtual event `<<speaking>>`, a falling edge
`<<silent>>`. The animator binds those.

**Cost.** Up to 50 ms of latency on each transition. The poll runs for as long as
the app is open.

**Result.** Nothing to calibrate, and the same behaviour on a machine we have
never run it on.

---

## 2. Responses are templates with callbacks

**Problem.** "What time is it" cannot come from a fixed string. Neither can
"weather in Lisbon", which additionally needs the word *Lisbon* out of the
sentence. But the conversation data is written by whoever is designing the
conversation, and they should not have to touch application code to add a
response.

**Rejected: a handler function per intent.** Every new response becomes a new
function and a new branch. The data file stops being data.

**Chosen.** A response is a template: `"It's {time} o'clock"`, `"{meteo}"`. The
name inside the braces is looked up in a callback map at render time and the
callback is handed the regex match, so it can read the capture group. Adding a
response that fetches weather for a city is one line in a dict.

**Cost.** A name in the data file that has no callback behind it is only caught
at render time. Mitigated two ways: an unknown name renders as `<name?>` instead
of raising, and a test fails if any template in the data file names a callback
that does not exist.

**Not planned.** Because a callback runs for its side effect as much as its
return value, a response can *act*: `{clear}` wipes the transcript, `{quit}`
closes the window, `{joke}` switches the avatar's mood. The conversation
designer can trigger application behaviour without writing code. That was a
by-product.

---

## 3. The language model is a route, not the engine

*The structure is the original's. The reasoning is reconstructed — there is no
record of it being argued at the time.*

**What was built.** The model was added last, on top of a rule-based stack that
was already complete, and it is reachable only by prefixing a line with `?`.
Every other route works with no token and no network.

**Effect.** Routing everything through a model would have made the
pattern table, the country data and the dispatcher invisible — which was most
of the assignment. It would also have put a live demo at the mercy of the
venue's wifi. Keeping the model as one route among several avoids both.

**Cost.** The model answers need an explicit prefix, which also keeps the
boundary between the two layers visible.

**Security note.** A model reply is rendered through the same placeholder
mechanism, because the prompt asks the model to emit `{joke}` or `{rap}` to
drive the avatar. Only those two names are offered to it. A model cannot reach
`{quit}` or `{clear}`, and prompt injection in a user's question cannot use the
renderer to act on the application.

---

## 4. Country lookups are their own layer, behind the pattern table

**Problem.** Countries are the one topic the bot genuinely knows: 195 entries
with capital, currency and language. Encoding that as regex patterns would need
hundreds of entries and would still not answer "which country has Lima".

**Chosen.** A separate module answering four shapes of question: country plus
aspect, capital to country, currency to countries, country alone.

**Where it sits changed during the cleanup.** The original ran it *before* the
pattern table. That breaks any sentence that names a place for some other
reason: "weather in Lisbon" was answered with facts about Portugal, because
Lisbon is a capital and the country layer never read the rest of the sentence.
It now runs *after*, so an explicit intent wins and the country layer catches
what is left. Two regression tests pin it.

Two more details were added during the cleanup, after tests were written for
cases the original got wrong:

- **Longest match wins.** `Niger` is a substring of `Nigeria`, and `Africa` of
  `South Africa`. The fix is to scan for the longest name first.
- **Whole-token matching.** Names are matched as tokens, not substrings, so
  `Chad` is not found inside `Chadwick`.

**Cost.** The layer still answers any sentence containing a
country name, whatever the sentence was about: "do you like China" returns the
capital, currency and language of China. Doing better means intent detection
before entity detection, which is a larger design than this project needed. See
[`known-issues.md`](known-issues.md).

---

## 5. Running arbitrary code is a feature, and it is off

*Taken during the cleanup, not during the project.*

**Problem.** "The bot can evaluate Python" is a good demo moment. It is also
`exec()` on user input.

**What the original did.** `eval()` and then `exec()` sat in the dispatcher as
automatic fallbacks for anything unmatched. Typing Python into the chat box ran
it in the app's process, imports included. Nobody decided this — it grew out of
using `eval` to answer arithmetic and never got bounded.

**Chosen.** The `:` and `!` routes still exist, because the feature is real, but
they are disabled unless the app is started with `--unsafe-code`, and they are
never reached without an explicit prefix. The banner in `--help` says what the
flag does.

Ordinary arithmetic still works with the flag off. Expressions are extracted
character by character and can contain only digits, operators and brackets, then
evaluated with empty globals. A test asserts that the extractor cannot emit a
name, an attribute or a call, for inputs that try.

**Cost.** One flag, and a line of documentation.

---

## 6. The response layer does not import a GUI

*Taken during the cleanup, not during the project.*

**Problem.** The original was one 1,600-line file. Importing the dispatcher
meant importing Tkinter, OpenCV and a speech engine, so nothing was tested.

**Chosen.** Split along the question "does this need a window?". The GUI hands
itself to the bot as a `Host` with three methods. Where there is no host, the
actions that need one become no-ops rather than errors, which is also what makes
`--terminal` mode work.

**Cost.** One indirection between an action and the window, and a protocol to
keep in sync. In exchange the response layer can be tested with no display and
no network.

---

## Not really decided

**Tkinter.** It was the default in the course and was never weighed against
anything. It works well enough here — ships with Python, no packaging step,
canvas text over a canvas image — but those reasons were found afterwards.

**Decoding video into memory.** Eleven clips are held as decoded Tk images, which
is tens of megabytes of RAM and several seconds of startup. A video widget or an
image-sequence format would be lighter. This was never compared; decoding with
OpenCV was simply the first thing that worked.
