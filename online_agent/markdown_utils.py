import re
from pathlib import Path
from typing import Any


def clean_cell(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE).strip()


def split_md_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [clean_cell(cell) for cell in cells]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells if cell.strip())


def iter_markdown_tables(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables = []
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            i += 1
            continue

        start = i + 1
        raw_rows = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            raw_rows.append(lines[i])
            i += 1

        parsed_rows = [split_md_row(row) for row in raw_rows]
        parsed_rows = [row for row in parsed_rows if row and not is_separator_row(row)]
        if not parsed_rows:
            continue

        headers, data_rows = parsed_rows[0], parsed_rows[1:]
        tables.append(
            {
                "source_file": path.name,
                "line_start": start,
                "headers": headers,
                "rows": data_rows,
            }
        )
    return tables


def extract_sql_blocks(text: str) -> list[str]:
    return [match.strip() for match in re.findall(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)]


def parse_values_from_description(description: str) -> list[str]:
    values = []
    for pattern in [
        r"'([^']+)'",
        r"（([^）]+)）",
        r"\(([^)]+)\)",
    ]:
        for match in re.findall(pattern, description):
            if ":" in match or "：" in match or "、" in match or "," in match:
                values.append(match.strip())
            elif pattern.startswith("'"):
                values.append(match.strip())
    seen = set()
    deduped = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
