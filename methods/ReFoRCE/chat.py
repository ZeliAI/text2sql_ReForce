import sys
import re
import time
import random
import os
import json
from abc import ABC, abstractmethod

try:
    from utils import extract_all_blocks
except ImportError:
    def extract_all_blocks(main_content, code_format):
        code_blocks = []
        start = 0
        while True:
            block_start = main_content.find(f"```{code_format}", start)
            if block_start == -1:
                break
            block_end = main_content.find("```", block_start + len(f"```{code_format}"))
            if block_end == -1:
                break
            code_blocks.append(main_content[block_start + len(f"```{code_format}"):block_end].strip())
            start = block_end + len("```")
        return code_blocks

class BaseChat(ABC):
    def __init__(self, model: str, temperature: float = 1.0):
        self.model = model
        self.temperature = float(temperature)
        self.messages = []
        self.debug_logger = None
        self.test_mode = os.environ.get("LLM_TEST_MODE", "false").strip().lower() in {"1", "true", "yes", "y"}
        self.max_retries = int(os.environ.get("LLM_RETRY_MAX", "8"))
        self.retry_base_seconds = float(os.environ.get("LLM_RETRY_BASE_SECONDS", "2"))
        self.retry_max_seconds = float(os.environ.get("LLM_RETRY_MAX_SECONDS", "30"))
        self.last_request_payload = None
        self.provider = ""

    def set_debug_logger(self, logger):
        self.debug_logger = logger

    def _debug(self, title, content):
        if self.test_mode and self.debug_logger:
            self.debug_logger.info(f"[{title}]\n{content}\n[{title}]")

    @abstractmethod
    def get_response(self, prompt) -> str:
        pass

    def extract_response_blocks(self, response, code_format):
        code_blocks = extract_all_blocks(response, code_format)
        if code_blocks or code_format != "sql":
            return code_blocks
        sql_match = re.search(
            r"(?is)\b(with|select|insert|update|delete|create)\b.*?(?:;|$)",
            response.strip(),
        )
        if sql_match:
            return [sql_match.group(0).strip()]
        return []

    def get_model_response(self, prompt, code_format=None) -> list:
        code_blocks = []
        max_try = 3
        while code_blocks == [] and max_try > 0:
            max_try -= 1
            try:
                response = self.get_response(prompt)
            except Exception as e:
                print(f"max_try: {max_try}, exception: {e}")
                self._debug("LLM exception", str(e))
                if hasattr(self, "is_retryable_exception") and not self.is_retryable_exception(e):
                    max_try = 0
                    break
                continue
            code_blocks = self.extract_response_blocks(response, code_format)
            self._debug(
                "LLM call",
                json.dumps(
                    {
                        "model": self.model,
                        "temperature": self.temperature,
                        "code_format": code_format,
                        "request": self.last_request_payload,
                        "raw_response": response,
                        "cleaned_blocks": code_blocks,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        if max_try == 0 or code_blocks == []:
            print(f"get_model_response() exit, max_try: {max_try}, code_blocks: {code_blocks}")
            sys.exit(0)
        return code_blocks

    def get_model_response_txt(self, prompt) -> str:
        max_try = 3
        while max_try > 0:
            max_try -= 1
            try:
                response = self.get_response(prompt)
                self._debug(
                    "LLM txt call",
                    json.dumps(
                        {
                            "model": self.model,
                            "temperature": self.temperature,
                            "request": self.last_request_payload,
                            "raw_response": response,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
                return response
            except Exception as e:
                print(f"max_try: {max_try}, exception: {e}")
                self._debug("LLM exception", str(e))
                if hasattr(self, "is_retryable_exception") and not self.is_retryable_exception(e):
                    max_try = 0
                    break
                continue
        print(f"get_model_response_txt() exit, max_try: {max_try}")
        sys.exit(0)

    def get_message_len(self):
        return {
            "prompt_len": sum(len(item["content"]) for item in self.messages if item["role"] == "user"),
            "response_len": sum(len(item["content"]) for item in self.messages if item["role"] == "assistant"),
            "num_calls": len(self.messages) // 2
        }

    def init_messages(self):
        self.messages = []


import urllib.request
import urllib.error
from pathlib import Path

try:
    from openai import OpenAI, AzureOpenAI
except ImportError:
    OpenAI = None
    AzureOpenAI = None


def load_env_file():
    for env_path in (Path(__file__).resolve().parent / ".env", Path.cwd() / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


def normalize_response_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") in {"text", "output_text"} and item.get("text"):
                    parts.append(item["text"])
                elif item.get("content"):
                    parts.append(str(item["content"]))
            else:
                text_value = getattr(item, "text", None)
                if text_value:
                    parts.append(text_value)
        return "\n".join(part for part in parts if part)
    return str(content)


def clean_provider_response_text(text, provider):
    text = normalize_response_text(text).strip()
    if provider == "simpleai":
        text = re.sub(r"(?is)^\s*<(?:think|thinking)>.*?</(?:think|thinking)>\s*", "", text).strip()
        text = re.sub(r"(?is)^\s*```(?:markdown|text)?\s*", "", text)
        text = re.sub(r"(?is)\s*```\s*$", "", text).strip()
    return text


class GPTChat(BaseChat):
    def __init__(self, azure=False, model="gpt-4o", temperature=1.0):
        super().__init__(model, temperature)
        self.http_mode = False
        self.base_url = None
        self.api_key = None
        self.timeout = float(os.environ.get("LLM_TIMEOUT", "120"))
        max_tokens = os.environ.get("LLM_MAX_TOKENS")
        self.max_tokens = int(max_tokens) if max_tokens else None
        self.provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
        self.think_or_not = os.environ.get("THINK_OR_NOT", "true").strip().lower() in {"1", "true", "yes", "y"}
        unsupported_thinking_models = {
            item.strip()
            for item in os.environ.get("THINKING_UNSUPPORTED_MODELS", "moonshot-v1-128k").split(",")
            if item.strip()
        }
        self.supports_thinking_param = self.provider == "moonshot" and self.model not in unsupported_thinking_models

        if not azure:
            base_url, api_key = self.resolve_provider()
            if OpenAI is None:
                if not base_url:
                    raise ImportError("Install openai or set OPENAI_BASE_URL/LLM_BASE_URL for the stdlib HTTP client.")
                self.http_mode = True
                self.base_url = base_url.rstrip("/")
                self.api_key = api_key
                return
            if model in ["o1-preview", "o1-mini"]:
                self.client = OpenAI(
                    api_key=api_key,
                    api_version="2024-12-01-preview"
                )
            elif model in ["deepseek-reasoner"]:
                self.client = OpenAI(
                    base_url="https://api.deepseek.com",
                    api_key=os.environ.get("DS_API_KEY"),
                    timeout=self.timeout,
                )
            else:
                kwargs = {"api_key": api_key, "timeout": self.timeout}
                if base_url:
                    kwargs["base_url"] = base_url
                self.client = OpenAI(**kwargs)
        else:
            if AzureOpenAI is None:
                raise ImportError("Azure mode requires the openai package. Install requirements.txt first.")
            if model in ["o1-preview", "o1-mini", "o3", "o4-mini"]:
                version = "2024-12-01-preview"
            elif model in ["o3-pro"]:
                version = "2025-03-01-preview"
            else:
                version = "2024-05-01-preview"

            self.client = AzureOpenAI(
                azure_endpoint=os.environ.get("AZURE_ENDPOINT"),
                api_key=os.environ.get("AZURE_OPENAI_KEY"),
                api_version=version,
                timeout=self.timeout,
            )

    def resolve_provider(self):
        provider = self.provider
        openai_base_url = os.environ.get("OPENAI_BASE_URL")
        llm_base_url = os.environ.get("LLM_BASE_URL")
        base_url = openai_base_url or llm_base_url
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")

        if provider == "moonshot":
            base_url = os.environ.get("MOONSHOT_BASE_URL") or llm_base_url or "https://api.moonshot.ai/v1"
            api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("LLM_API_KEY") or api_key
        elif provider == "openai":
            base_url = openai_base_url or None
            api_key = os.environ.get("OPENAI_API_KEY") or api_key
        elif provider == "simpleai":
            base_url = os.environ.get("SIMPLEAI_BASE_URL") or "https://key.simpleai.com.cn/v1"
            api_key = os.environ.get("SIMPLEAI_API_KEY") or os.environ.get("LLM_API_KEY") or api_key
        elif provider in {"openai_compatible", "local"}:
            base_url = llm_base_url or base_url
            api_key = os.environ.get("LLM_API_KEY") or api_key

        if base_url:
            base_url = base_url.rstrip("/")
        return base_url, api_key

    def is_retryable_exception(self, exc):
        text = str(exc).lower()
        permanent_markers = [
            "insufficient balance",
            "exceeded_current_quota",
            "suspended",
            "billing",
            "invalid api key",
            "unauthorized",
            "permission denied",
            "model not found",
            "invalid temperature",
        ]
        if any(marker in text for marker in permanent_markers):
            return False
        retry_markers = [
            "429",
            "rate limit",
            "rate_limit",
            "max organization concurrency",
            "temporarily unavailable",
            "timeout",
            "timed out",
            "connection reset",
            "service unavailable",
            "502",
            "503",
            "504",
        ]
        return any(marker in text for marker in retry_markers)

    def with_retry(self, fn):
        attempt = 0
        while True:
            try:
                return fn()
            except Exception as exc:
                attempt += 1
                if attempt > self.max_retries or not self.is_retryable_exception(exc):
                    raise
                delay = min(self.retry_max_seconds, self.retry_base_seconds * (2 ** (attempt - 1)))
                delay += random.uniform(0, min(1.0, delay * 0.25))
                self._debug("LLM retry", f"attempt={attempt}, sleep={delay:.2f}s, error={exc}")
                time.sleep(delay)

    def get_http_response(self) -> str:
        payload = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        if not self.think_or_not and self.supports_thinking_param:
            payload["thinking"] = {"type": "disabled"}
        self.last_request_payload = payload
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key or ''}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        return clean_provider_response_text(body["choices"][0]["message"]["content"], self.provider)

    def get_response(self, prompt) -> str:
        self.messages.append({"role": "user", "content": prompt})
        if self.http_mode:
            main_content = self.with_retry(self.get_http_response)
        elif self.model == "o3-pro":
            kwargs = {
                "model": self.model,
                "input": list(self.messages),
                "temperature": self.temperature
            }
            if self.max_tokens:
                kwargs["max_output_tokens"] = self.max_tokens
            self.last_request_payload = kwargs
            response = self.with_retry(lambda: self.client.responses.create(**kwargs))
            main_content = response.output_text
        else:
            kwargs = {
                "model": self.model,
                "messages": list(self.messages),
                "temperature": self.temperature
            }
            if self.max_tokens:
                kwargs["max_tokens"] = self.max_tokens
            if not self.think_or_not and self.supports_thinking_param:
                kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
            self.last_request_payload = kwargs
            response = self.with_retry(lambda: self.client.chat.completions.create(**kwargs))
            main_content = clean_provider_response_text(response.choices[0].message.content, self.provider)

        self.messages.append({"role": "assistant", "content": main_content})
        return main_content
