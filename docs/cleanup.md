# What changed against the original

The original repository is
[`jobben-2025/Speak2Me`](https://github.com/jobben-2025/Speak2Me). Everything
below is checkable by diffing the final file there, `geopatra_exe.py`, against
`src/` here.

## 1. A credential was in the source

The Hugging Face token was written into the code as a string literal, on a
public repository. It has been removed here and is read from `HF_TOKEN` instead.

Removing it from this repository does not make the leaked token safe — it stays
reachable through the old commit on the original repository. The token was
revoked at Hugging Face, which is what actually settles it.

## 2. The repository shipped its own dependencies

A full copy of Pillow, including compiled `.dylib` files, was committed at the
top level, along with `__pycache__` and `.DS_Store`. The checkout was 59 MB, of
which 19 MB is avatar clips, 19 MB is Pillow and the rest is build output.

Here: a pinned `requirements.txt`, a `.gitignore`, and a 20 MB checkout that is
almost entirely the avatar clips.

## 3. Twenty-one abandoned iterations were in the tree

`dump/` held `chatbot.py` through `chatbot13_gtts.py`, three GUI experiments
and several scratch files: 21 Python files, 10,856 lines, none of them imported
by anything. They are part of how the project was built and stay in the original
repository; they are not part of the project and are not here.

## 4. The logic could not be tested

`geopatra_exe.py` was a single 1,601-line file, and the three top-level modules
came to 2,965 lines. Importing any part of the response logic meant importing
Tkinter, OpenCV and a TTS engine, so there were no tests.

Split here into modules that import none of those (`text`, `countries`,
`responder`, `actions`, `weather`, `llm`, `github`) and modules that do
(`avatar`, `tts`, `app`). The GUI hands itself to the bot as a host object. 84
tests run with no window and no network, in CI on Linux with no display.

## 5. Eight correctness bugs

| | Found in | Effect |
|:--|:--|:--|
| 1 | Keyword patterns had no word boundaries | `hi` matched *somet**hi**ng*; `war` matched *soft**war**e*, so "what is software" was answered with an opinion about war. Every bare keyword pattern is now `\b(?:…)\b`. |
| 2 | OpenCV frames fed to PIL unconverted | BGR read as RGB — red and blue swapped on every frame. Barely visible on this near-monochrome footage, wrong nonetheless. |
| 3 | GitHub content lookup used a module-level `last_owner` that was never updated | "content of *X*" always queried one hardcoded account, whatever repository was asked about. |
| 4 | Two placeholder callbacks read module globals (`bot`, `app`) instead of their own attributes | Worked only because `__main__` happened to define those names. Any other entry point — including a test — raised `NameError`. |
| 5 | `{rap}` pointed at a neutral clip, and the rap clips were never loaded | The rap response played the ordinary talking animation. |
| 6 | Unreachable branch: `if rx < 70: … elif rx < 69: …` | The second idle clip could never be selected. |
| 7 | Input history crashed on an empty history | Pressing ↑ before typing anything raised `IndexError` on `history[0]`. |
| 8 | The `<` and `>` forced routes called their handler and discarded the result | Both were debug helpers that printed to stdout and returned `None`. Removed rather than fixed. |

`speech_recognition` was also imported and never used. There is no voice
*input* in this project and the dependency is gone; output is spoken, input is
typed.

## 6. Running arbitrary code is now opt-in

The original dispatcher used `eval()` and then `exec()` as automatic fallbacks
for any input that nothing else matched. Typing Python into the chat box ran it
in the application's process — including imports.

Here the `:` and `!` routes still exist, because evaluating code *is* one of the
demo features, but they are off unless the app is started with `--unsafe-code`,
and they are never reached automatically. Plain arithmetic ("12*12") still
answers without the flag: expressions are extracted character by character and
can only contain digits, operators and brackets, which is asserted by a test.

## 7. Personal content removed

Six hotkeys played jokes naming individual classmates and instructors. They were
funny in the room they were written for and do not belong in a public
repository.

## 8. The README described a different project

The original README is the assignment brief from day one — roles, a five-day
timeline, "at least two special features". It was never updated, and the
repository description still reads "Python basic Chatbot without AI
functionality", which by the end was not true.
