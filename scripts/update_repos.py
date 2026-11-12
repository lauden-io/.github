"""Rewrite the public repositories table in profile/README.md.

Reads the organisation's public repositories from the GitHub API and
replaces everything between the `repos:start` and `repos:end` markers.
Standard library only. A token in GH_TOKEN is used when present (the
workflow passes its own read-only use of it); without one the public API
works too, within its lower rate limit.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import urllib.error
import urllib.request

ORG = "lauden-io"
API = "https://api.github.com"
README = pathlib.Path(__file__).resolve().parent.parent / "profile" / "README.md"
START, END = "<!-- repos:start -->", "<!-- repos:end -->"
SKIP = {".github"}  # this repository itself


def get(path: str):
    request = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "lauden-io-profile",
    })
    token = os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return None
        raise


def cell(text: str | None) -> str:
    """Safe inside a Markdown table cell: one line, no pipes, no HTML."""
    text = " ".join(str(text or "").split())
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|")


def table() -> str:
    repos = get(f"/orgs/{ORG}/repos?type=public&per_page=100") or []
    repos = [r for r in repos if not r.get("private") and not r.get("fork") and r.get("name") not in SKIP]
    repos.sort(key=lambda r: (r.get("archived", False), -r.get("stargazers_count", 0), r["name"].lower()))
    rows = []
    for r in repos:
        release = get(f"/repos/{ORG}/{r['name']}/releases/latest")
        latest = f"[{cell(release['tag_name'])}]({release['html_url']})" if release else "–"
        licence = ((r.get("license") or {}).get("spdx_id") or "–").replace("NOASSERTION", "other")
        name = f"[**{cell(r['name'])}**]({r['html_url']})" + (" (archived)" if r.get("archived") else "")
        rows.append(f"| {name} | {cell(r.get('description')) or '–'} | {cell(r.get('language')) or '–'} | {latest} | {licence} |")
    head = "| Repository | What it is | Language | Latest release | Licence |\n|---|---|---|---|---|"
    return head + "\n" + ("\n".join(rows) if rows else "| – | Nothing public yet. | | | |")


def main() -> None:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("markers not found in profile/README.md")
    new = pattern.sub(lambda _: f"{START}\n{table()}\n{END}", text)
    if new != text:
        README.write_text(new, encoding="utf-8", newline="\n")
        print("updated")
    else:
        print("unchanged")


if __name__ == "__main__":
    main()
