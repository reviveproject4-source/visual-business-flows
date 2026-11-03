#!/usr/bin/env python3
"""Extract, parse, and render every Mermaid fenced block in Markdown files."""
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
MMD = ROOT / "node_modules" / ".bin" / "mmdc"
PUPPETEER_CONFIG = ROOT / ".github" / "puppeteer-config.json"
FENCE = chr(96) * 3

def extract_blocks(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks, active, current, start_line = [], False, [], 0
    for number, line in enumerate(lines, start=1):
        token = line.strip()
        if not active and token.lower() == FENCE + "mermaid":
            active, current, start_line = True, [], number
        elif active and token == FENCE:
            blocks.append((start_line, "\n".join(current) + "\n"))
            active, current = False, []
        elif active:
            current.append(line)
    if active:
        raise ValueError(f"{path.relative_to(ROOT)}:{start_line}: unclosed Mermaid fence")
    return blocks

def main():
    if not MMD.exists():
        print("ERROR: Mermaid CLI is not installed.", file=sys.stderr)
        return 2
    markdown_files = sorted(p for p in ROOT.rglob("*.md")
                            if "node_modules" not in p.parts and ".git" not in p.parts)
    diagrams, failures = [], []
    for path in markdown_files:
        try:
            blocks = extract_blocks(path)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        for index, (line, source) in enumerate(blocks, start=1):
            diagrams.append((path, line, index, source))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    if not diagrams:
        print("ERROR: No Mermaid blocks found.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="vbf-mermaid-") as temp:
        temp_dir = Path(temp)
        combined = temp_dir / "all-diagrams.md"
        rendered = temp_dir / "rendered-diagrams.md"
        parts = []
        for path, line, index, source in diagrams:
            parts.append(f"## {path.relative_to(ROOT)} — diagram {index}, source line {line}\n\n")
            parts.append(FENCE + "mermaid\n" + source + FENCE + "\n\n")
        combined.write_text("".join(parts), encoding="utf-8")
        result = subprocess.run(
            [str(MMD), "--input", str(combined), "--output", str(rendered),
             "--quiet", "--puppeteerConfigFile", str(PUPPETEER_CONFIG)],
            text=True, capture_output=True
        )
        if result.returncode == 0 and rendered.exists():
            for path, line, index, _ in diagrams:
                print(f"PASS {path.relative_to(ROOT)}:{line} diagram {index}")
            print(f"\nValidated and rendered {len(diagrams)} Mermaid diagrams across {len(markdown_files)} Markdown files.")
            return 0

        detail = (result.stderr or result.stdout or "No renderer output").strip()
        print("Combined render failed; isolating diagrams to report exact failures.")
        for number, (path, line, index, source) in enumerate(diagrams, start=1):
            source_file = temp_dir / f"diagram-{number}.mmd"
            output_file = temp_dir / f"diagram-{number}.svg"
            source_file.write_text(source, encoding="utf-8")
            isolated = subprocess.run(
                [str(MMD), "--input", str(source_file), "--output", str(output_file),
                 "--quiet", "--puppeteerConfigFile", str(PUPPETEER_CONFIG)],
                text=True, capture_output=True
            )
            if isolated.returncode != 0 or not output_file.exists():
                message = (isolated.stderr or isolated.stdout or detail).strip()
                failures.append(f"{path.relative_to(ROOT)}:{line} (diagram {index}): {message[-1800:]}")
            else:
                print(f"PASS {path.relative_to(ROOT)}:{line} diagram {index}")
    if failures:
        print("\nMermaid validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("All Mermaid blocks rendered successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
