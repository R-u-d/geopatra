"""Record the README demo GIF from the running application.

This exists so the GIF in the README is a recording of the real program rather
than a mock-up, and so it can be regenerated when the UI changes instead of
quietly going stale.

    python tools/record_demo.py                 # writes docs/media/demo.gif
    python tools/record_demo.py --keep-video    # keep the intermediate .mov

Three things about how it works are deliberate:

**The window opens at a fixed position and size**, so the screen rectangle is
known before anything is drawn and `screencapture` can be pointed straight at
it.

**Recording runs in its own process.** Grabbing frames one at a time from inside
the Tk loop would stall the animation and then record the stall.

**Recording starts only once the clips have finished decoding.** Startup is
several seconds of a static first frame; including it would spend a third of the
GIF on nothing.

The voice runs for real, quietly. The avatar animates off the speech engine's
busy edge, so muting it would change what gets recorded.

Requires ffmpeg, and macOS Screen Recording permission for whichever terminal
runs this: System Settings -> Privacy & Security -> Screen Recording. The
permission is only picked up after the terminal is restarted. Without it,
`screencapture` writes nothing and this script says so rather than producing a
black GIF.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geopatra.app import App  # noqa: E402
from geopatra.bot import Bot  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "media" / "demo.gif"

WINDOW_X, WINDOW_Y = 60, 60
VOLUME = 0.15

# Asked in order, with how long each answer stays on screen. The waits have to
# cover the spoken answer: the avatar only moves while the voice is running, so
# cutting early would show the idle loop instead of the point of the recording.
SCRIPT: list[tuple[str, float]] = [
    ("capital of peru", 4.0),
    ("tell me a joke", 6.0),
]

WELCOME_HOLD = 3.5   # the bot greets itself before the first question
TAIL = 1.2

# Roughly 15 seconds, which at the settings below lands near 6 MB. Every extra
# second costs about 0.4 MB, so adding a question means dropping another.

# Measured against the real clips rather than guessed. Full-frame video with
# constant motion is the worst case for GIF: at 640px/8fps/128 colours the
# avatar costs 104 KB per frame, which is 12 MB for fifteen seconds.
#
#   640px 8fps 128col   104 KB/frame     640px 8fps 32col    55 KB/frame
#   640px 8fps  64col    80 KB/frame     480px 8fps 64col    47 KB/frame
#
# The footage is very nearly greyscale, so dropping to 32 colours costs almost
# nothing visually and roughly halves the file. Dithering is pure overhead here
# for the same reason — it adds noise that defeats the compressor.
GIF_WIDTH = 640
GIF_FPS = 8
GIF_COLORS = 32
GIF_DITHER = "none"


def duration() -> float:
    return WELCOME_HOLD + sum(wait for _, wait in SCRIPT) + TAIL


def to_gif(video: Path, target: Path) -> None:
    """Two-pass palette conversion.

    One pass builds a palette from the whole recording, the second applies it.
    A single shared palette is what stops the colours shifting between frames;
    letting the encoder pick per frame is both uglier and larger.
    """
    palette = video.with_suffix(".palette.png")
    scale = f"fps={GIF_FPS},scale={GIF_WIDTH}:-1:flags=lanczos"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-vf", f"{scale},palettegen=max_colors={GIF_COLORS}:stats_mode=diff",
         str(palette)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(palette),
         "-lavfi", f"{scale}[x];[x][1:v]paletteuse=dither={GIF_DITHER}"
                   ":diff_mode=rectangle",
         str(target)],
        check=True,
    )
    palette.unlink(missing_ok=True)

    size_mb = target.stat().st_size / 1_000_000
    print(f"{target}  {size_mb:.1f} MB")
    if size_mb > 6:
        print("warning: over 6 MB. Shorten SCRIPT, or lower GIF_WIDTH / GIF_COLORS.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the README demo GIF")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--keep-video", action="store_true")
    args = parser.parse_args()

    if sys.platform != "darwin" or not shutil.which("screencapture"):
        raise SystemExit("This uses macOS screencapture. Record manually elsewhere.")
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found: brew install ffmpeg")

    video = args.output.with_suffix(".mov")
    video.parent.mkdir(parents=True, exist_ok=True)
    video.unlink(missing_ok=True)

    root = tk.Tk()
    root.geometry(f"+{WINDOW_X}+{WINDOW_Y}")
    bot = Bot(user="you")
    app = App(root, bot)
    app.speaker.engine.setProperty("volume", VOLUME)
    root.update_idletasks()

    rect = (root.winfo_rootx(), root.winfo_rooty(),
            root.winfo_width(), root.winfo_height())
    state: dict[str, subprocess.Popen | None] = {"recorder": None}

    def when_ready() -> None:
        """Poll until the clips have decoded, then record and start asking."""
        if not app.animator.ready:
            root.after(200, when_ready)
            return

        x, y, w, h = rect
        print(f"recording {w}x{h} at ({x},{y}) for {duration():.0f}s")
        state["recorder"] = subprocess.Popen(
            ["screencapture", "-v", "-x", "-V", str(int(duration()) + 2),
             "-R", f"{x},{y},{w},{h}", str(video)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

        delay = int(WELCOME_HOLD * 1000)
        for question, wait in SCRIPT:
            root.after(delay, lambda q=question: (app.entry.insert(0, q), app.on_send()))
            delay += int(wait * 1000)
        root.after(delay + int(TAIL * 1000), app.on_close)

    root.after(200, when_ready)
    root.mainloop()

    recorder = state["recorder"]
    if recorder is None:
        raise SystemExit("the clips never finished decoding — nothing was recorded")
    recorder.wait(timeout=60)

    if not video.exists() or video.stat().st_size == 0:
        stderr = recorder.stderr.read().decode().strip() if recorder.stderr else ""
        raise SystemExit(
            "screencapture wrote nothing"
            + (f": {stderr}" if stderr else "")
            + "\n\nGrant Screen Recording to this terminal in System Settings ->"
            "\nPrivacy & Security -> Screen Recording, then restart the terminal"
            "\nand run this again."
        )

    to_gif(video, args.output)
    if not args.keep_video:
        video.unlink()


if __name__ == "__main__":
    main()
