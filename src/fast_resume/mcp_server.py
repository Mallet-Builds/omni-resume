"""MCP server for omni-resume."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .search import SessionSearch

mcp = FastMCP("omni-resume", json_response=True)


def _session_payload(search: SessionSearch, session) -> dict[str, Any]:
    """Serialize a session into a stable payload for MCP clients."""
    return {
        "id": session.id,
        "agent": session.agent,
        "title": session.title,
        "directory": session.directory,
        "timestamp": session.timestamp.isoformat(),
        "message_count": session.message_count,
        "yolo": session.yolo,
        "resume_command": search.get_resume_command(session, yolo=session.yolo),
    }


def _stats_payload(search: SessionSearch) -> dict[str, Any]:
    stats = search.get_stats()
    return {
        "total_sessions": stats.total_sessions,
        "total_messages": stats.total_messages,
        "oldest_session": stats.oldest_session.isoformat()
        if stats.oldest_session
        else None,
        "newest_session": stats.newest_session.isoformat()
        if stats.newest_session
        else None,
        "sessions_by_agent": stats.sessions_by_agent,
        "avg_messages_per_session": stats.avg_messages_per_session,
        "index_size_bytes": stats.index_size_bytes,
    }


@mcp.tool()
def search_sessions(
    query: str = "",
    agent: str | None = None,
    directory: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search sessions and return resume-ready metadata."""
    search = SessionSearch()
    sessions = search.search(
        query=query,
        agent_filter=agent,
        directory_filter=directory,
        limit=limit,
    )
    return [_session_payload(search, session) for session in sessions]


@mcp.tool()
def resume_command(session_id: str, yolo: bool = False) -> dict[str, Any]:
    """Return the native resume command for an exact session id."""
    search = SessionSearch()
    session = search.get_session_by_id(session_id)
    if session is None:
        return {
            "found": False,
            "session_id": session_id,
            "resume_command": [],
            "workdir": None,
        }

    return {
        "found": True,
        "session_id": session.id,
        "agent": session.agent,
        "workdir": session.directory,
        "resume_command": search.get_resume_command(session, yolo=yolo),
    }


@mcp.tool()
def index_stats() -> dict[str, Any]:
    """Return current omni-resume index statistics."""
    search = SessionSearch()
    search._load_from_index()  # Read-only browse path
    return _stats_payload(search)


@mcp.tool()
def refresh_index(force: bool = False) -> dict[str, Any]:
    """Refresh the local session index and report summary counts."""
    search = SessionSearch()
    sessions = search.get_all_sessions(force_refresh=force)
    return {
        "refreshed": True,
        "force": force,
        "session_count": len(sessions),
        "stats": _stats_payload(search),
    }


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
