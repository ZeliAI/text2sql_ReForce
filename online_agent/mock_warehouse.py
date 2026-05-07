import csv
from pathlib import Path
from typing import Any

from online_agent.config import domain_config, resolve_path


def mock_warehouse_dir(config: dict[str, Any], domain: str) -> Path:
    domain_info = domain_config(config, domain)
    return resolve_path(domain_info["mock_warehouse_dir"])


def list_mock_tables(config: dict[str, Any], domain: str) -> list[Path]:
    root = mock_warehouse_dir(config, domain)
    if not root.exists():
        return []
    return sorted(root.glob("*.csv"))


def load_mock_preview(config: dict[str, Any], domain: str, max_rows: int = 5) -> dict[str, list[dict[str, Any]]]:
    previews: dict[str, list[dict[str, Any]]] = {}
    for csv_path in list_mock_tables(config, domain):
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            previews[csv_path.stem] = [row for _, row in zip(range(max_rows), reader)]
    return previews
