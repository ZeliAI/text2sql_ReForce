import sys
import re
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
                continue
            code_blocks = self.extract_response_blocks(response, code_format)
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
                return response
            except Exception as e:
                print(f"max_try: {max_try}, exception: {e}")
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


import os
import json
import urllib.request
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

class GPTChat(BaseChat):
    def __init__(self, azure=False, model="gpt-4o", temperature=1.0):
        super().__init__(model, temperature)
        self.http_mode = False
        self.base_url = None
        self.api_key = None
        self.timeout = float(os.environ.get("LLM_TIMEOUT", "120"))
        max_tokens = os.environ.get("LLM_MAX_TOKENS")
        self.max_tokens = int(max_tokens) if max_tokens else None
        self.think_or_not = os.environ.get("THINK_OR_NOT", "true").strip().lower() in {"1", "true", "yes", "y"}
        self.supports_thinking_param = self.model not in {"moonshot-v1-128k"}

        if not azure:
            base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("LLM_BASE_URL")
            api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
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
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]

    def get_response(self, prompt) -> str:
        self.messages.append({"role": "user", "content": prompt})
        if self.http_mode:
            main_content = self.get_http_response()
        elif self.model == "o3-pro":
            kwargs = {
                "model": self.model,
                "input": self.messages,
                "temperature": self.temperature
            }
            if self.max_tokens:
                kwargs["max_output_tokens"] = self.max_tokens
            response = self.client.responses.create(**kwargs)
            main_content = response.output_text
        else:
            kwargs = {
                "model": self.model,
                "messages": self.messages,
                "temperature": self.temperature
            }
            if self.max_tokens:
                kwargs["max_tokens"] = self.max_tokens
            if not self.think_or_not and self.supports_thinking_param:
                kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
            response = self.client.chat.completions.create(**kwargs)
            main_content = response.choices[0].message.content

        self.messages.append({"role": "assistant", "content": main_content})
        return main_content
