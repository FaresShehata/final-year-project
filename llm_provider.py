from __future__ import annotations

import atexit
import asyncio
import os
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, cast

from copilot import CopilotClient

HUGGINGFACE_TOKEN_PATH = Path.home() / ".config" / "huggingface" / "token"
COPILOT_TOKEN_PATH = Path.home() / ".config" / "github-copilot" / "token"
FALLBACK_COPILOT_TOKEN_PATHS = [
    COPILOT_TOKEN_PATH,
    Path("/home/appuser/.config/github-copilot/token"),
    Path("/root/.config/github-copilot/token"),
]


class LLMProvider(Protocol):
    model_id: str

    def model_info(self) -> dict[str, str]:
        raise NotImplementedError

    def build_prompt(self, generator: str, prefix: str, suffix: str) -> str:
        raise NotImplementedError

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1200,
        repetition_penalty: float = 1.1,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


def _trim_stop_sequences(text: str, stop: list[str] | None) -> tuple[str, str]:
    if not stop:
        return text, "eos_token"
    for stop_seq in stop:
        if stop_seq and stop_seq in text:
            return text.split(stop_seq, 1)[0], "stop_sequence"
    return text, "eos_token"


@dataclass
class HuggingFaceTGIProvider:
    endpoint: str
    model_id: str
    request_timeout_s: float = 120.0

    def model_info(self) -> dict[str, str]:
        return {"model_id": self.model_id}

    def build_prompt(self, generator: str, prefix: str, suffix: str) -> str:
        if generator == "complete":
            return prefix
        if "starcoder" in self.model_id:
            return f"<fim_prefix>{prefix}<fim_suffix>{suffix}<fim_middle>"
        if self.model_id.startswith("Qwen/Qwen2.5-Coder"):
            return f"<|fim_prefix|>{prefix}<|fim_suffix|>{suffix}<|fim_middle|>"
        return f"<PRE> {prefix} <SUF>{suffix} <MID>"

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1200,
        repetition_penalty: float = 1.1,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        import requests

        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_new_tokens,
                "do_sample": True,
                "repetition_penalty": repetition_penalty,
                "details": True,
            },
        }
        if stop is not None:
            data["parameters"]["stop"] = stop
        try:
            return requests.post(
                f"{self.endpoint}/generate",
                json=data,
                timeout=self.request_timeout_s,
            ).json()
        except requests.Timeout:
            return {
                "error": "timeout",
                "timeout_seconds": self.request_timeout_s,
                "details": {"finish_reason": "timeout"},
            }


@dataclass
class GitHubCopilotProvider:
    model_id: str
    github_token: str | None = None
    _runtime_lock: threading.Lock = field(init=False, repr=False)
    _request_lock: threading.Lock = field(init=False, repr=False)
    _loop: asyncio.AbstractEventLoop | None = field(init=False, default=None, repr=False)
    _loop_thread: threading.Thread | None = field(init=False, default=None, repr=False)
    _client: CopilotClient | None = field(init=False, default=None, repr=False)
    _session: Any | None = field(init=False, default=None, repr=False)
    _fatal_error: str | None = field(init=False, default=None, repr=False)
    _closed: bool = field(init=False, default=False, repr=False)

    def __post_init__(self) -> None:
        if self.github_token is None:
            self.github_token = self._load_token()
        self._runtime_lock = threading.Lock()
        self._request_lock = threading.Lock()
        atexit.register(self.close)

    def _load_token(self) -> str:
        env_token = os.environ.get("GITHUB_COPILOT_TOKEN")
        if env_token:
            return env_token.strip()
        for token_path in FALLBACK_COPILOT_TOKEN_PATHS:
            if token_path.exists():
                token = token_path.read_text().strip()
                if token:
                    return token
        raise RuntimeError(
            "GitHub Copilot token not configured. Set it with `elfuzz config --set copilot.github_token ...`."
        )

    def model_info(self) -> dict[str, str]:
        return {"model_id": self.model_id}

    def build_prompt(self, generator: str, prefix: str, suffix: str) -> str:
        if generator == "complete":
            return "Continue the following code. Return only code, with no markdown or explanation.\n\n" f"{prefix}"
        return (
            "Fill in the missing code between the prefix and suffix. Return only the code, with no markdown or explanation.\n\n"
            f"PREFIX:\n{prefix}\n\nSUFFIX:\n{suffix}\n\nMISSING CODE:"
        )

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1200,
        repetition_penalty: float = 1.1,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        del temperature, repetition_penalty
        if self._fatal_error is not None:
            raise RuntimeError(self._fatal_error)
        with self._request_lock:
            self._ensure_session_ready()
            assert self._loop is not None
            future = asyncio.run_coroutine_threadsafe(
                self._generate_async(prompt, max_new_tokens=max_new_tokens, stop=stop),
                self._loop,
            )
            return future.result()

    def _ensure_session_ready(self) -> None:
        with self._runtime_lock:
            if self._closed:
                raise RuntimeError("GitHub Copilot provider has been closed")
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
                self._loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
                self._loop_thread.start()

        assert self._loop is not None
        if self._session is None:
            future = asyncio.run_coroutine_threadsafe(self._start_client_and_session(), self._loop)
            future.result()

    def _run_event_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _start_client_and_session(self) -> None:
        if self._client is None:
            token = self.github_token
            if token is None:
                raise RuntimeError("GitHub Copilot token not configured")
            self._client = CopilotClient(cast(Any, {"github_token": token}))
            try:
                await self._client.start()
            except Exception as e:
                self._client = None
                raise RuntimeError(f"Failed to start GitHub Copilot CLI subprocess: {e}") from e
        if self._session is None:
            try:
                self._session = await self._client.create_session({"model": self.model_id})
            except Exception as e:
                # Some Copilot environments reject explicit model names (e.g. gpt-5).
                # Fall back to provider-selected default model instead of hard failing.
                if self._is_unsupported_model_error(e):
                    print(
                        f"WARNING: Copilot model {self.model_id!r} is unsupported; falling back to default model",
                        file=sys.stderr,
                    )
                    self._session = await self._client.create_session({})
                else:
                    raise

    async def _generate_async(
        self,
        prompt: str,
        max_new_tokens: int = 1200,
        stop: list[str] | None = None,
    ) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("GitHub Copilot session is not initialized")
        try:
            response = await self._session.send_and_wait({"prompt": prompt}, timeout=120.0)
        except Exception as e:
            if self._is_unsupported_model_error(e):
                self._fatal_error = (
                    "Copilot rejected the requested model. Set ELMFUZZ_COPILOT_MODEL to a supported model "
                    "or leave it unset to use Copilot default."
                )
                raise RuntimeError(self._fatal_error) from e
            raise
        if response is None:
            messages = await self._session.get_messages()
            response = next(
                (
                    event
                    for event in reversed(messages)
                    if getattr(event.type, "value", event.type) == "assistant.message"
                ),
                None,
            )
        generated_text = ""
        if response is not None and getattr(response, "data", None) is not None:
            generated_text = getattr(response.data, "content", "") or ""
        generated_text, finish_reason = _trim_stop_sequences(generated_text, stop)
        if max_new_tokens <= 0:
            finish_reason = "length"
        return {
            "generated_text": generated_text,
            "details": {"finish_reason": finish_reason},
        }

    @staticmethod
    def _is_unsupported_model_error(error: Exception) -> bool:
        msg = str(error).lower()
        return "model is not supported" in msg or "requested model is not supported" in msg

    def close(self) -> None:
        with self._runtime_lock:
            if self._closed:
                return
            self._closed = True
            loop = self._loop
            loop_thread = self._loop_thread

        if loop is None:
            return

        if self._client is not None:
            future = asyncio.run_coroutine_threadsafe(self._stop_client(), loop)
            try:
                future.result(timeout=10.0)
            except Exception:
                pass

        loop.call_soon_threadsafe(loop.stop)
        if loop_thread is not None:
            loop_thread.join(timeout=2.0)
        if not loop.is_closed():
            loop.close()

    async def _stop_client(self) -> None:
        if self._client is None:
            return
        try:
            await self._client.stop()
        finally:
            self._session = None
            self._client = None


def create_provider(
    backend: str,
    *,
    model_id: str,
    endpoint: str | None = None,
    github_token: str | None = None,
    request_timeout_s: float | None = None,
) -> LLMProvider:
    if backend == "copilot":
        return GitHubCopilotProvider(model_id=model_id, github_token=github_token)
    if endpoint is None:
        raise ValueError("Hugging Face backend requires an endpoint")
    if request_timeout_s is None:
        request_timeout_s = float(os.environ.get("ELMFUZZ_HF_TIMEOUT", "120"))
    return HuggingFaceTGIProvider(endpoint=endpoint, model_id=model_id, request_timeout_s=request_timeout_s)
