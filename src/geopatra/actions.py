"""The callbacks behind {placeholders} in response templates.

A response in `data.PATTERNS` is a template, not a finished sentence. When the
template contains `{time}` the bot has to ask the clock; when it contains
`{meteo}` it has to hit an API; when it contains `{quit}` it has to close the
window. `Actions` is where those live, one method per placeholder name.

Each callback receives the same `context` tuple — (template, pattern, match) —
so it can read the regex capture group out of the user's sentence. That is how
"weather in Lisbon" gets Lisbon to the weather call without a second parse.

Nothing here imports tkinter. The GUI is reached through the `Host` protocol,
and when there is no host (terminal mode, tests) the callbacks degrade instead
of failing.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from . import github, text, weather


@runtime_checkable
class Host(Protocol):
    """What the actions need from whatever is displaying the bot."""

    def clear_transcript(self) -> None: ...
    def request_quit(self) -> None: ...
    def queue_mood(self, key: str) -> None: ...


Context = tuple[str, str, Any]


def _group(context: Context, index: int = 1) -> str:
    """The captured text from the pattern, e.g. the place name in "weather in X"."""
    match = context[2]
    try:
        return (match.group(index) or "").strip()
    except (AttributeError, IndexError):
        return ""


class Actions:
    def __init__(self, bot, host: Host | None = None) -> None:
        self.bot = bot
        self.host = host
        # "content of <repo>" names a repo but not an owner. Remember whoever
        # was asked about last so the follow-up question works. The original
        # hardcoded a single username here, which made the feature answer for
        # the wrong account.
        self.last_github_owner = "R-u-d"

    # -- clock -------------------------------------------------------------
    def date(self, context: Context) -> str:
        return text.date_and_time("%a %d %b %y")

    def day(self, context: Context) -> str:
        return text.date_and_time("%A")

    def month(self, context: Context) -> str:
        return text.date_and_time("%B")

    def year(self, context: Context) -> str:
        return text.date_and_time("%Y")

    def time(self, context: Context) -> str:
        return text.date_and_time("%H:%M:%S")

    # -- who am I talking to ----------------------------------------------
    def user(self, context: Context) -> str:
        return self.bot.nickname or self.bot.current_user

    def set_nickname(self, context: Context) -> str:
        nickname = _group(context)
        if nickname:
            self.bot.nickname = nickname
        return self.bot.nickname or "nobody yet"

    # -- arithmetic --------------------------------------------------------
    def evaluate_expressions(self, context: Context) -> str:
        """Evaluate the arithmetic found in the user's sentence.

        `extract_expressions` only ever yields digits, operators and brackets,
        so this eval cannot see names, attributes or calls.
        """
        expressions = text.extract_expressions(self.bot.last_input)
        if not expressions:
            return "I could not find anything to calculate in there."

        width = max(len(e) for e in expressions)
        lines = []
        for expression in expressions:
            try:
                result: Any = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
            except (SyntaxError, ZeroDivisionError, TypeError, ValueError, OverflowError):
                result = "does not compute"
            lines.append(f"{expression:>{width}} = {result}")
        return "\n".join(lines)

    # -- network -----------------------------------------------------------
    def github_repos(self, context: Context) -> str:
        owner = _group(context)
        if owner:
            self.last_github_owner = owner
        return github.repos(self.last_github_owner)

    def github_contents(self, context: Context) -> str:
        return github.contents(self.last_github_owner, _group(context))

    def weather(self, context: Context) -> str:
        place = _group(context)
        return weather.report(place) if place else "Weather where?"

    # -- app control -------------------------------------------------------
    def clear_chat(self, context: Context) -> str:
        if self.host:
            self.host.clear_transcript()
        return ""

    def quit(self, context: Context) -> str:
        if self.host:
            self.host.request_quit()
        return ""

    def mood(self, context: Context, key: str) -> str:
        if self.host:
            self.host.queue_mood(key)
        return ""

    # -- wiring ------------------------------------------------------------
    def callbacks(self) -> dict:
        """Placeholder name -> callback, as used by `text.render`."""
        return {
            "x": self.evaluate_expressions,
            "date": self.date,
            "day": self.day,
            "month": self.month,
            "year": self.year,
            "time": self.time,
            "user": self.user,
            "nick": self.set_nickname,
            "clear": self.clear_chat,
            "quit": self.quit,
            "repos": self.github_repos,
            "repcon": self.github_contents,
            "meteo": self.weather,
            "joke": lambda ctx: self.mood(ctx, "funny_v1"),
            "joke1": lambda ctx: self.mood(ctx, "funny_v2"),
            "rap": lambda ctx: self.mood(ctx, "rap_v1"),
        }
