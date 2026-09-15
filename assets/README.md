# Assets

25 MP4 clips of the avatar, a background GIF and a window icon.

The clips are AI-generated video (MiniMax / Hailuo). They are here so the
application runs as demonstrated; they are not covered by the project's MIT
licence and are not offered for reuse. See `../LICENSE`.

The bottom tenth of each frame is cropped at load time (`RENDER_CROP` in
`src/geopatra/app.py`) — that is where the generator watermark sits.

Clip names drive the animation state machine. A clip whose name contains
`idle` joins the idle pool; `neutral`, `funny` or `rap` join the speaking pool.
`arrival` is loaded first and shown while the rest decode. Fourteen of the 25
are not loaded at startup; the list is `CLIPS` in `app.py`.
