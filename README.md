# type-tap-watcher

Disables trackpad tap-to-click while you're actively typing, so a resting
palm can't fire a stray click mid-sentence. Re-enables automatically once you
stop. A small macOS LaunchAgent — about 30 lines of Python.

## How it works

The guard runs on two opposite mechanisms, because typing and not-typing
aren't symmetrical events:

- Arming is event-driven. A pynput keyboard listener catches every keypress.
  When 10 keys land within a 3-second rolling window, tap-to-click switches off.
- Disarming is polled. "Stopped typing" never fires an event, so a background
  timer checks once a second and switches tap-to-click back on after ~4
  seconds of silence.

Because it watches the raw key stream (not just which app is frontmost), it
requires macOS Input Monitoring permission. Taps are toggled via
`defaults write com.apple.AppleMultitouchTrackpad Clicking` plus a settings
refresh, and tap-to-click is always restored on exit (SIGTERM/SIGINT).

Three constants at the top of the script tune the feel:

    WINDOW      3.0    rolling window, seconds
    THRESHOLD   10     keystrokes within WINDOW that arm the guard
    IDLE_RESET  4.0    seconds of silence that disarm it

## Requirements

- macOS
- Python 3
- pynput:  pip3 install --break-system-packages pynput
- Input Monitoring permission for the Python interpreter
  (System Settings > Privacy & Security > Input Monitoring)

## Install

1. Find the interpreter that has pynput:

       which python3

   Point the LaunchAgent at that exact binary. On Homebrew (Apple Silicon)
   prefer the versioned symlink, e.g. /opt/homebrew/bin/python3.14 — not the
   /opt/homebrew/Cellar/... path, which is version-pinned and breaks on the
   next brew upgrade.

2. Edit com.example.typetapwatcher.plist:
   - set Label to your own namespace (e.g. com.github.yourname.typetapwatcher)
     and rename the file to match
   - set the interpreter path from step 1
   - set the full path to type-tap-watcher.py

3. Install and load:

       cp com.example.typetapwatcher.plist ~/Library/LaunchAgents/
       launchctl load ~/Library/LaunchAgents/com.example.typetapwatcher.plist

4. Grant the interpreter Input Monitoring when prompted. If no prompt appears
   (common under launchd), add it manually in System Settings > Privacy &
   Security > Input Monitoring, then unload and load once more.

## Uninstall

    launchctl unload ~/Library/LaunchAgents/com.example.typetapwatcher.plist
    rm ~/Library/LaunchAgents/com.example.typetapwatcher.plist

## License

MIT — see LICENSE.
