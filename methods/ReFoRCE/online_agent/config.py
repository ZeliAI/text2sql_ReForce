import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union


REPO_ROOT = Path(__file__).resolve().parents[3]
METHOD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = METHOD_ROOT / "configs" / "online_agent_v1_2.json"


@dataclass(frozen=True)
class NodeLLMConfig:
    node: str
    provider: str
    model: str
    temperature: float
    num_candidates: int = 1


def resolve_path(value: Union[str, Path], base_dir: Path = REPO_ROOT) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def node_llm_config(config: dict[str, Any], node: str) -> NodeLLMConfig:
    node_config = config.get("llm", {}).get("nodes", {}).get(node, {})
    env_prefix = f"LLM_NODE_{node.upper()}_"
    provider = os.environ.get(env_prefix + "PROVIDER", node_config.get("provider", ""))
    model = os.environ.get(env_prefix + "MODEL", node_config.get("model", os.environ.get("LLM_MODEL", "")))
    temperature = float(os.environ.get(env_prefix + "TEMPERATURE", node_config.get("temperature", 0.6)))
    num_candidates = int(os.environ.get(env_prefix + "NUM_CANDIDATES", node_config.get("num_candidates", 1)))
    return NodeLLMConfig(
        node=node,
        provider=provider,
        model=model,
        temperature=temperature,
        num_candidates=num_candidates,
    )


def domain_config(config: dict[str, Any], domain: str) -> dict[str, Any]:
    domains = config.get("domains", {})
    if domain not in domains:
        raise KeyError(f"Unknown domain: {domain}")
    return domains[domain]
