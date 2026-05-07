import os
from contextlib import contextmanager
from typing import Iterator

from chat import GPTChat

from online_agent.config import NodeLLMConfig


@contextmanager
def temporary_env(updates: dict[str, str]) -> Iterator[None]:
    old_values = {key: os.environ.get(key) for key in updates}
    for key, value in updates.items():
        if value:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def llm_for(node_config: NodeLLMConfig) -> GPTChat:
    env_updates = {}
    if node_config.provider:
        env_updates["LLM_PROVIDER"] = node_config.provider
    with temporary_env(env_updates):
        return GPTChat(model=node_config.model, temperature=node_config.temperature)
