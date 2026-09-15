"""The Tk window: transcript on a canvas, avatar behind it, entry at the bottom.

The transcript is drawn as canvas text items rather than in a Text widget. That
is what allows the avatar video to sit behind the words with no opaque box
around them — the canvas background *is* the animation, and the background
image is repositioned on every scroll so it stays put while the text moves.

`App` is also the `Host` the bot's actions talk to: it is what `{clear}` and
`{quit}` and the mood placeholders reach.
"""

from __future__ import annotations

import argparse
import tkinter as tk
from itertools import cycle
from pathlib import Path
from threading import Thread

from .avatar import EVENT_BUSY, EVENT_IDLE, EVENT_QUIT, Animator, Clip, load_frames
from .bot import WELCOME, Bot
from .tts import Speaker

ASSETS = Path(__file__).resolve().parents[2] / "assets"

# Clips loaded at startup. Names are matched by substring, so "idle" lands in
# the idle pool and "funny"/"rap"/"neutral" in the speaking pool.
CLIPS = (
    "idle_v1", "idle_v2", "idle_v3", "idle_v9",
    "neutral_v2", "neutral_v3",
    "funny_v1", "funny_v2", "funny_v3",
    "rap_v1",
)
FIRST_CLIP = "arrival"

RENDER_SIZE = (1234, 768)
RENDER_CROP = (0.0, 0.0, 1.0, 0.90)  # trim the letterbox at the bottom

COLOR_USER = "#CAEAFC"
COLOR_BOT = "#BD0029"
COLOR_HEADER_BG = "#2A2A2A"


class App:
    def __init__(self, root: tk.Tk, bot: Bot) -> None:
        self.root = root
        self.bot = bot
        self.bot.actions.host = self
        self.speaker = Speaker(root)
        self.busy = True
        self._quitting = False

        root.wm_title("Speak2Me — Geopatra")
        root.geometry(f"{RENDER_SIZE[0]}x{RENDER_SIZE[1] - 50}")
        root.minsize(800, 500)
        root.configure(bg=COLOR_HEADER_BG)

        # -- layout --------------------------------------------------------
        entry_rel_h = 0.05
        frame = tk.Frame(root)
        frame.place(relwidth=1, relheight=1 - entry_rel_h)

        self.header_font = ["Arial", 28, "bold"]
        self.header = tk.Label(
            frame, text="geopatra.exe", font=self.header_font,
            bg=COLOR_HEADER_BG, fg="white",
        )
        self.header.pack(fill=tk.X)

        self.canvas = tk.Canvas(frame, bg="black", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        first_path = ASSETS / "geopatra" / f"{FIRST_CLIP}.mp4"
        first = Clip(FIRST_CLIP, load_frames(first_path, RENDER_SIZE, RENDER_CROP))
        self.background_id = self.canvas.create_image(
            0, 0, image=first.photos[0], anchor="nw", tags=("bg",)
        )

        self.entry = tk.Entry(root, font=("Arial", 22), bg=COLOR_HEADER_BG, fg="#FFFFFF")
        self.entry.place(relwidth=0.88, relheight=entry_rel_h, rely=1 - entry_rel_h)
        self.entry.bind("<Return>", self.on_send)
        self.entry.focus_set()

        tk.Button(root, text="Send", font=("Arial", 14), command=self.on_send).place(
            relx=0.88, rely=1 - entry_rel_h, relwidth=0.12, relheight=entry_rel_h
        )

        # -- transcript state ---------------------------------------------
        self.chat_font = ["Arial", 20]
        self.font_min, self.font_max = 10, 48
        self.text_items: list[int] = []
        self.x_offset = 40
        self.y_offset_start = 10
        self.y_offset = self.y_offset_start
        self.y_pad = 8
        self.wrap = RENDER_SIZE[0] / 3

        self.history: list[str] = []
        self.history_index = 0
        self.keys_held: set[str] = set()

        # -- avatar --------------------------------------------------------
        self.animator = Animator(root, self.canvas, self.background_id)
        self.animator.add(FIRST_CLIP, first)
        self.loader = Thread(target=self._load_clips, daemon=True)
        self.loader.start()

        # -- bindings ------------------------------------------------------
        root.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", lambda e: self.keys_held.discard(e.keysym))
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        root.bind(EVENT_BUSY, lambda e: setattr(self, "busy", True))
        root.bind(EVENT_IDLE, lambda e: setattr(self, "busy", False))
        root.bind(EVENT_QUIT, self.on_quit_event)

        self._header_colors = cycle([COLOR_HEADER_BG, "#FFFFFF"])
        self._flash_header()
        self.animator.start()

    def on_canvas_resize(self, event=None) -> None:
        self.scroll_to_bottom()
        self.reposition_background()

    def _flash_header(self) -> None:
        self.header.configure(fg=next(self._header_colors))
        self.root.after(800, self._flash_header)

    # -- Host protocol -----------------------------------------------------
    def clear_transcript(self) -> None:
        self.canvas.delete("msg")
        self.text_items.clear()
        self.y_offset = self.y_offset_start
        self.canvas.configure(
            scrollregion=(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height())
        )
        self.canvas.yview_moveto(0.0)
        self.reposition_background()

    def request_quit(self) -> None:
        self.root.event_generate(EVENT_QUIT)

    def queue_mood(self, key: str) -> None:
        self.animator.queue_mood(key)

    # -- startup -----------------------------------------------------------
    def _load_clips(self) -> None:
        """Decode the remaining clips off the main thread.

        Decoding all of them up front costs several seconds of a frozen window.
        The `arrival` clip is already on screen, so the rest can stream in while
        the user reads the welcome line.
        """
        for name in CLIPS:
            path = ASSETS / "geopatra" / f"{name}.mp4"
            if not path.exists():
                continue
            frames = load_frames(path, RENDER_SIZE, RENDER_CROP)
            if len(frames) >= 2:
                # Tk objects must be built on the main thread, so the decode
                # happens here but the Clip is constructed over there.
                self.root.after(0, self._register_clip, name, frames)
        self.root.after(0, self._clips_ready)

    def _register_clip(self, name: str, frames) -> None:
        self.animator.add(name, Clip(name, frames))

    def _clips_ready(self) -> None:
        self.animator.classify()
        self.animator.ready = True
        self.say(WELCOME.splitlines()[0], mood=FIRST_CLIP)

    # -- talking -----------------------------------------------------------
    def say(self, text: str, mood: str = "neutral") -> None:
        self.animator.queue_mood(mood)
        self.speaker.say(text)

    def on_send(self, event=None) -> None:
        query = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not query:
            return

        self.add_line(f"{self.bot.name} > {query}", COLOR_USER)
        self.history.append(query)
        self.history_index = 0

        if self.bot.wants_to_leave(query):
            self.say("Goodbye.")
            self.request_quit()
            return

        reply = self.bot.respond(query)
        if reply:
            self.add_line(f"Geopatra: {reply}", COLOR_BOT)
            self.speaker.say(reply)

    # -- transcript --------------------------------------------------------
    def add_line(self, text: str, color: str) -> None:
        self.canvas.update_idletasks()
        item = self.canvas.create_text(
            self.x_offset, self.y_offset, anchor="nw", text=text,
            font=self.chat_font, fill=color, width=self.wrap, tags=("msg",),
        )
        self.text_items.append(item)
        self.y_offset = self.canvas.bbox(item)[3] + self.y_pad
        self.scroll_to_bottom()
        self.reposition_background()

    def relayout(self) -> None:
        self.y_offset = self.y_offset_start
        for item in self.text_items:
            self.canvas.coords(item, self.x_offset, self.y_offset)
            self.y_offset = self.canvas.bbox(item)[3] + self.y_pad
        self.scroll_to_bottom()
        self.reposition_background()

    def scroll_to_bottom(self) -> None:
        self.canvas.update_idletasks()
        box = self.canvas.bbox("msg")
        view_w, view_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        _, _, x2, y2 = box if box else (0, 0, view_w, view_h)
        self.canvas.configure(scrollregion=(0, 0, max(x2, view_w), max(y2, view_h)))
        self.canvas.yview_moveto(1.0)

    def reposition_background(self) -> None:
        """Pin the avatar to the viewport while the transcript scrolls past it."""
        self.canvas.coords(
            self.background_id, self.canvas.canvasx(0), self.canvas.canvasy(0)
        )

    def zoom(self, delta: int) -> None:
        size = self.chat_font[1]
        self.chat_font[1] = min(self.font_max, max(self.font_min, size + delta))
        for item in self.text_items:
            self.canvas.itemconfig(item, font=self.chat_font)
        self.relayout()

    def recall_history(self, direction: int) -> None:
        if not self.history:
            return
        self.history_index = max(0, min(len(self.history), self.history_index - direction))
        self.entry.delete(0, tk.END)
        if self.history_index:
            self.entry.insert(0, self.history[-self.history_index])

    # -- input -------------------------------------------------------------
    def on_key_press(self, event) -> None:
        self.keys_held.add(event.keysym)
        control = "Control_L" in self.keys_held or "Control_R" in self.keys_held
        match event.keysym:
            case "minus" if control:
                self.zoom(-1)
            case "plus" | "equal" if control:
                self.zoom(1)
            case "Up":
                self.recall_history(1)
            case "Down":
                self.recall_history(-1)
            case "F5":
                self.say("You pressed F5. I am a chatbot, not a web page.", "funny_v1")

    def on_mousewheel(self, event) -> None:
        delta = int(-1 * (event.delta / 120))
        if "Control_L" in self.keys_held or "Control_R" in self.keys_held:
            self.zoom(delta)
            return
        self.canvas.yview_scroll(delta, "units")
        self.reposition_background()

    # -- shutdown ----------------------------------------------------------
    def on_quit_event(self, event=None) -> None:
        """Wait for the voice to finish its goodbye before tearing down Tk."""
        self._quitting = True
        if self.busy:
            self.root.after(500, self.on_quit_event)
            return
        self.on_close()

    def on_close(self) -> None:
        self.speaker.shutdown()
        self.animator.stop()
        self.root.destroy()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Speak2Me — chatbot with an animated avatar")
    parser.add_argument("--terminal", action="store_true", help="run without the GUI or voice")
    parser.add_argument(
        "--unsafe-code",
        action="store_true",
        help="enable the ':' and '!' routes, which run typed input as Python",
    )
    parser.add_argument("--user", default="friend", help="how the bot addresses you")
    args = parser.parse_args(argv)

    if args.terminal:
        from .bot import repl

        repl(Bot(user=args.user, allow_code_execution=args.unsafe_code))
        return

    root = tk.Tk()
    bot = Bot(user=args.user, allow_code_execution=args.unsafe_code)
    App(root, bot)
    root.mainloop()


if __name__ == "__main__":
    main()
