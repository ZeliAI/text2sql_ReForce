import json
from typing import Any

from online_agent.config import domain_config, resolve_path


def load_domain_registry(config: dict[str, Any], domain: str) -> dict[str, Any]:
    domain_info = domain_config(config, domain)
    registry_path = domain_info.get("registry_path")
    if not registry_path:
        raise FileNotFoundError(f"Domain {domain} has no registry_path configured.")
    return json.loads(resolve_path(registry_path).read_text(encoding="utf-8"))
