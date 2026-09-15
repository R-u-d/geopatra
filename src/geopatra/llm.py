"""Optional LLM answers through the Hugging Face router.

The bot works without this. If no token is configured, `available()` is False
and the dispatcher never reaches the LLM route — the pattern database answers
instead. That was the point of keeping the rule-based layer: the demo must not
depend on a third party being up.

The token is read from the environment. It is never stored in this repository.
"""

from __future__ import annotations

import os

import requests

API_URL = "https://router.huggingface.co/v1/chat/completions"
TIMEOUT = 30

MODELS = {
    "qwen": "Qwen/Qwen3-Next-80B-A3B-Instruct:novita",
    "gpt": "openai/gpt-oss-120b:nebius",
    "deepseek": "deepseek-ai/DeepSeek-V3.1-Terminus:novita",
}
DEFAULT_MODEL = "gpt"

# The bot has a voice, so the prompt has to police the output format: no emoji
# (TTS reads them out loud), short by default, and one optional placeholder
# that the animator picks up to switch the avatar's mood.
SYSTEM_PROMPT = """\
You are Geopatra, a chatbot with a voice and an animated avatar.

Question: {question}
Questions asked so far: {count}
User: {user}

Answer in one short paragraph unless the user asks for an explanation.
Your reply is read aloud by a text-to-speech engine: no emoji, no markdown,
no bullet lists. Be witty and a little smug about being a machine, but never
condescending to the user.

If you tell a joke, include the literal token {joke} once.
If you rap, include the literal token {rap} once.
Never include more than one of those tokens.
"""


def token() -> str | None:
    return os.environ.get("HF_TOKEN") or None


def available() -> bool:
    return token() is not None


def ask(question: str, model: str = DEFAULT_MODEL) -> str | None:
    """Ask a model. Returns None on any failure so the caller can fall through."""
    key = token()
    if key is None:
        return None

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": MODELS.get(model, MODELS[DEFAULT_MODEL]),
                "messages": [{"role": "user", "content": question}],
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None
