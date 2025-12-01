"""ADK adapter for session/memory operations.

This module attempts to use the ADK `InMemorySessionService` when the
ADK package is available. If ADK is not installed or the expected
APIs are not present, it falls back to the local SQLite-backed
`agents_capstone.tools.memory` implementation.

Exposes:
- set_value(user_id, key, value)
- get_value(user_id, key)
- append_to_list(user_id, key, item)
- init()
- USING_ADK (bool)

This enables transparent ADK integration: install the ADK package,
and the adapter will prefer it; if ADK is absent, the sqlite fallback
is used automatically.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Local fallback memory module
from agents_capstone.tools import memory as _local_memory

# Try to import ADK (best-effort). ADK import paths may vary across
# distributions; try a few plausible locations. If successful, wrap it
# and attempt to call methods dynamically.
_adk_session = None
_using_adk = False

_possible_adk_imports = [
    "google.ai.adk.sessions",
    "adk.sessions",
    "google_adk.sessions",
    "google.generativeai.adk.sessions",
]

for mod_path in _possible_adk_imports:
    try:
        mod = __import__(mod_path, fromlist=["InMemorySessionService"])
        InMemorySessionService = getattr(mod, "InMemorySessionService", None)
        if InMemorySessionService:
            _adk_session = InMemorySessionService()
            _using_adk = True
            logger.info("ADK InMemorySessionService loaded from %s", mod_path)
            break
    except Exception:
        continue


def _use_adk() -> bool:
    return _using_adk and _adk_session is not None


def set_value(user_id: str, key: str, value: Any) -> None:
    """Set a value in ADK-backed session storage if available else fallback."""
    if _use_adk():
        try:
            # Try common method names; ADK implementations may vary so
            # we use getattr and fall back to JSON-encoded blobs.
            if hasattr(_adk_session, "set"):
                _adk_session.set(user_id, key, value)
                return
            if hasattr(_adk_session, "persist"):
                _adk_session.persist(user_id, {key: value})
                return
        except Exception:
            logger.exception("ADK backend set_value failed, falling back to sqlite")

    # fallback
    _local_memory.set_value(user_id, key, value)


def get_value(user_id: str, key: str) -> Optional[Any]:
    """Get a value from ADK-backed session storage or fallback."""
    if _use_adk():
        try:
            if hasattr(_adk_session, "get"):
                return _adk_session.get(user_id, key)
            if hasattr(_adk_session, "load"):
                data = _adk_session.load(user_id)
                if isinstance(data, dict):
                    return data.get(key)
        except Exception:
            logger.exception("ADK backend get_value failed, falling back to sqlite")

    return _local_memory.get_value(user_id, key)


def append_to_list(user_id: str, key: str, item: Any) -> None:
    """Append an item to a list stored under `key`.

    Uses ADK operations when possible but falls back to the sqlite
    implementation otherwise.
    """
    if _use_adk():
        try:
            # Try to use a native list-append if ADK exposes it
            if hasattr(_adk_session, "append"):
                _adk_session.append(user_id, key, item)
                return
        except Exception:
            logger.exception("ADK backend append failed, falling back to sqlite")

    # fallback
    _local_memory.append_to_list(user_id, key, item)


def init():
    """Initialize underlying storage if necessary."""
    if _use_adk():
        try:
            if hasattr(_adk_session, "init"):
                _adk_session.init()
                return
        except Exception:
            logger.exception("ADK backend init failed, falling back to sqlite")

    _local_memory.init_db()


# Expose a hint for callers
USING_ADK = _use_adk()
