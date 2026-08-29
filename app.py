"""SafeZone - community safety lookup.

Serves the UI and a single JSON search endpoint backed by real registry
providers. When no provider can authoritatively answer for an area, the
response says so and points at the official registry; it never guesses.
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, render_template, request

from safezone.providers import (
    build_providers,
    lookup_zip,
    nsopw_search_url,
)
from safezone.zip_codes import is_valid_zip, state_for_zip, state_name

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)


def _require_secret() -> str:
    """Session secret from the environment.

    A hardcoded fallback would mean every deployment that forgets to set
    SESSION_SECRET shares a publicly-known key, so outside debug we refuse to
    start instead.
    """
    secret = os.environ.get("SESSION_SECRET")
    if secret:
        return secret
    if os.environ.get("FLASK_DEBUG") == "1":
        logger.warning("SESSION_SECRET unset - using an ephemeral development key.")
        return os.urandom(32).hex()
    raise RuntimeError(
        "SESSION_SECRET is not set. Generate one with "
        "`python -c \"import secrets; print(secrets.token_hex(32))\"` "
        "and set it in your deployment's environment (on Replit: the Secrets pane)."
    )


RATE_LIMIT_REQUESTS = int(os.environ.get("SAFEZONE_RATE_LIMIT", "30"))
RATE_LIMIT_WINDOW = 60.0
_hits: dict[str, deque] = defaultdict(deque)


def _rate_limited(key: str) -> bool:
    now = time.monotonic()
    bucket = _hits[key]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return True
    bucket.append(now)
    if len(_hits) > 10_000:  # bound memory under scan traffic
        for stale in [k for k, v in _hits.items() if not v][:5_000]:
            del _hits[stale]
    return False


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = _require_secret()
    app.config["PROVIDERS"] = build_providers()

    logger.info(
        "Registry providers active: %s",
        ", ".join(p.name for p in app.config["PROVIDERS"]) or "none (official-registry handoff only)",
    )

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/search", methods=["POST"])
    def search_zip():
        if _rate_limited(request.remote_addr or "unknown"):
            return jsonify({"success": False, "error": "Too many searches. Please wait a minute."}), 429

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "error": "Expected a JSON body."}), 400

        zip_code = str(data.get("zip_code", "")).strip()
        if not zip_code:
            return jsonify({"success": False, "error": "ZIP code is required"}), 400
        if not is_valid_zip(zip_code):
            return jsonify({"success": False, "error": "Please enter a valid 5-digit ZIP code"}), 400

        state = state_for_zip(zip_code)

        try:
            result = lookup_zip(zip_code, app.config["PROVIDERS"])
        except Exception:
            logger.exception("Lookup failed for %s", zip_code)
            return jsonify({"success": False, "error": "The registry lookup failed. Please try again."}), 502

        payload = result.to_dict()
        payload["success"] = True
        payload["state_name"] = state_name(state)
        payload["official_search_url"] = nsopw_search_url(state)

        if result.degraded:
            payload["message"] = (
                f"The registry source for {state_name(state) or 'this area'} could not be "
                f"reached just now. Search the official registry directly for current information."
            )
        elif not result.covered:
            payload["message"] = (
                f"SafeZone does not have a verified data source for "
                f"{state_name(state) or 'this area'} yet. Search the official registry "
                f"for accurate, current information."
            )
        elif result.count:
            payload["message"] = (
                f"The official registry lists {result.count} registered "
                f"offender(s) with an address in ZIP code {zip_code}."
            )
        else:
            payload["message"] = (
                f"The official registry lists no registered offenders with an "
                f"address in ZIP code {zip_code}."
            )

        return jsonify(payload)

    @app.route("/health/providers")
    def provider_health():
        """Diagnostic: confirm each provider can actually reach its source.

        Use this after deploying to verify live endpoints, which cannot be
        reached from a sandboxed development environment.
        """
        from safezone.providers.base import ProviderError

        probes = {"Open Data DC (Metropolitan Police Department)": ("20001", "DC")}
        report = []
        for provider in app.config["PROVIDERS"]:
            zip_code, state = probes.get(provider.name, ("20001", "DC"))
            entry = {"provider": provider.name, "probe_zip": zip_code}
            try:
                records = provider.lookup(zip_code, state)
                entry.update(ok=True, records_returned=len(records))
            except ProviderError as exc:
                entry.update(ok=False, error=str(exc))
            except Exception as exc:  # noqa: BLE001 - diagnostic endpoint
                entry.update(ok=False, error=f"{type(exc).__name__}: {exc}")
            report.append(entry)

        healthy = all(e["ok"] for e in report) if report else False
        return jsonify({"providers": report, "healthy": healthy}), (200 if healthy else 503)

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith(("/search", "/health")):
            return jsonify({"success": False, "error": "Not found"}), 404
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"success": False, "error": "Internal server error."}), 500

    return app
