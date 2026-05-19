from dataclasses import dataclass, field
from datetime import datetime, timezone

import fast_resume.mcp_server as mcp_server
from fast_resume.adapters.base import Session


@dataclass
class FakeStats:
    total_sessions: int = 2
    total_messages: int = 12
    oldest_session: datetime | None = datetime(2026, 5, 1, tzinfo=timezone.utc)
    newest_session: datetime | None = datetime(2026, 5, 19, tzinfo=timezone.utc)
    sessions_by_agent: dict[str, int] = field(default_factory=lambda: {"antigravity": 2})
    avg_messages_per_session: float = 6.0
    index_size_bytes: int = 12345


class FakeSearch:
    def __init__(self) -> None:
        self._session = Session(
            id="session-1",
            agent="antigravity",
            title="Fix resume path",
            directory="/Users/firstlast/Documents/AI Workspace",
            timestamp=datetime(2026, 5, 19, 12, 0, tzinfo=timezone.utc),
            content="Fix resume path",
            message_count=6,
            mtime=0.0,
            yolo=False,
        )
        self._stats = FakeStats()

    def search(self, query: str, agent_filter=None, directory_filter=None, limit=20):
        return [self._session]

    def get_session_by_id(self, session_id: str):
        if session_id == self._session.id:
            return self._session
        return None

    def get_resume_command(self, session: Session, yolo: bool = False):
        return ["gemini", "--resume", session.id]

    def get_stats(self):
        return self._stats

    def get_all_sessions(self, force_refresh: bool = False):
        return [self._session]


def test_search_sessions_serializes_resume_command(monkeypatch):
    monkeypatch.setattr(mcp_server, "SessionSearch", FakeSearch)

    results = mcp_server.search_sessions("resume")

    assert results == [
        {
            "id": "session-1",
            "agent": "antigravity",
            "title": "Fix resume path",
            "directory": "/Users/firstlast/Documents/AI Workspace",
            "timestamp": "2026-05-19T12:00:00+00:00",
            "message_count": 6,
            "yolo": False,
            "resume_command": ["gemini", "--resume", "session-1"],
        }
    ]


def test_resume_command_handles_missing_session(monkeypatch):
    monkeypatch.setattr(mcp_server, "SessionSearch", FakeSearch)

    missing = mcp_server.resume_command("missing")

    assert missing == {
        "found": False,
        "session_id": "missing",
        "resume_command": [],
        "workdir": None,
    }
