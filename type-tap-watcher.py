#!/usr/bin/env python3
"""Disable trackpad tap-to-click while actively typing."""
import subprocess, time, threading, signal, sys
from collections import deque
from pynput import keyboard

WINDOW     = 3.0    # rolling window, seconds
THRESHOLD  = 10     # keystrokes inside WINDOW that arm the guard
IDLE_RESET = 4.0    # seconds of silence that disarm it

presses    = deque()   # timestamps of recent key presses
last_press = 0.0
state      = None      # "on" = taps enabled, "off" = taps disabled
lock       = threading.Lock()

def set_taps(enabled):
    """Flip tap-to-click — but only on a real transition."""
    global state
    want = "on" if enabled else "off"
    if state == want:
        return
    subprocess.run(["defaults", "write", "com.apple.AppleMultitouchTrackpad",
                    "Clicking", "-bool", "true" if enabled else "false"])
    subprocess.run(["/System/Library/PrivateFrameworks/SystemAdministration.framework/Resources/activateSettings", "-u"])
    state = want
    print(f"{time.strftime('%H:%M:%S')}  taps {'ENABLED' if enabled else 'DISABLED'}", flush=True)

def on_press(key):
    global last_press
    now = time.monotonic()
    with lock:
        last_press = now
        presses.append(now)
        while presses and now - presses[0] > WINDOW:
            presses.popleft()
        if len(presses) >= THRESHOLD:
            set_taps(False)

def idle_watch():
    while True:
        time.sleep(1)
        with lock:
            if state == "off" and time.monotonic() - last_press >= IDLE_RESET:
                set_taps(True)

def shutdown(signum, frame):
    set_taps(True)      # always hand taps back, however we're told to quit
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT,  shutdown)   # Ctrl+C
    signal.signal(signal.SIGTERM, shutdown)   # launchctl unload
    set_taps(True)
    threading.Thread(target=idle_watch, daemon=True).start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
