#!/usr/bin/env python3
"""Read-only client for Zotero Desktop's Local API.

This module intentionally uses only Python's standard library and only issues
HTTP GET requests to the local Zotero API.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://localhost:23119/api/"
USER_ROOT = "users/0/"
NON_BIBLIOGRAPHIC_TYPES = {"annotation", "attachment", "note"}


class ZoteroError(RuntimeError):
    """A readable Zotero Local API error."""


class ZoteroLocal:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def get(self, path: str = "", params: dict[str, Any] | None = None) -> Any:
        url = self.base_url + path.lstrip("/")
        if params:
            clean = {key: value for key, value in params.items() if value is not None}
            if clean:
                url += "?" + urlencode(clean, doseq=True)
        request = Request(
            url,
            method="GET",
            headers={"Accept": "application/json", "Zotero-API-Version": "3"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
                content_type = response.headers.get_content_type()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ZoteroError(f"HTTP {exc.code} for {url}: {detail}") from exc
        except URLError as exc:
            raise ZoteroError(f"Cannot reach Zotero Local API at {url}: {exc.reason}") from exc

        text = raw.decode("utf-8", errors="replace")
        if content_type == "application/json" or text[:1] in "[{":
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise ZoteroError(f"Invalid JSON from {url}: {exc}") from exc
        return text

    def health(self) -> dict[str, Any]:
        response = self.get()
        return {"ok": True, "base_url": self.base_url, "response": response}

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        items = self.get(
            USER_ROOT + "items/top",
            {"q": query, "qmode": "everything", "limit": limit, "include": "data"},
        )
        return [item for item in items if item.get("data", {}).get("itemType") not in NON_BIBLIOGRAPHIC_TYPES]

    def item(self, key: str) -> dict[str, Any]:
        return self.get(USER_ROOT + f"items/{key}")

    def children(self, key: str) -> list[dict[str, Any]]:
        return self.get(USER_ROOT + f"items/{key}/children", {"include": "data"})

    def fulltext(self, attachment_key: str) -> dict[str, Any]:
        return self.get(USER_ROOT + f"items/{attachment_key}/fulltext")

    def file(self, attachment_key: str) -> dict[str, Any]:
        result = self.get(USER_ROOT + f"items/{attachment_key}/file/view/url")
        if isinstance(result, str):
            return {"url": result, "path": _path_from_file_url(result)}
        if isinstance(result, dict):
            url = result.get("url") or result.get("fileURL") or result.get("path")
            result.setdefault("path", _path_from_file_url(url) if isinstance(url, str) else None)
            return result
        return {"value": result}

    def collections(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.get(USER_ROOT + "collections", {"limit": limit})


def _path_from_file_url(value: str) -> str | None:
    from urllib.parse import unquote, urlparse

    parsed = urlparse(value)
    if parsed.scheme != "file":
        return value if Path(value).is_absolute() else None
    path = unquote(parsed.path)
    if parsed.netloc:
        path = f"//{parsed.netloc}{path}"
    if len(path) >= 3 and path[0] == "/" and path[2] == ":":
        path = path[1:]
    return str(Path(path))


def _is_pdf_attachment(item: dict[str, Any]) -> bool:
    data = item.get("data", {})
    return (
        data.get("itemType") == "attachment"
        and (
            data.get("contentType") == "application/pdf"
            or str(data.get("filename", "")).lower().endswith(".pdf")
            or str(data.get("title", "")).lower().endswith(".pdf")
        )
    )


def _summary(item: dict[str, Any]) -> dict[str, Any]:
    data = item.get("data", {})
    creators = []
    for creator in data.get("creators", []):
        name = creator.get("name") or " ".join(
            part for part in (creator.get("firstName"), creator.get("lastName")) if part
        )
        if name:
            creators.append(name)
    return {
        "key": item.get("key") or data.get("key"),
        "itemType": data.get("itemType"),
        "title": data.get("title"),
        "creators": creators,
        "date": data.get("date"),
        "DOI": data.get("DOI"),
        "collections": data.get("collections", []),
    }


def _emit(value: Any, pretty: bool = True) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2 if pretty else None)
    sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=10.0)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Check the Zotero Local API")
    search = sub.add_parser("search", help="Search top-level bibliographic items")
    search.add_argument("query", help="Title, author, DOI, or keyword")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--raw", action="store_true")

    for name, help_text in (
        ("item", "Get item metadata"),
        ("children", "Get child notes and attachments"),
        ("fulltext", "Get indexed attachment full text"),
        ("file", "Get an attachment's real file URL/path"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("key")
        if name == "children":
            command.add_argument("--pdf-only", action="store_true")

    collections = sub.add_parser("collections", help="List collection names")
    collections.add_argument("--limit", type=int, default=100)
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    client = ZoteroLocal(args.base_url, args.timeout)
    try:
        if args.command == "health":
            result = client.health()
        elif args.command == "search":
            items = client.search(args.query, args.limit)
            result = items if args.raw else [_summary(item) for item in items]
        elif args.command == "item":
            result = client.item(args.key)
        elif args.command == "children":
            result = client.children(args.key)
            if args.pdf_only:
                result = [item for item in result if _is_pdf_attachment(item)]
        elif args.command == "fulltext":
            result = client.fulltext(args.key)
        elif args.command == "file":
            result = client.file(args.key)
        elif args.command == "collections":
            result = [
                {"key": item.get("key"), "name": item.get("data", {}).get("name")}
                for item in client.collections(args.limit)
            ]
        else:
            raise AssertionError(args.command)
        _emit(result)
        return 0
    except ZoteroError as exc:
        _emit({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
