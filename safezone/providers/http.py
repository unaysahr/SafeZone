"""Small HTTP helper shared by providers.

Uses urllib so the app has no hard third-party HTTP dependency. Providers get
a bounded timeout and a descriptive User-Agent - several state registries
reject unidentified clients.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from .base import ProviderError

logger = logging.getLogger(__name__)

USER_AGENT = "SafeZone/1.0 (community safety lookup; +https://github.com/unaysahr/safezone)"


def get_json(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 10.0,
) -> dict:
    """GET a URL and parse JSON, or raise ProviderError.

    Every failure mode - network, HTTP status, malformed body - becomes a
    ProviderError so callers can degrade to the official-registry handoff
    instead of showing the user something invented.
    """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"HTTP {exc.code} from {urllib.parse.urlsplit(url).netloc}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Network error contacting {urllib.parse.urlsplit(url).netloc}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ProviderError("Registry request timed out") from exc

    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ProviderError("Registry returned a malformed response") from exc
