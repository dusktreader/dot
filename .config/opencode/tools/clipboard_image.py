#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow"]
# ///
"""Capture or grab a screenshot for OpenCode to read.

Usage:
  clipboard_image.py clipboard   - save clipboard image to fixed path
  clipboard_image.py capture     - open interactive region selector, save result
"""

import platform
import subprocess
import sys
from pathlib import Path

OUTPUT_PATH = Path.home() / ".config" / "opencode" / "clipboard.png"


def capture_interactive() -> None:
    """Open a native region selector and save the result to OUTPUT_PATH."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    system = platform.system()

    if system == "Darwin":
        # -i = interactive, -s = selection mode, saves directly to file
        result = subprocess.run(
            ["screencapture", "-i", "-s", str(OUTPUT_PATH)],
            capture_output=True,
        )
        if result.returncode != 0:
            print("error: screencapture failed or was cancelled", file=sys.stderr)
            sys.exit(1)
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.stat().st_size == 0:
            print("error: capture cancelled", file=sys.stderr)
            sys.exit(1)

    elif system == "Linux":
        # Try slurp+grim (Wayland), fall back to gnome-screenshot (X11)
        if subprocess.run(["which", "slurp"], capture_output=True).returncode == 0 and \
           subprocess.run(["which", "grim"], capture_output=True).returncode == 0:
            region = subprocess.run(["slurp"], capture_output=True, text=True)
            if region.returncode != 0:
                print("error: selection cancelled", file=sys.stderr)
                sys.exit(1)
            result = subprocess.run(
                ["grim", "-g", region.stdout.strip(), str(OUTPUT_PATH)],
                capture_output=True,
            )
        elif subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode == 0:
            result = subprocess.run(
                ["gnome-screenshot", "-a", "-f", str(OUTPUT_PATH)],
                capture_output=True,
            )
        elif subprocess.run(["which", "scrot"], capture_output=True).returncode == 0:
            result = subprocess.run(
                ["scrot", "-s", str(OUTPUT_PATH)],
                capture_output=True,
            )
        else:
            print("error: no supported screenshot tool found (install grim+slurp, gnome-screenshot, or scrot)", file=sys.stderr)
            sys.exit(1)
        if result.returncode != 0:
            print("error: capture failed or was cancelled", file=sys.stderr)
            sys.exit(1)

    elif system == "Windows":
        # Use Snipping Tool via PowerShell — saves to clipboard, then we grab it
        subprocess.run(
            ["powershell", "-Command", "Start-Process", "snippingtool", "/clip"],
            capture_output=True,
        )
        import time
        time.sleep(3)  # give the user time to snip
        grab_clipboard()
        return

    else:
        print(f"error: unsupported platform: {system}", file=sys.stderr)
        sys.exit(1)

    print(OUTPUT_PATH)


def grab_clipboard() -> None:
    """Save clipboard image to OUTPUT_PATH."""
    try:
        from PIL import ImageGrab
    except ImportError:
        print("error: Pillow not available", file=sys.stderr)
        sys.exit(1)

    img = ImageGrab.grabclipboard()
    if img is None:
        print("error: no image found on clipboard", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH, format="PNG")
    print(OUTPUT_PATH)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "clipboard"
    if mode == "capture":
        capture_interactive()
    elif mode == "clipboard":
        grab_clipboard()
    else:
        print(f"error: unknown mode '{mode}' (use 'clipboard' or 'capture')", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
