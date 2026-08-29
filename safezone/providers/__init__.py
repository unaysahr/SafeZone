"""Provider registry and lookup orchestration."""

from __future__ import annotations

import logging
import os

from .base import (
    LookupResult,
    OffenderRecord,
    ProviderError,
    RegistryProvider,
    nsopw_search_url,
)
from .dc import DCProvider
from .national import NationalAPIProvider
from ..zip_codes import is_valid_zip, state_for_zip

logger = logging.getLogger(__name__)

__all__ = [
    "LookupResult",
    "OffenderRecord",
    "ProviderError",
    "RegistryProvider",
    "build_providers",
    "lookup_zip",
    "nsopw_search_url",
]


def build_providers(env: dict | None = None) -> list[RegistryProvider]:
    """Assemble the active provider chain from environment configuration.

    Free official sources come first; the optional commercial aggregator is
    the catch-all. If nothing is configured the chain may be empty, which is
    a supported state - the app then always hands off to the official search.
    """
    env = os.environ if env is None else env
    providers: list[RegistryProvider] = []

    if env.get("SAFEZONE_ENABLE_DC", "1") not in ("0", "false", "False"):
        layer = env.get("SAFEZONE_DC_LAYER_URL")
        providers.append(DCProvider(layer) if layer else DCProvider())

    api_url = env.get("SAFEZONE_NATIONAL_API_URL")
    api_key = env.get("SAFEZONE_NATIONAL_API_KEY")
    if api_url and api_key:
        providers.append(
            NationalAPIProvider(
                api_url=api_url,
                api_key=api_key,
                zip_param=env.get("SAFEZONE_NATIONAL_ZIP_PARAM", "zip"),
                auth_header=env.get("SAFEZONE_NATIONAL_AUTH_HEADER", "X-Api-Key"),
                results_key=env.get("SAFEZONE_NATIONAL_RESULTS_KEY", "offenders"),
            )
        )
    elif api_url or api_key:
        logger.warning(
            "National provider ignored: SAFEZONE_NATIONAL_API_URL and "
            "SAFEZONE_NATIONAL_API_KEY must both be set."
        )

    return providers


def lookup_zip(zip_code: str, providers: list[RegistryProvider]) -> LookupResult:
    """Look up a ZIP against the provider chain.

    Returns a result with ``covered=False`` when no provider serves the area
    or when every provider that does errors out. It never invents records:
    an unanswerable query is reported as unanswerable so the caller can send
    the user to the official registry.
    """
    if not is_valid_zip(zip_code):
        raise ValueError("zip_code must be 5 digits")

    state = state_for_zip(zip_code)
    attempted = False

    for provider in providers:
        if not provider.covers(zip_code, state):
            continue
        attempted = True
        try:
            records = provider.lookup(zip_code, state)
        except ProviderError as exc:
            logger.warning("Provider %s failed for %s: %s", provider.name, zip_code, exc)
            continue
        except Exception:
            logger.exception("Provider %s raised unexpectedly for %s", provider.name, zip_code)
            continue

        return LookupResult(
            zip_code=zip_code,
            covered=True,
            records=records,
            source=provider.name,
            source_url=provider.source_url,
            attribution=provider.attribution,
            state=state,
        )

    # attempted means a provider serves this area but every attempt failed,
    # which is an outage - materially different from having no source at all.
    return LookupResult(
        zip_code=zip_code, covered=False, state=state, degraded=attempted
    )
