from __future__ import annotations

import atexit
import asyncio
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, cast

from copilot import CopilotClient

# --- TGI resilience config -------------------------------------------------
# The TGI server runs in a Docker container that can be OOM-killed mid-run
# (e.g. the host RAM spike from the parallel coverage step). Since the
# container is no longer started with --rm, a crashed server can be revived
# with `docker start`. These knobs control how aggressively we retry/restart.
_TGI_MAX_ATTEMPTS = int(os.environ.get("ELFUZZ_TGI_MAX_ATTEMPTS", "6"))
_TGI_BACKOFF_BASE = float(os.environ.get("ELFUZZ_TGI_BACKOFF_BASE", "2.0"))
_TGI_BACKOFF_CAP = float(os.environ.get("ELFUZZ_TGI_BACKOFF_CAP", "20.0"))
_TGI_HEALTH_TIMEOUT = float(os.environ.get("ELFUZZ_TGI_HEALTH_TIMEOUT", "180.0"))
_TGI_CONTAINER = os.environ.get("TGI_CONTAINER_NAME") or os.environ.get("DOCKER_NAME") or "tgi-server"
_TGI_AUTORESTART = os.environ.get("ELFUZZ_TGI_AUTORESTART", "1").lower() not in ("0", "false", "no", "")
# Serialize restart attempts: when the server dies, every worker thread sees
# the failure at once; only one should try to bring it back up.
_tgi_restart_lock = threading.Lock()

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

        # Retry transport-level failures (server down / stalled). We deliberately
        # do NOT retry on HTTP error *responses* (e.g. 422 validation): those come
        # back as JSON and the caller already handles them as a failed variant.
        last_exc: Exception | None = None
        for attempt in range(1, _TGI_MAX_ATTEMPTS + 1):
            try:
                return requests.post(f"{self.endpoint}/generate", json=data, timeout=120).json()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exc = e
                if attempt >= _TGI_MAX_ATTEMPTS:
                    break
                # Connection refused => the server process is gone (likely
                # OOM-killed). Try to revive the container before retrying.
                if isinstance(e, requests.exceptions.ConnectionError):
                    self._ensure_server_up()
                delay = min(_TGI_BACKOFF_CAP, _TGI_BACKOFF_BASE * (2 ** (attempt - 1)))
                print(
                    f"WARNING: TGI request to {self.endpoint} failed "
                    f"(attempt {attempt}/{_TGI_MAX_ATTEMPTS}, {type(e).__name__}); "
                    f"retrying in {delay:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(delay)
        assert last_exc is not None
        raise last_exc

    def _ensure_server_up(self) -> None:
        """Best-effort revival of a dead TGI container.

        Only one thread restarts at a time; the rest wait on the lock and then
        find the server already healthy. Failures here are non-fatal -- the
        caller will simply keep retrying the request.
        """
        if not _TGI_AUTORESTART:
            return
        import requests

        health_url = f"{self.endpoint}/health"
        with _tgi_restart_lock:
            # Another thread may have already brought it back.
            try:
                if requests.get(health_url, timeout=5).ok:
                    return
            except requests.exceptions.RequestException:
                pass

            print(
                f"WARNING: TGI endpoint {self.endpoint} is down; "
                f"attempting `docker start {_TGI_CONTAINER}`",
                file=sys.stderr,
                flush=True,
            )
            docker = ["docker"] if os.geteuid() == 0 else ["sudo", "docker"]
            try:
                subprocess.run(
                    docker + ["start", _TGI_CONTAINER],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=60,
                )
            except Exception as e:  # docker missing, perms, timeout, ...
                print(f"WARNING: could not restart TGI container: {e}", file=sys.stderr, flush=True)
                return

            # Wait for the model to reload and the server to report healthy.
            deadline = time.monotonic() + _TGI_HEALTH_TIMEOUT
            while time.monotonic() < deadline:
                try:
                    if requests.get(health_url, timeout=5).ok:
                        print(f"INFO: TGI endpoint {self.endpoint} is back up", file=sys.stderr, flush=True)
                        return
                except requests.exceptions.RequestException:
                    pass
                time.sleep(3)
            print(
                f"WARNING: TGI endpoint {self.endpoint} did not become healthy "
                f"within {_TGI_HEALTH_TIMEOUT:.0f}s of restart",
                file=sys.stderr,
                flush=True,
            )


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
) -> LLMProvider:
    if backend == "copilot":
        return GitHubCopilotProvider(model_id=model_id, github_token=github_token)
    if endpoint is None:
        raise ValueError("Hugging Face backend requires an endpoint")
    return HuggingFaceTGIProvider(endpoint=endpoint, model_id=model_id)
