"""
data_store.py

Lightweight local persistence for the app, using plain JSON files on disk.
No database and no user accounts are required. This gives two things:

1. Session save / resume: every conversation is auto-saved under a short
   session code. If the browser is closed or refreshed, the customer can
   type their code back in to pick up exactly where they left off.
2. Report history: every finished report is appended to a running log per
   assistant type, so past reports can be revisited later in the same
   install.

Everything lives under a local "data" folder next to this file. This is
fine for a single person or small team running the app themselves. It is
not meant to scale to many simultaneous strangers sharing one deployment,
since session codes are the only thing standing in for a real login.
"""

import json
import random
import string
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
HISTORY_FILE = DATA_DIR / "history.json"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def generate_session_code() -> str:
    """A short, easy to read/type code like 'AVA-7K3F'."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=4))
    return f"AVA-{suffix}"


def _session_path(code: str) -> Path:
    safe_code = "".join(ch for ch in code.strip().upper() if ch.isalnum() or ch == "-")
    return SESSIONS_DIR / f"{safe_code}.json"


def save_session(code: str, assistant_key: str, messages: list[dict], report: str | None) -> None:
    """Write (or overwrite) the current conversation state for this code."""
    payload = {
        "assistant_key": assistant_key,
        "messages": messages,
        "report": report,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        _session_path(code).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        # Persistence is a convenience feature; never let a disk error
        # break the live conversation.
        pass


def load_session(code: str) -> dict | None:
    """Return the saved state for a code, or None if it doesn't exist."""
    path = _session_path(code)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def append_history(assistant_key: str, title: str, report_text: str) -> None:
    """Add a finished report to the running history log."""
    history = _read_history()
    history.append({
        "assistant_key": assistant_key,
        "title": title,
        "report_text": report_text,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    })
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except OSError:
        pass


def load_history(assistant_key: str | None = None) -> list[dict]:
    """Return past reports, most recent first, optionally filtered by type."""
    history = _read_history()
    if assistant_key:
        history = [h for h in history if h.get("assistant_key") == assistant_key]
    return list(reversed(history))


def _read_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
