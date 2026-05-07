from __future__ import annotations

import argparse
import re
from pathlib import Path


SEPARATOR_RE = re.compile(
    r"(?ms)^=+\s*\n<!--\s*FILE_SEPARATOR:\s*(?P<name>[^>]+?)\s*-->\s*\n=+\s*\n?"
)


def sanitize_filename(name: str) -> str:
    name = name.strip().replace("\0", "")
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name or "untitled.md"


def infer_first_name(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return sanitize_filename(title + ".md")
    return "文档一_text2sql线上链路.md"


def write_part(output_dir: Path, filename: str, content: str) -> Path | None:
    content = content.strip()
    if not content:
        return None
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / sanitize_filename(filename)
    output_path.write_text(content + "\n", encoding="utf-8")
    return output_path


def split_markdown(input_path: Path, output_dir: Path) -> list[Path]:
    text = input_path.read_text(encoding="utf-8-sig")
    matches = list(SEPARATOR_RE.finditer(text))
    written: list[Path] = []

    if not matches:
        output_name = infer_first_name(text)
        output_path = write_part(output_dir, output_name, text)
        return [output_path] if output_path else []

    first_content = text[: matches[0].start()]
    first_name = infer_first_name(first_content)
    output_path = write_part(output_dir, first_name, first_content)
    if output_path:
        written.append(output_path)

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        filename = match.group("name").strip()
        output_path = write_part(output_dir, filename, text[start:end])
        if output_path:
            written.append(output_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Split a merged markdown txt file into markdown files.")
    parser.add_argument("--input", default="合并表结构.txt", type=Path)
    parser.add_argument("--output-dir", default="业务评测集_markdown", type=Path)
    args = parser.parse_args()

    written = split_markdown(args.input, args.output_dir)
    for path in written:
        print(path)
    print(f"wrote {len(written)} files to {args.output_dir}")


if __name__ == "__main__":
    main()
