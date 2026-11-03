#!/usr/bin/env python3
"""Extract and render all Mermaid fenced blocks in Markdown files."""
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
MMD = ROOT / "node_modules" / ".bin" / "mmdc"
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
    total, failures = 0, []
    with tempfile.TemporaryDirectory(prefix="vbf-mermaid-") as temp:
        temp_dir = Path(temp)
        for path in markdown_files:
            try:
                blocks = extract_blocks(path)
            except ValueError as exc:
                failures.append(str(exc))
                continue
            for index, (line, source) in enumerate(blocks, start=1):
                total += 1
                source_file = temp_dir / f"diagram-{total}.mmd"
                output_file = temp_dir / f"diagram-{total}.svg"
                source_file.write_text(source, encoding="utf-8")
                result = subprocess.run(
                    [str(MMD), "--input", str(source_file), "--output", str(output_file), "--quiet"],
                    text=True, capture_output=True
                )
                if result.returncode != 0 or not output_file.exists():
                    detail = (result.stderr or result.stdout or "No renderer output").strip()
                    failures.append(f"{path.relative_to(ROOT)}:{line} (diagram {index}): {detail[-1800:]}")
                else:
                    print(f"PASS {path.relative_to(ROOT)}:{line} diagram {index}")
    print(f"\nValidated {total} Mermaid diagrams across {len(markdown_files)} Markdown files.")
    if failures:
        print("\nMermaid validation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("All Mermaid blocks parsed and rendered successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
