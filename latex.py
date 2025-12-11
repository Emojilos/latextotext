#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
import webbrowser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backend: inject LaTeX into frontend template."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=pathlib.Path,
        help="Path to a .tex file to load into the page.",
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Raw LaTeX string to preload. If omitted, stdin is used.",
    )
    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="Open the generated page in the default browser.",
    )
    return parser.parse_args()


def load_latex(args: argparse.Namespace) -> str:
    if args.file:
        if not args.file.is_file():
            raise FileNotFoundError(f"No such file: {args.file}")
        return args.file.read_text(encoding="utf-8")

    if args.text:
        return args.text

    data = sys.stdin.read()
    if not data.strip():
        return ""
    return data


def normalize_latex(source: str) -> str:
    stripped = source.strip()
    if not stripped:
        return ""
    if any(marker in stripped for marker in ("\\(", "\\)", "$$", "\\[", "\\]")):
        return stripped
    return f"$$\n{stripped}\n$$"


def default_sample() -> str:
    return (
        "E = mc^2\n"
        "\\int_0^{\\infty} e^{-x^2}\\,dx = \\frac{\\sqrt{\\pi}}{2}\n"
        "\\textbf{Матрица: }\\begin{bmatrix}1 & 0 \\ 0 & 1\\end{bmatrix}"
    )


def build_page(latex: str, template_path: pathlib.Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return (
        template.replace("__PRELOAD__", json.dumps(latex))
        .replace("__SAMPLE__", json.dumps(default_sample()))
    )


def write_and_open(html: str, should_open: bool) -> pathlib.Path:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    path = pathlib.Path(temp_file.name)
    path.write_text(html, encoding="utf-8")
    if should_open:
        webbrowser.open(path.as_uri())
    return path


def main() -> None:
    args = parse_args()
    try:
        raw_latex = load_latex(args)
        normalized = normalize_latex(raw_latex)
        template_path = pathlib.Path(__file__).with_name("index.html")
        if not template_path.is_file():
            raise FileNotFoundError(f"Template not found: {template_path}")
        html = build_page(normalized, template_path)
        path = write_and_open(html, args.open)
        print(f"Preview written to {path}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
