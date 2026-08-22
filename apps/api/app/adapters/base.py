"""Shared HTTP plumbing for ATS adapters: timeout, retries, HTML->text, hashing."""

from __future__ import annotations

import hashlib
import html
import re
import time
from collections.abc import Callable
from typing import Any

import httpx

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RETRIES = 3
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t]*\n[ \t\n]*")


class HttpFetcher:
    """GET-with-retry wrapper around an injectable httpx.Client."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff: Callable[[int], float | None] | None = None,
    ) -> None:
        self._client = client or httpx.Client(timeout=timeout)
        self.timeout_seconds = timeout
        self.max_retries = max_retries
        self.backoff = backoff or (lambda attempt: min(2**attempt * 0.25, 4.0))

    def get_json(self, url: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            response = self._client.get(url)
            if response.status_code in _RETRYABLE_STATUS:
                last_error = httpx.HTTPStatusError(
                    f"retryable status {response.status_code} from {url}",
                    request=response.request,
                    response=response,
                )
                sleep_for = self.backoff(attempt)
                if sleep_for:
                    time.sleep(sleep_for)
                continue
            if response.is_error:
                response.raise_for_status()
            return response.json()
        assert last_error is not None
        raise last_error


def html_content_to_text(raw: str) -> str:
    """Greenhouse 'content' is HTML-escaped markup; produce clean plain text."""
    unescaped = html.unescape(raw)
    without_tags = _TAG_RE.sub("\n", unescaped)
    collapsed = _WS_RE.sub("\n", without_tags)
    return collapsed.strip()


def normalized_text_hash(text: str) -> str:
    """Deterministic SHA-256 over whitespace-normalized description text."""
    canonical = " ".join(text.split())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
