"""Persistent household memory for HomeCopilot."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "data" / "homecopilot_memory.sqlite3"


def _connect() -> sqlite3.Connection:
  DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
  connection = sqlite3.connect(DATABASE_PATH)
  connection.row_factory = sqlite3.Row
  connection.execute(
      """
      CREATE TABLE IF NOT EXISTS household_memory (
          user_key TEXT PRIMARY KEY,
          profile_json TEXT NOT NULL DEFAULT '{}',
          updated_at TEXT NOT NULL
      )
      """
  )
  connection.execute(
      """
      CREATE TABLE IF NOT EXISTS memory_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_key TEXT NOT NULL,
          event_type TEXT NOT NULL,
          content TEXT NOT NULL,
          created_at TEXT NOT NULL
      )
      """
  )
  connection.commit()
  return connection


def _user_key(identifier: str) -> str:
  return identifier.strip().lower()


def load_memory(identifier: str) -> dict:
  key = _user_key(identifier)
  if not key:
    return {"profile": {}, "events": []}
  with _connect() as connection:
    row = connection.execute(
        "SELECT profile_json FROM household_memory WHERE user_key = ?",
        (key,),
    ).fetchone()
    events = connection.execute(
        """
        SELECT event_type, content, created_at
        FROM memory_events
        WHERE user_key = ?
        ORDER BY id DESC
        LIMIT 8
        """,
        (key,),
    ).fetchall()
  profile = json.loads(row["profile_json"]) if row else {}
  return {
      "profile": profile,
      "events": [dict(event) for event in reversed(events)],
  }


def save_profile(identifier: str, profile: dict) -> None:
  key = _user_key(identifier)
  if not key:
    return
  now = datetime.now(timezone.utc).isoformat()
  with _connect() as connection:
    connection.execute(
        """
        INSERT INTO household_memory (user_key, profile_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_key) DO UPDATE SET
            profile_json = excluded.profile_json,
            updated_at = excluded.updated_at
        """,
        (key, json.dumps(profile, ensure_ascii=False), now),
    )
    connection.commit()


def record_event(identifier: str, event_type: str, content: str) -> None:
  key = _user_key(identifier)
  if not key or not content.strip():
    return
  with _connect() as connection:
    connection.execute(
        """
        INSERT INTO memory_events (user_key, event_type, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            key,
            event_type,
            content.strip(),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()


def format_memory(memory: dict, language: str) -> str:
  profile = memory.get("profile", {})
  events = memory.get("events", [])
  if not profile and not events:
    return (
        "No persistent household memory yet."
        if language == "English"
        else "Aún no existe memoria persistente del hogar."
    )

  lines = []
  if profile.get("schedule"):
    lines.append(f"- Saved schedule:\n{profile['schedule']}")
  if profile.get("modules"):
    lines.append(
        f"- Saved family modules: {json.dumps(profile['modules'], ensure_ascii=False)}"
    )
  if profile.get("origin"):
    lines.append(f"- Saved origin: {profile['origin']}")
  if profile.get("destination"):
    lines.append(f"- Saved destination: {profile['destination']}")
  if events:
    lines.append("- Recent household events:")
    lines.extend(
        f"  - [{event['event_type']}] {event['content']}"
        for event in events
    )
  return "\n".join(lines)
