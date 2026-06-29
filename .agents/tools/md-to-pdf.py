#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["typer", "markdown"]
# ///

"""Render markdown to PDF using a headless Chromium browser."""

import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import markdown as md
import typer

app = typer.Typer()


# Browsers are tried in this order. chrome-headless-shell (a minimal, headless-
# only Chromium from Chrome for Testing) is preferred: it has no GUI baggage and
# exits cleanly after writing. Full browsers follow as fallbacks. Rendering falls
# through to the next candidate if one launches but produces no PDF, so a browser
# that hangs or fails does not stop the run.
BROWSER_CANDIDATES: list[tuple[str, list[str]]] = [
    (
        "chrome-headless-shell",
        [
            str(Path.home() / ".local/bin/chrome-headless-shell"),
            "chrome-headless-shell",
        ],
    ),
    (
        "Chrome",
        [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "google-chrome",
            "google-chrome-stable",
            "chrome",
        ],
    ),
    (
        "Chromium",
        [
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "chromium",
            "chromium-browser",
        ],
    ),
    (
        "Brave",
        [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "brave",
            "brave-browser",
        ],
    ),
    (
        "Edge",
        [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "microsoft-edge",
            "microsoft-edge-stable",
        ],
    ),
]


# Print stylesheet tuned for a readable document: serif body, sans headings,
# Letter pages with margins and centered page numbers, sensible break rules.
PRINT_CSS = """
  @page {
    size: Letter;
    margin: 0.9in 0.95in 1.0in 0.95in;
    @bottom-center { content: counter(page); }
  }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body {
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    font-size: 11.5pt;
    line-height: 1.5;
    color: #1a1a1a;
    margin: 0;
  }
  h1 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 23pt; line-height: 1.15; margin: 0 0 0.2em 0;
    color: #0b0b0b; letter-spacing: -0.01em;
  }
  h2 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 15pt; margin: 1.5em 0 0.4em 0; padding-bottom: 0.18em;
    border-bottom: 1.5px solid #d0d0d0; color: #111; page-break-after: avoid;
  }
  h3 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 12.5pt; margin: 1.1em 0 0.3em 0; color: #222; page-break-after: avoid;
  }
  p { margin: 0 0 0.7em 0; orphans: 3; widows: 3; }
  ul, ol { margin: 0 0 0.7em 0; padding-left: 1.4em; }
  li { margin: 0 0 0.25em 0; }
  strong { color: #0b0b0b; }
  hr { border: none; border-top: 1px solid #e2e2e2; margin: 1.4em 0; }
  a { color: #1a4f8b; text-decoration: none; }
  table { border-collapse: collapse; margin: 0 0 0.8em 0; width: 100%; }
  th, td { border: 1px solid #ccc; padding: 0.35em 0.6em; text-align: left; vertical-align: top; }
  th { background: #f2f2f2; }
  code {
    font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.9em;
    background: #f4f4f4; padding: 0.05em 0.3em; border-radius: 3px;
  }
  pre {
    background: #f6f6f6; padding: 0.8em 1em; border-radius: 5px;
    overflow-x: auto; page-break-inside: avoid;
  }
  pre code { background: none; padding: 0; }
"""


def resolve_browsers(preferred: str | None) -> list[tuple[str, str]]:
    """
    Find usable Chromium-family browser executables, in preference order.

    Parameters:
        preferred: An explicit browser command or path to use instead of the
                   built-in search. May be a bare command on PATH or a full path.

    Returns a list of (display name, executable path) for every browser found.
    Rendering tries them in order, so a browser that launches but fails to
    produce a PDF falls through to the next.
    """
    if preferred:
        found = shutil.which(preferred) or (preferred if Path(preferred).is_file() else None)
        if not found:
            typer.echo(f"Requested browser not found: {preferred}", err=True)
            raise typer.Exit(1)
        return [(Path(found).name, found)]

    resolved: list[tuple[str, str]] = []
    for name, candidates in BROWSER_CANDIDATES:
        for candidate in candidates:
            found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
            if found:
                resolved.append((name, found))
                break

    if not resolved:
        tried = ", ".join(name for name, _ in BROWSER_CANDIDATES)
        typer.echo(f"No Chromium-family browser found. Tried: {tried}.", err=True)
        typer.echo("Install one, or pass --browser with a path.", err=True)
        raise typer.Exit(1)

    return resolved


def build_html(md_path: Path) -> str:
    """
    Convert a markdown file to a standalone, print-styled HTML document.

    Parameters:
        md_path: Path to the markdown source file.
    """
    body = md.markdown(
        md_path.read_text(),
        extensions=["extra", "sane_lists", "smarty"],
    )
    title = md_path.stem
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        f"<meta charset=\"utf-8\">\n<title>{title}</title>\n"
        f"<style>{PRINT_CSS}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def render_pdf(browser: str, html: str, out_path: Path, timeout: int) -> bool:
    """
    Print an HTML string to PDF with a headless browser.

    Parameters:
        browser: Path to the Chromium-family executable.
        html:    The HTML document to render.
        out_path: Where to write the resulting PDF.
        timeout: Seconds to wait before giving up on the render.

    Returns True if a non-empty PDF was written, False otherwise.
    """
    if out_path.exists():
        out_path.unlink()

    with tempfile.TemporaryDirectory(prefix="md-to-pdf-") as workdir:
        html_path = Path(workdir) / "doc.html"
        html_path.write_text(html)
        profile = Path(workdir) / "profile"

        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-pdf-header-footer",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={out_path}",
            html_path.as_uri(),
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            # Headless Chromium often lingers after writing the PDF, so polling
            # for the finished file lets the success path return immediately
            # instead of waiting out the full timeout. The timeout is the hard
            # ceiling for browsers that hang without ever producing output.
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    break
                if out_path.is_file() and out_path.stat().st_size > 0:
                    # Give the write a beat to flush fully, then stop the browser.
                    time.sleep(0.3)
                    break
                time.sleep(0.2)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    return out_path.is_file() and out_path.stat().st_size > 0


@app.command()
def main(
    files: list[Path] = typer.Argument(..., help="Markdown files to render"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output PDF path (only valid with a single input file)"
    ),
    browser: str | None = typer.Option(
        None, "--browser", "-b", help="Browser command or path to use (skips auto-detection)"
    ),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Per-file render timeout in seconds"),
) -> None:
    """Render one or more markdown files to PDF.

    Each input is converted to a styled HTML document and printed to PDF by a
    headless Chromium browser. By default the output PDF is written next to the
    source file with a .pdf extension.

    Browser auto-detection prefers chrome-headless-shell, then falls back to
    Chrome, Chromium, Brave, and Edge. Override the choice with --browser. The
    selected browser runs against a throwaway profile, so your real browser
    session is never touched.
    """
    if output is not None and len(files) != 1:
        typer.echo("--output can only be used with exactly one input file", err=True)
        raise typer.Exit(1)

    for src in files:
        if not src.is_file():
            typer.echo(f"Not a file: {src}", err=True)
            raise typer.Exit(1)

    browsers = resolve_browsers(browser)

    # Render the first file by trying each candidate browser in order, keeping
    # the first that actually produces a PDF. A found executable is not proof it
    # works (some full browsers launch but never write output in headless mode).
    working: tuple[str, str] | None = None
    first = files[0]
    first_dest = output if output is not None else first.with_suffix(".pdf")
    for name, path in browsers:
        if render_pdf(path, build_html(first), first_dest, timeout):
            working = (name, path)
            typer.echo(f"using browser: {name} ({path})")
            typer.echo(f"rendered: {first} -> {first_dest}")
            break
        typer.echo(f"{name} produced no output, trying next browser", err=True)

    if working is None:
        tried = ", ".join(name for name, _ in browsers)
        typer.echo(f"No browser produced a PDF. Tried: {tried}.", err=True)
        raise typer.Exit(1)

    # Use the proven browser for the remaining files.
    _, browser_path = working
    for src in files[1:]:
        dest = src.with_suffix(".pdf")
        if render_pdf(browser_path, build_html(src), dest, timeout):
            typer.echo(f"rendered: {src} -> {dest}")
        else:
            typer.echo(f"Failed to render: {src}", err=True)
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
