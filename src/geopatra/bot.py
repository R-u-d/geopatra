"""The bot itself: state plus wiring, no presentation.

`Bot` holds what a conversation needs to remember (who it is talking to, what
was last said) and owns a `Responder` and an `Actions`. It knows nothing about
windows, canvases or audio — a GUI passes itself in as `host`, a terminal
passes nothing. That is what makes the whole response layer testable.
"""

from __future__ import annotations

from . import data
from .actions import Actions, Host
from .responder import Responder

WELCOME = (
    "Welcome to Speak2Me. I am Geopatra.\n"
    "Ask me about any country — capital, currency, language — or about the "
    "time, the weather somewhere, or a GitHub user.\n"
    "Type 'exit' when you are done."
)

EXIT_WORDS = {"quit", "exit", "bye"}


class Bot:
    def __init__(
        self,
        user: str = "friend",
        host: Host | None = None,
        countries: dict | None = None,
        patterns: dict | None = None,
        default_responses: list[str] | None = None,
        allow_code_execution: bool = False,
    ) -> None:
        self.current_user = user
        self.nickname: str | None = None
        self.last_input = ""

        self.countries = data.COUNTRIES if countries is None else countries
        self.patterns = data.PATTERNS if patterns is None else patterns
        self.default_responses = (
            data.DEFAULT_RESPONSES if default_responses is None else default_responses
        )

        self.actions = Actions(self, host=host)
        self.callbacks = self.actions.callbacks()
        self.responder = Responder(self, allow_code_execution=allow_code_execution)

    @property
    def name(self) -> str:
        return self.nickname or self.current_user

    def respond(self, user_input: str) -> str | None:
        reply, _meta = self.responder.dispatch(user_input)
        return reply

    def wants_to_leave(self, user_input: str) -> bool:
        return user_input.strip().lower() in EXIT_WORDS


def repl(bot: Bot | None = None) -> None:
    """Terminal loop. Used for testing the response layer without a window."""
    bot = bot or Bot()
    print(WELCOME)
    print("-" * 60)
    try:
        while True:
            user_input = input(">> ")
            if bot.wants_to_leave(user_input):
                break
            reply = bot.respond(user_input)
            if reply:
                print(f"Geopatra: {reply}")
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        print("\nGeopatra: thanks for chatting.")
