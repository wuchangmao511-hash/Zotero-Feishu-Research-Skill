#!/usr/bin/env python3
"""Extract page-bounded text or Markdown from a PDF using PyMuPDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz


def parse_page_range(value: str | None, page_count: int) -> tuple[int, int]:
    """Return a zero-based, end-exclusive page range from a 1-based range."""
    if not value:
        return 0, page_count
    parts = value.split("-", 1)
    try:
        start = int(parts[0])
        end = int(parts[1]) if len(parts) == 2 and parts[1] else page_count
    except ValueError as exc:
        raise ValueError("Page range must look like 3 or 3-8") from exc
    if start < 1 or end < start or end > page_count:
        raise ValueError(f"Page range must be within 1-{page_count}")
    return start - 1, end


def extract_pdf(pdf_path: Path, pages: str | None, output_format: str) -> str:
    with fitz.open(pdf_path) as document:
        start, end = parse_page_range(pages, document.page_count)
        chunks: list[str] = []
        for index in range(start, end):
            text = document.load_page(index).get_text("text").rstrip()
            page_number = index + 1
            if output_format == "markdown":
                chunks.append(f"## Page {page_number}\n\n{text}\n")
            else:
                chunks.append(f"===== Page {page_number} =====\n{text}\n")
        separator = "\n" if output_format == "markdown" else "\n\f\n"
        return separator.join(chunks)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", help="1-based page or inclusive range, e.g. 2 or 2-5")
    parser.add_argument("--format", choices=("markdown", "text"), default="markdown")
    parser.add_argument("--output", type=Path, help="UTF-8 output file; defaults to stdout")
    args = parser.parse_args()

    if not args.pdf.is_file():
        parser.error(f"PDF does not exist: {args.pdf}")
    try:
        content = extract_pdf(args.pdf, args.pages, args.format)
    except (fitz.FileDataError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(args.output.resolve())
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
