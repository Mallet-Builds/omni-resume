---
name: omni-resume
description: "Search and reopen prior coding-agent sessions across Antigravity, Hermes, Codex, Claude Code, OpenCode, and related surfaces."
---

# Omni Resume

Use this skill when the user wants to find, inspect, or reopen a prior coding-agent session.

## Operating rules

- Use the `omni-resume` MCP tools first when available.
- Prefer exact session resume commands when the target agent supports them.
- Do not use this skill as a memory layer. Keep durable memory updates in Honcho or the host workspace memory system.
- Keep ingestion responsibilities in the source-specific daemons and watchers. This skill is for retrieval and resume only.

## Recommended flow

1. Search sessions with `search_sessions`.
2. Inspect the most relevant result.
3. Use `resume_command` for an exact reopen command.
4. If the user wants a newer view of the index, call `refresh_index`.

