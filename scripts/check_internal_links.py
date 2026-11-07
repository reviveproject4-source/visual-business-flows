#!/usr/bin/env python3
"""Check relative Markdown links resolve to files or directories in this repository."""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
markdown_files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
repo_paths = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}

link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
errors = []

for source in markdown_files:
    text = source.read_text(encoding="utf-8")
    # Ignore links inside fenced code examples.
    text = re.sub(r"(?ms)^\s*(\`{3,}|~{3,}).*?^\s*\1\s*$", "", text)
    for match in link_pattern.finditer(text):
        raw = match.group(1).strip()
        destination = raw.split()[0] if raw else ""
        if destination.startswith("<") and destination.endswith(">"):
            destination = destination[1:-1]
        if not destination:
            continue

        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or destination.startswith("#"):
            continue

        target = unquote(parsed.path)
        if not target:
            continue

        if target.startswith("/"):
            candidate = PurePosixPath(target.lstrip("/"))
        else:
            candidate = PurePosixPath(source.relative_to(ROOT).parent, target)
        parts = []
        for part in candidate.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        normalized = "/".join(parts)

        exists = normalized in repo_paths or any(p.startswith(normalized.rstrip("/") + "/") for p in repo_paths)
        if not exists:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{source.relative_to(ROOT)}:{line}: missing local target '{destination}'")

if errors:
    print("\n".join(errors))
    print(f"\nFound {len(errors)} broken local Markdown link(s).")
    sys.exit(1)

print(f"Checked relative Markdown links in {len(markdown_files)} files; no broken targets found.")
