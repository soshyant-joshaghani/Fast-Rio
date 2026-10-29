"""Minimal HTTP client for kit seed scripts (stdlib only)."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .paths import CTRL_NAME


class ApiError(RuntimeError):
    def __init__(self, method: str, path: str, status: int, body: str) -> None:
        self.method = method
        self.path = path
        self.status = status
        self.body = body
        super().__init__(f"{method} {path} -> {status}: {body[:500]}")


class _PreserveMethodRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        method = req.get_method()
        if code in {301, 302, 303} and method != "GET":
            if method == "POST" and code in {301, 302}:
                return urllib.request.Request(
                    newurl,
                    data=req.data,
                    headers={k: v for k, v in req.headers.items() if k.lower() != "content-length"},
                    method="POST",
                )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_SSL_CTX = ssl.create_default_context()
_OPENER = urllib.request.build_opener(
    _PreserveMethodRedirectHandler(),
    urllib.request.HTTPSHandler(context=_SSL_CTX),
)


def _rewrite_localhost_for_ipv4(base_url: str) -> tuple[str, str | None]:
    parsed = urllib.parse.urlsplit(base_url.rstrip("/"))
    host = (parsed.hostname or "").lower()
    if not host:
        return base_url.rstrip("/"), None
    if host != "localhost" and not host.endswith(".localhost"):
        return base_url.rstrip("/"), None

    port = parsed.port
    netloc = "127.0.0.1" if port is None else f"127.0.0.1:{port}"
    rewritten = urllib.parse.urlunsplit(
        (parsed.scheme or "http", netloc, parsed.path, parsed.query, parsed.fragment)
    ).rstrip("/")
    if port and not (
        (parsed.scheme == "http" and port == 80)
        or (parsed.scheme == "https" and port == 443)
    ):
        host_header = f"{host}:{port}"
    else:
        host_header = host
    return rewritten, host_header


class ApiClient:
    def __init__(self, base_url: str, *, token: str | None = None) -> None:
        connect_url, host_header = _rewrite_localhost_for_ipv4(base_url)
        self.base_url = connect_url
        self._host_header = host_header
        self._display_url = base_url.rstrip("/")
        self.token = token

    def with_token(self, token: str) -> "ApiClient":
        return ApiClient(self._display_url, token=token)

    def _headers(self, *, json_body: bool = False) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": f"{CTRL_NAME}-seed/1.0"}
        if self._host_header:
            headers["Host"] = self._host_header
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _urlopen(self, req: urllib.request.Request, *, timeout: float):
        try:
            return _OPENER.open(req, timeout=timeout)
        except urllib.error.HTTPError:
            raise
        except TimeoutError as exc:
            raise urllib.error.URLError(
                f"timed out after {timeout:.0f}s talking to {self._display_url}"
            ) from exc
        except OSError as exc:
            if "timed out" in str(exc).lower():
                raise urllib.error.URLError(
                    f"timed out after {timeout:.0f}s talking to {self._display_url}"
                ) from exc
            raise
        except urllib.error.URLError as exc:
            hint = ""
            if self._host_header or "localhost" in self._display_url.lower():
                hint = (
                    "\nHint: local API refused the connection. "
                    f"Confirm the kit is up (`{CTRL_NAME}.bat dev run all --slim`), "
                    "then retry with --api http://api.localhost"
                )
            raise urllib.error.URLError(f"{exc.reason}{hint}") from exc

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any | None = None,
        form: dict[str, str] | None = None,
        query: dict[str, Any] | None = None,
        expect: set[int] | None = None,
        timeout: float = 120,
    ) -> Any:
        url = self.base_url + path
        if query:
            qs = urllib.parse.urlencode(
                {k: v for k, v in query.items() if v is not None}, doseq=True
            )
            url = f"{url}?{qs}"

        data: bytes | None = None
        headers = self._headers(json_body=json_body is not None)
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
        elif form is not None:
            data = urllib.parse.urlencode(form).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with self._urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                status = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            status = exc.code
            if expect and status in expect:
                return _parse(raw)
            raise ApiError(method.upper(), path, status, raw) from exc

        if expect and status not in expect:
            raise ApiError(method.upper(), path, status, raw)
        if status >= 400:
            raise ApiError(method.upper(), path, status, raw)
        return _parse(raw)

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Any:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)


def _parse(raw: str) -> Any:
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw
