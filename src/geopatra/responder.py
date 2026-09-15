"""Where every reply is decided.

One rule holds the design together: a route returns `None` when it has nothing
to say, and the dispatcher moves on. An empty string is a *valid* answer and
stops the chain — that is how a template like "{clear}" can do something and
deliberately print nothing.

Every route returns `(reply, metadata)`. The metadata says which route won,
which is what the GUI uses to colour the line and what the tests assert on.
"""

from __future__ import annotations

import contextlib
import io
import random
import re
from typing import Any

from . import countries as country_facts
from . import llm, text

Reply = tuple[str | None, dict[str, Any]]

# input prefixes that force a specific route
PREFIX_EVAL = ":"
PREFIX_EXEC = "!"
PREFIX_DB = "."
PREFIX_LLM = "?"

_ARITHMETIC = re.compile(r"^[\d\s+\-*/%().]+$")


class Responder:
    def __init__(self, bot, allow_code_execution: bool = False) -> None:
        self.bot = bot
        # Off by default. See docs/known-issues.md — with this on, anything
        # typed into the chat window runs as Python in the app's process.
        self.allow_code_execution = allow_code_execution
        self.llm_requests = 0

    # -- routes ------------------------------------------------------------

    def by_prefix(self, user_input: str) -> Reply:
        prefix, rest = user_input[0], user_input[1:].strip()
        if not rest:
            return None, {"route": "prefix"}
        if prefix == PREFIX_EVAL:
            return self.by_eval(rest)
        if prefix == PREFIX_EXEC:
            return self.by_exec(rest)
        if prefix == PREFIX_DB:
            return self.by_pattern(rest)
        if prefix == PREFIX_LLM:
            return self.by_llm(rest)
        return None, {"route": "prefix"}

    def by_country(self, user_input: str) -> Reply:
        reply = country_facts.answer(user_input, self.bot.countries)
        return reply, {"route": "country"}

    def by_pattern(self, user_input: str) -> Reply:
        """First regex in the data file that matches wins.

        Order in `data.PATTERNS` is therefore significant — specific patterns
        are listed before greedy ones.

        Matching runs against the raw input, not a normalized copy: several
        patterns in the data file contain apostrophes ("what's the date"), and
        capture groups have to keep the user's own capitalisation so that
        "my nickname is Rud" does not answer "rud".
        """
        raw = user_input.strip()
        for pattern, responses in self.bot.patterns.items():
            match = re.search(pattern, raw, re.IGNORECASE)
            if match:
                template = random.choice(responses)
                context = (template, pattern, match)
                rendered = text.render(template, context, self.bot.callbacks)
                return rendered, {"route": "pattern", "pattern": pattern}
        return None, {"route": "pattern"}

    def by_arithmetic(self, user_input: str) -> Reply:
        """Answer a bare sum like "2+2" without needing a pattern for it."""
        stripped = user_input.strip()
        if not _ARITHMETIC.fullmatch(stripped) or not any(c.isdigit() for c in stripped):
            return None, {"route": "arithmetic"}
        try:
            result = eval(stripped, {"__builtins__": {}}, {})  # noqa: S307
        except (SyntaxError, ZeroDivisionError, TypeError, ValueError, OverflowError):
            return None, {"route": "arithmetic"}
        return f"{stripped} = {result}", {"route": "arithmetic"}

    def by_llm(self, user_input: str) -> Reply:
        if not llm.available():
            return (
                "No language model is configured. Set HF_TOKEN if you want one.",
                {"route": "llm", "configured": False},
            )
        self.llm_requests += 1
        prompt = llm.SYSTEM_PROMPT.format(
            question=user_input,
            count=self.llm_requests,
            user=self.bot.nickname or self.bot.current_user,
            joke="{joke}",
            rap="{rap}",
        )
        answer = llm.ask(prompt)
        if answer is None:
            return "The model did not answer.", {"route": "llm", "failed": True}

        # The model may return {joke} or {rap}; those still have to drive the
        # avatar, so the reply goes through the same renderer. Only the two
        # mood placeholders are offered — a model must not be able to reach
        # {quit} or {clear}.
        mood_only = {
            key: self.bot.callbacks[key]
            for key in ("joke", "rap")
            if key in self.bot.callbacks
        }
        return text.render(answer, (answer, "llm", None), mood_only), {"route": "llm"}

    def by_eval(self, source: str) -> Reply:
        """Evaluate a Python expression. Gated; see `allow_code_execution`."""
        if not self.allow_code_execution:
            return self._blocked("eval")
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured):
                result = eval(source)  # noqa: S307
            return str(result if result is not None else captured.getvalue()), {"route": "eval"}
        except Exception as error:  # noqa: BLE001 - reporting the error IS the reply
            return f"{type(error).__name__}: {error}", {"route": "eval", "failed": True}

    def by_exec(self, source: str) -> Reply:
        """Run Python statements. Gated; see `allow_code_execution`."""
        if not self.allow_code_execution:
            return self._blocked("exec")
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured):
                exec(source)  # noqa: S102
            return captured.getvalue(), {"route": "exec"}
        except NameError as error:
            return f"Am I supposed to know what {error.name} is?", {"route": "exec"}
        except SyntaxError as error:
            return f"{error.msg}", {"route": "exec"}
        except Exception as error:  # noqa: BLE001 - reporting the error IS the reply
            return f"{type(error).__name__}: {error}", {"route": "exec", "failed": True}

    def by_default(self) -> Reply:
        return random.choice(self.bot.default_responses), {"route": "default"}

    def _blocked(self, route: str) -> Reply:
        return (
            "Running code is switched off. Start with --unsafe-code if you mean it.",
            {"route": route, "blocked": True},
        )

    # -- dispatcher --------------------------------------------------------

    def dispatch(self, user_input: str) -> Reply:
        """Try each route in order of specificity; first non-None wins."""
        user_input = user_input.strip()
        if not user_input:
            return None, {"route": "empty"}

        self.bot.last_input = user_input

        routes = []
        if user_input[0] in (PREFIX_EVAL, PREFIX_EXEC, PREFIX_DB, PREFIX_LLM):
            routes.append(lambda: self.by_prefix(user_input))
        routes += [
            # Patterns first. The original ran countries first, which meant
            # "weather in Lisbon" was answered with facts about Portugal —
            # Lisbon is a capital, and the country layer never looked at the
            # rest of the sentence. Patterns carry the explicit intent, so
            # they get first refusal; countries catch everything else that
            # names a place.
            lambda: self.by_pattern(user_input),
            lambda: self.by_country(user_input),
            lambda: self.by_arithmetic(user_input),
        ]
        if self.allow_code_execution:
            routes.append(lambda: self.by_exec(user_input))
        routes.append(self.by_default)

        for route in routes:
            reply, meta = route()
            if reply is not None:
                return reply, meta

        return "I have run out of ideas.", {"route": "error"}
